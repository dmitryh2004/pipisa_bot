import datetime
import logging

from aiogram import types

import pytz
from pathlib import Path


class MessageLogger:
    LOG_DIRECTORY = Path(r"logs")

    current_log_file = ""

    def __init__(self):
        self.update_current_log_file()

    def update_current_log_file(self):
        timezone = pytz.timezone("Europe/Moscow")
        current_time = datetime.datetime.now(timezone).replace(tzinfo=None)
        log_file_name = f"log_{current_time.strftime('%Y-%m-%d_%H')}h.log"
        self.current_log_file = Path("logs/" + log_file_name)

    def log_message(self, message: types.message.Message):
        self.update_current_log_file()
        timezone = pytz.timezone("Europe/Moscow")
        current_time = datetime.datetime.now(timezone).replace(tzinfo=None)
        id = message.message_id
        text = message.text
        group = message.chat.id
        group_name = message.chat.full_name
        user_name = message.from_user.full_name
        user_id = message.from_user.id
        log_text = f"[{current_time.strftime('%H:%M:%S %d.%m.%Y')}] Message {id} from user {user_name} (ID = {user_id}) in group {group_name} (ID = {group}). Text: {text}\n"
        if self.current_log_file.is_file():
            with open(self.current_log_file.absolute(), "a") as log_file:
                log_file.write(log_text)
        else:
            with open(self.current_log_file.absolute(), "w+") as log_file:
                log_file.write(log_text)