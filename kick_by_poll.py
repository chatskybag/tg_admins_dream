import time

from telethon import TelegramClient, events
from telethon.tl.types import PeerChannel, PeerChat, PeerUser
from functions.connection import create_client
from functions.helpers import get_chat_id
from telethon import functions, types
from time import sleep

client = create_client()
global user_ids, poll_ids, chat_id


@client.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    await event.respond("""
    Привет! Я запустился, я подключился. Порядок такой:
    1. /users
    1. *опционально* /show_users
    2. Пересылаешь опрос
    3. /kick_by_poll
    """)


@client.on(events.NewMessage(pattern='/users'))
async def take_users(event):
    global user_ids, chat_id
    # await event.respond("Начинаю собирать id пользователей чата")
    print("Начинаю собирать id пользователей чата")

    # возвращаем только chat_id у функции
    chat_id = get_chat_id(event)[1]

    # await client.send_message(chat_id, f"Всем привет, а наш чат айди: {chat_id}")
    print(f"Айди чата: {chat_id}")

    # Получаем список пользователей
    participants = await client.get_participants(chat_id, aggressive=True, limit=None)

    user_ids = [participant.id for participant in participants]
    # print(user_ids)

    text = ''
    for participant in participants:
        text = text + f"Пользователь: {participant.first_name} {participant.last_name}, telegram id: {participant.id} \n"
    # await client.send_message(chat_id, text)
    print(text)


@client.on(events.NewMessage(pattern='/show_users'))
async def show_users(event):
    global user_ids
    # await event.respond(f"Список пользователей чата {user_ids}")
    print(f"Список пользователей чата {user_ids}")


@client.on(events.NewMessage)
async def poll_handler(event):
    # Проверяем, является ли сообщение опросом
    # if hasattr(event.message, 'poll'):
    if event.message.poll is not None:
        global poll_ids

        # this_chat_id = event.message.peer_id.chat_id

        poll = event.message.poll
        # print(poll)

        # print(f"Название опроса: {poll.question}")
        # Получаем результаты опроса
        results = await client(functions.messages.GetPollVotesRequest(
            peer=event.message.peer_id,
            id=event.message.id,
            limit=1000,
        ))

        # next_offset = results.next_offset
        # print("НЕКСТ ОФСЕТ БЛЯТЬ", next_offset)

        total_votes = results.count
        # Инициализируем offset
        users_get = 0
        offset = results.next_offset
        # Список всех пользователей
        all_users = []
        # Цикл до тех пор, пока не получены все голоса
        while users_get < total_votes:
            # Делаем запрос с offset
            # results = await client(functions.messages.GetPollVotesRequest(peer=event.message.peer_id,
            #                                            id=event.message.id,
            #                                            offset=offset,
            #                                                 limit=1000,))

            results = await client(functions.messages.GetPollVotesRequest(
                peer=event.message.peer_id,
                id=event.message.id,
                offset=offset,
                limit=1000,
            ))

            # Добавляем пользователей в список
            poll_ids = [vote.peer.user_id for vote in results.votes]
            all_users.extend(poll_ids)
            poll_ids = []

            # Увеличиваем offset
            offset = results.next_offset
            users_get += 50

        print(f"Список айдишников из опроса {all_users}")
        poll_ids = all_users


@client.on(events.NewMessage(pattern='/kickbypoll'))
async def show_users(event):
    global user_ids, poll_ids, chat_id

    white_list = [1230480769, 1584816588, 428033786, 314211715, 137319637, 1158439141, 276585077, 6424014829, 7261927301]

    # await event.respond(f"Начинаю кикать тех, кто не отвечал на опрос")
    for user in user_ids:
        time.sleep(0.5)
        # await client.send_message(chat_id, f"Проверяем, есть ли {user} в списке голосовавших")
        print(f"- Проверяем, есть ли {user} в списке голосовавших")
        if user not in poll_ids:
            if user in white_list:
                print(f"Пользователь с id {user} в белом листе, не кикаем")
            else:
                # await client.send_message(chat_id, f"Пользователя с id {user} не было в списке голосовавших. КИКАЕМ!")
                print(f"Пользователя с id {user} не было в списке голосовавших. КИКАЕМ!")
                await client.edit_permissions(chat_id, user, view_messages=False)
        else:
            # await client.send_message(chat_id, f"Пользователь с id {user} есть в списке проголосовавших")
            print(f"Пользователь с id {user} есть в списке проголосовавших")


with client:
    client.loop.run_until_complete(client.run_until_disconnected())
