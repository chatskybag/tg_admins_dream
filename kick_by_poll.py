import time
from telethon import events, errors
from functions.connection import create_client
from functions.helpers import get_chat_id, printing_status
from telethon import functions

# создаем сессию
client = create_client()

global user_ids, poll_ids, chat_id

# Список id тех, кого ну никак нельзя кикать из группы
white_list = [1230480769, 1584816588, 428033786, 314211715, 137319637, 1158439141, 276585077, 70401481]

# None - отчётность в консоль, Любое значение - отчетность в чат
to = None


# Используем printing_status, но сокращаем, чтобы не писать лишний раз кучу аргументов
async def print_to(msg, to_):
    """
    Упрощенная функция на основе printing_status.
    Вывод детализации в консоль или чат.
    Если аргумент 'to_ is not None', то сообщения пойдут в чат.
    """
    return await printing_status(client, msg, chat_id, to_)


@client.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    await client.get_dialogs(limit=40)
    print("Бот запущен")


@client.on(events.NewMessage(pattern='/help'))
async def help_handler(event):
    global chat_id
    chat_id = get_chat_id(event)[1]
    await print_to("""
    Привет от бота! Порядок такой:
    1. /users - получить пользователей чата
    2. /show_users - вывести список пользователей чата
    3. Пересылаешь опрос, введя текст /reply_poll (кнопка "ответить") 
    4. /kick_by_poll - для запуска процедуры кика 
    """, to)


@client.on(events.NewMessage(pattern='/users'))
async def take_users(event):
    global user_ids, chat_id

    chat_id = get_chat_id(event)[1]
    await print_to("Начинаю собирать id пользователей чата", to)
    await print_to(f"Айди чата: {chat_id}", to)

    # Получаем список пользователей
    participants = await client.get_participants(chat_id, aggressive=True, limit=None)
    user_ids = [participant.id for participant in participants]
    text = ''
    for participant in participants:
        text = text + f"Пользователь: {participant.first_name} {participant.last_name}, telegram id: {participant.id} \n"
    await print_to(text, to)


@client.on(events.NewMessage(pattern='/show_users'))
async def show_users(event):
    global user_ids
    await print_to(f"Количество пользователей чата {len(user_ids)}, список: \n{user_ids}", to)


@client.on(events.NewMessage(pattern='/reply_poll'))
async def poll_handler(event):
    global chat_id

    # Получение reply сообщения
    reply_poll = await event.get_reply_message()

    # Проверка, что получили опрос
    if reply_poll.poll is not None:
        global poll_ids
        all_users = []
        offset = ''

        # Цикл с перебором offset, пока не получены все пользователи
        while offset is not None:
            results = await client(functions.messages.GetPollVotesRequest(
                peer=reply_poll.peer_id,
                id=reply_poll.id,
                offset=offset,
                limit=1000,
            ))

            # Добавляем пользователей в список
            poll_ids = [vote.peer.user_id for vote in results.votes]
            all_users.extend(poll_ids)

            # Берем следующий offset
            offset = results.next_offset

        # Вывод результата
        try:
            await print_to(f"Количество голосовавших {len(all_users)}, участники: \n{all_users}", to)
        except NameError:
            print('Результаты опроса получены, но для детализации списка пользователей сначала получи chat_id, используя'
                  ' команду /users')
        poll_ids = all_users
    else:
        try:
            await print_to('Выбери опрос в качестве пересланного сообщения', to)
        except NameError:
            print('Cначала получи chat_id, используя команду /users')


@client.on(events.NewMessage(pattern='/kick_by_poll'))
async def show_users(event):
    global user_ids, poll_ids, chat_id, white_list

    await print_to(f"Запущена процедура кика пользователей, не участвовавших в опросе", to)

    for idx, user in enumerate(user_ids):
        try:
            await print_to(f"- Проверяем, есть ли {user} в списке голосовавших", to)
            if user not in poll_ids:
                if user in white_list:
                    await print_to(f"Пользователь с id {user} в белом листе, не кикаем", to)
                else:
                    await print_to(f"Пользователя с id {user} не было в списке голосовавших. КИКАЕМ!", to)
                    await client.edit_permissions(chat_id, user, view_messages=False)
            else:
                await print_to(f"Пользователь с id {user} есть в списке проголосовавших", to)

        except errors.FloodWaitError as e:
            await print_to(f'Ожидаю {e.seconds} секунд, чтобы избежать ошибки от телеграма', to)
            time.sleep(e.seconds)

            await print_to(f"- Проверяем, есть ли {user} в списке голосовавших", to)
            if user not in poll_ids:
                if user in white_list:
                    await print_to(f"Пользователь с id {user} в белом листе, не кикаем", to)
                else:
                    await print_to(f"Пользователя с id {user} не было в списке голосовавших. КИКАЕМ!", to)
                    await client.edit_permissions(chat_id, user, view_messages=False)
            continue

    await print_to(f"Процедура кика пользователей завершена успешно", to)


with client:
    client.loop.run_until_complete(client.run_until_disconnected())
