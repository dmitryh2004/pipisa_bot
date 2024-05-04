import json
import logging
import math

from settings import TOKEN, DEBUG_GROUPS as SETTINGS_DEBUG_GROUPS

logging.basicConfig(level=logging.INFO)

BOT_VERSION = "0.9"
BOT_NAME = "pipisa_plus_bot"
DEBUG = True
DEBUG_GROUPS = SETTINGS_DEBUG_GROUPS

DATABASE_LOC = r"./database/database.db"

ITEMS = {}
ITEMS_LOC = {}
ITEMS_MIN_OFFSET = {}
ITEMS_MAX_OFFSET = {}
ITEMS_MIN_VALUE = {}
ITEMS_MAX_VALUE = {}
ITEMS_START_VALUE = {}
ITEMS_SORT_DIRECTION = {}  # True - по убыванию, False - по возрастанию
ITEMS_TIME_INTERVAL = {}

PIE_CHART_COLORS = ['royalblue', 'orangered', 'mediumspringgreen', 'blueviolet', 'orange', 'lightblue', 'lightcoral', 'lightgreen', 'magenta', 'yellow', 'lightgray']

ROLES = {
    0: ("Обычный игрок", "Роль по умолчанию.\nОсобенностей нет."),
    1: ("\U0001F3C5 Тестировщик", "Роль, выдающаяся за участие в тестировании бота.\nОсобенности:\n- доступны промокоды, недоступные остальным игрокам."),
    2: ("\U0001F396 Админ", "Роль, выдаваемая только доверенным лицам и только разработчиком бота.\nОсобенности:\n- доступны промокоды, недоступные остальным игрокам;\n- может создавать новые промокоды;\n- может изменять роли обычных игроков и Тестировщиков.\n\nПодробную информацию можно узнать через команду /admin_features в личных сообщениях."),
    3: ("\U0001F48E\U0001F396 Главный админ", "Роль разработчика бота.\nОсобенности:\n- доступны промокоды, недоступные остальным игрокам;\n- может создавать новые промокоды;\n- может выдавать роли другим игрокам (до Админа включительно).\n\nПодробную информацию можно узнать через команду /developer_features в личных сообщениях.")
}

BAN_REASONS = {
    "0": "Причина не указана",
    "1": "Спам, флуд"
}


def read_config(filepath):
    """
    Чтение config.json и применение характеристик из него.
    :param filepath: путь к config.json
    :return: none
    """
    content = dict()
    with open(filepath, "r", encoding="utf-8") as file:
        content = json.load(file)
    total = 0
    for item in content:
        total += 1
        ITEMS[total] = item
        if "loc" in content[item]:
            ITEMS_LOC[total] = content[item]["loc"]
        else:
            ITEMS_LOC[total] = item
        
        if "min_offset" in content[item]:
            ITEMS_MIN_OFFSET[total] = int(content[item]["min_offset"])
        else:
            ITEMS_MIN_OFFSET[total] = -5
            
        if "max_offset" in content[item]:
            ITEMS_MAX_OFFSET[total] = int(content[item]["max_offset"])
        else:
            ITEMS_MAX_OFFSET[total] = 10

        if "min_value" in content[item]:
            ITEMS_MIN_VALUE[total] = int(content[item]["min_value"])
        else:
            ITEMS_MIN_VALUE[total] = -math.inf

        if "max_value" in content[item]:
            ITEMS_MAX_VALUE[total] = int(content[item]["max_value"])
        else:
            ITEMS_MAX_VALUE[total] = math.inf

        if "start_value" in content[item]:
            ITEMS_START_VALUE[total] = int(content[item]["start_value"])
        else:
            ITEMS_START_VALUE[total] = 0

        if "reverse_sort" in content[item]:
            ITEMS_SORT_DIRECTION[total] = False
        else:
            ITEMS_SORT_DIRECTION[total] = True

        if "time_interval" in content[item]:
            ITEMS_TIME_INTERVAL[total] = int(content[item]["time_interval"])
        else:
            ITEMS_TIME_INTERVAL[total] = 24


read_config("config.json")
