import time
from telethon import events, errors
from functions.connection import create_client
from functions.helpers import get_chat_id, printing_status
from telethon import functions

# создаем сессию
client = create_client()
global user_ids, poll_ids, chat_id

# Список id тех, кого ну никак нельзя кикать из группы
white_list = [1230480769, 1584816588, 428033786, 314211715, 137319637, 1158439141, 276585077, 6424014829, 7261927301]

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
@client.on(events.NewMessage(pattern='/help'))
async def start_handler(event):
    await print_to("""
    Привет! Я запустился, я подключился. Порядок такой:
    1. /users
    1. *опционально* /show_users
    2. Пересылаешь опрос, введя текст /reply_poll (кнопка "ответить") 
    3. /kick_by_poll
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
    await print_to(f"Список пользователей чата: \n{user_ids}", to)


@client.on(events.NewMessage(pattern='/reply_poll'))
async def poll_handler(event):
    global chat_id
    # Проверяем, является ли сообщение опросом
    # if hasattr(event.message, 'poll'):

    # Получение предыдущего сообщения
    reply_poll = await event.get_reply_message()

    if reply_poll.poll is not None:
        global poll_ids
        all_users = []
        offset = ''

        # Цикл с перебором offset, пока не получены все голоса
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
            print('Результаты опроса получены, но для детализации списка сначала получи chat_id, используя команду '
                  '/users')
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
            # await client.send_message(chat_id, f"Проверяем, есть ли {user} в списке голосовавших")
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
