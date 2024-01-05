import json
import logging
import math

from settings import TOKEN

logging.basicConfig(level=logging.INFO)

BOT_VERSION = 0.3
BOT_NAME = "pipisa_plus_bot"

DATABASE_LOC = "database.json"
USERNAME_DATABASE_LOC = "usernames.json"

ITEMS = {}
ITEMS_LOC = {}
ITEMS_MIN_OFFSET = {}
ITEMS_MAX_OFFSET = {}
ITEMS_MIN_VALUE = {}
ITEMS_MAX_VALUE = {}
ITEMS_START_VALUE = {}
ITEMS_SORT_DIRECTION = {}  # True - по убыванию, False - по возрастанию


def read_config(filepath):
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
            ITEMS_MIN_OFFSET[str(total)] = -10
            
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


read_config("config.json")
