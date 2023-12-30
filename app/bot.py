import aiogram
from aiogram import Bot, types
from aiogram.dispatcher.dispatcher import Dispatcher

import logging

from aiogram.utils.keyboard import InlineKeyboardBuilder

import config
from config import *
from app.dialogs import msg
from database import databaseEntity as db
from database import usernameDatabaseEntity as udb

import random

import datetime


bot = Bot(token=TOKEN)
dp = Dispatcher()


last_save_time = datetime.datetime.now()


def autosave_dbs():
    global last_save_time
    current_time = datetime.datetime.now()
    if (current_time - last_save_time).total_seconds() > 300.0:  # 5 минут
        db.saveDatabase(config.DATABASE_LOC)
        udb.saveDatabase(config.USERNAME_DATABASE_LOC)
        last_save_time = current_time


def build_top_10(group, item):
    raw_text = db.get_top_10(group, item)
    string = ""
    total = 0
    for entry in raw_text:
        total += 1
        string += f"{total} | {entry[1]} - {entry[0]} см.\n"
    return string


def change_dimension(group, user, item):
    dimension = int(db.getDimension(group, user, item))
    min_offset = int(ITEMS_MIN_OFFSET[item])
    max_offset = int(ITEMS_MAX_OFFSET[item])
    offset = random.randint(min_offset, max_offset)
    if offset >= 0:
        if (dimension + offset) > ITEMS_MAX_VALUE[item]:
            db.setDimension(group, user, item, ITEMS_MAX_VALUE[item])
            offset = ITEMS_MAX_VALUE[item] - dimension
        else:
            db.setDimension(group, user, item, dimension + offset)
    else:
        if (dimension + offset) < ITEMS_MIN_VALUE[item]:
            db.setDimension(group, user, item, ITEMS_MIN_VALUE[item])
            offset = dimension - ITEMS_MIN_VALUE[item]
        else:
            db.setDimension(group, user, item, dimension + offset)
    return (dimension + offset), offset


@dp.message(aiogram.F.text)
async def handle_message(message: types.message.Message):
    text = message.text
    group = message.chat.id
    user_name = message.from_user.first_name
    user_id = message.from_user.id
    thread = message.message_thread_id if message.is_topic_message else None

    if "@" in text:  # если сообщение в группе
        if ("@" + BOT_NAME) in text:  # если сообщение для этого бота
            text = text.split("@")[0]  # то обрезаем команду
        else:
            return
    if text == "/help":
        await bot.send_message(group, msg.help, thread)
    else:
        # добавить имя юзера в базу данных юзернеймов
        udb.append(str(user_id), str(user_name))
        if text == "/make_turn":
            dim = db.getCurrent(str(group), str(user_id))
            current, offset = change_dimension(str(group), str(user_id), dim)
            offset_sign = ""
            offset_val = abs(offset)
            if offset >= 0:
                offset_sign = "увеличилось"
            else:
                offset_sign = "уменьшилось"
            await bot.send_message(group, msg.make_turn.format(name=user_name, dimension=ITEMS_LOC[dim], offset_sign=offset_sign,
                                                      offset_val=offset_val, current=current), thread)
        elif text == "/current":
            dim = db.getCurrent(str(group), str(user_id))
            await bot.send_message(group, msg.current_dimension.format(name=user_name, item=ITEMS_LOC[dim],
                                                              current=db.getDimension(str(group), str(user_id), dim)), thread)
        elif text == "/switch":
            btns = InlineKeyboardBuilder()
            btn = []
            for item in ITEMS_LOC:
                btn.append(types.InlineKeyboardButton(text=ITEMS_LOC[item], callback_data=item))
            for i in range(0, len(btn), 2):
                if i+1 < len(btn):
                    btns.row(btn[i], btn[i+1])
                else:
                    btns.row(btn[i])
            await bot.send_message(group, msg.switch.format(name=user_name), thread, reply_markup=btns.as_markup())
        elif text == "/top10_current":
            dim = db.getCurrent(str(group), str(user_id))
            top10 = build_top_10(str(group), dim)
            await bot.send_message(group, msg.top10_current.format(item=ITEMS_LOC[dim], top10=top10), thread)
        else:
            await bot.send_message(group, msg.unknown, thread)
        autosave_dbs()


@dp.callback_query(lambda c: True)
async def callback_handler(c):
    for item in ITEMS:
        if c.data == item:
            message = c.message
            user_name = c.from_user.first_name
            user_id = c.from_user.id
            group = message.chat.id
            thread = message.message_thread_id if message.is_topic_message else None
            db.setCurrent(str(group), str(user_id), c.data)
            current = db.getDimension(str(group), str(user_id), db.getCurrent(str(group), str(user_id)))
            await bot.send_message(group, msg.switch_confirm.format(name=user_name, item=ITEMS_LOC[c.data], current=current), thread)


@dp.shutdown()
async def on_shutdown():
    logging.warning('Shutting down..')
    # выгрузка базы данных
    db.saveDatabase(config.DATABASE_LOC)
    udb.saveDatabase(config.USERNAME_DATABASE_LOC)
