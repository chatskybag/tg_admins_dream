'''
Функции для создания сессии (client) и их помощники
'''
import configparser
from telethon import TelegramClient, events, functions
from pathlib import Path

cfg_name = 'config.ini'


def path_to_config(config_name):
    # Получаем объект Path для текущего каталога
    current_dir = Path(__file__).parent
    # Переходим в родительский каталог (project)
    project_dir = current_dir.parent
    # Создаем относительный путь к файлу в project
    full_file_path = project_dir / config_name
    return full_file_path


def create_client():
    # Создаем объект парсера конфигурационного файла
    config = configparser.ConfigParser()
    # Читаем файл config.ini
    config.read(path_to_config(cfg_name))
    # Получаем конфигурационные значения
    api_id = config.getint('MAIN_SESSION','api_id')
    api_hash = config['MAIN_SESSION']['api_hash']
    try:
        password = config['MAIN_SESSION']['password']
        if len(password)<1:
            password = None
    except KeyError:
        password = None
    client = TelegramClient('main_session', api_id, api_hash, system_version="Telegram Android 10.15.1", device_model="Poco X3", app_version='0.3 beta')
    client.start(password=password)
    return client
