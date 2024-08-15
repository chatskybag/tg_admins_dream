'''
Эксперимент по обработке FloodWaitError, который возникает при чистке больших чатов
'''
import time
import asyncio
from telethon import events, errors
from telethon.tl.types import PeerChannel, PeerChat, PeerUser
from functions.connection import create_client
from functions.helpers import get_chat_id
from telethon import functions, types
from time import sleep

client = create_client()

white_list = [1230480769, 1584816588, 428033786, 314211715, 137319637, 1158439141, 276585077, 6424014829, 7261927301]


@client.on(events.NewMessage(outgoing=True, pattern='!flood'))
async def handler(event):
    a = 0
    request = "Some request"  # Замените на ваш запрос
    seconds = 10  # Замените на время ожидания
    for idx, user in enumerate(white_list):
        try:
            # await event.respond('!pong')
            if idx == 5:
                raise errors.FloodWaitError(request, seconds)
            print("Число это: ", idx, user)
        except errors.FloodWaitError as e:
            print('Have to sleep', e.seconds, 'seconds')
            time.sleep(e.seconds)
            # просто добавить сюда действия как в блоке try
            print("Число это: ", idx, user)
            continue


with client:
    client.loop.run_until_complete(client.run_until_disconnected())
