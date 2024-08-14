'''
Вспомогательные многоразовые функции
'''
from telethon.tl.types import PeerChannel, PeerChat, PeerUser


def get_chat_id(event):
    '''
    Функция, возвращающая peer_id и chat_id у поступившего event
    '''
    peer_id = event.message.peer_id
    if isinstance(peer_id, PeerChannel):
        # Канал
        chat_id = peer_id.channel_id
    elif isinstance(peer_id, PeerChat):
        # Чат
        chat_id = peer_id.chat_id
    elif isinstance(peer_id, PeerUser):
        # Пользователь
        chat_id = peer_id.user_id
    else:
        chat_id = None
    return peer_id, chat_id

