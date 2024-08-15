'''
Здесь будут эксперименты
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


@client.on(events.NewMessage(outgoing=True, pattern='!hello'))
async def handler(event):
    await client.send_message('me', 'Hello to myself!')


with client:
    client.loop.run_until_complete(client.run_until_disconnected())
