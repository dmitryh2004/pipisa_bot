import json
import logging
import math

from settings import TOKEN

logging.basicConfig(level=logging.INFO)

BOT_VERSION = "0.8.2"
BOT_NAME = "pipisa_plus_bot"

DATABASE_LOC = r"./database/database.json"
PROMO_DATABASE_LOC = r"./database/promos.json"
USERNAME_DATABASE_LOC = r"./database/usernames.json"
GROUP_DATABASE_LOC = r"./database/groupnames.json"

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
        ITEMS[str(total)] = item
        if "loc" in content[item]:
            ITEMS_LOC[str(total)] = content[item]["loc"]
        else:
            ITEMS_LOC[str(total)] = item
        
        if "min_offset" in content[item]:
            ITEMS_MIN_OFFSET[str(total)] = int(content[item]["min_offset"])
        else:
            ITEMS_MIN_OFFSET[str(total)] = -5
            
        if "max_offset" in content[item]:
            ITEMS_MAX_OFFSET[str(total)] = int(content[item]["max_offset"])
        else:
            ITEMS_MAX_OFFSET[str(total)] = 10

        if "min_value" in content[item]:
            ITEMS_MIN_VALUE[str(total)] = int(content[item]["min_value"])
        else:
            ITEMS_MIN_VALUE[str(total)] = -math.inf

        if "max_value" in content[item]:
            ITEMS_MAX_VALUE[str(total)] = int(content[item]["max_value"])
        else:
            ITEMS_MAX_VALUE[str(total)] = math.inf

        if "start_value" in content[item]:
            ITEMS_START_VALUE[str(total)] = int(content[item]["start_value"])
        else:
            ITEMS_START_VALUE[str(total)] = 0

        if "reverse_sort" in content[item]:
            ITEMS_SORT_DIRECTION[str(total)] = False
        else:
            ITEMS_SORT_DIRECTION[str(total)] = True

        if "time_interval" in content[item]:
            ITEMS_TIME_INTERVAL[str(total)] = int(content[item]["time_interval"])
        else:
            ITEMS_TIME_INTERVAL[str(total)] = 24


read_config("config.json")
