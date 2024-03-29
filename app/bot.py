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
from database import groupsDatabaseEntity as gdb
from database import promoDatabaseEntity as pdb

import random

import datetime

import os


total_emojis = {
    1: "\U0001F947",
    2: "\U0001F948",
    3: "\U0001F949",
    4: "\U00000034\U0000FE0F\U000020E3",
    5: "\U00000035\U0000FE0F\U000020E3",
    6: "\U00000036\U0000FE0F\U000020E3",
    7: "\U00000037\U0000FE0F\U000020E3",
    8: "\U00000038\U0000FE0F\U000020E3",
    9: "\U00000039\U0000FE0F\U000020E3",
    10: "\U0001F51F"
}


bot = Bot(token=TOKEN)
dp = Dispatcher()


last_save_time = datetime.datetime.now()


def build_top_10(group, item):
    raw_text = db.get_top(group, item, amount=10)
    string = ""
    total = 0
    for entry in raw_text:
        total += 1
        string += f"{total_emojis[total]} | {entry[1]} - {entry[0]} см.\n"
    return string


def change_dimension(group, user, item):
    dimension = int(db.getDimension(group, user, item))
    min_offset = int(ITEMS_MIN_OFFSET[item])
    max_offset = int(ITEMS_MAX_OFFSET[item])
    offset = random.randint(min_offset, max_offset)
    bonus = db.getBonus(group, user, item)
    db.useBonus(group, user, item)
    if offset >= 0:
        if (dimension + offset + bonus) > ITEMS_MAX_VALUE[item]:
            db.setDimension(group, user, item, ITEMS_MAX_VALUE[item])
            offset = ITEMS_MAX_VALUE[item] - dimension - bonus
        else:
            db.setDimension(group, user, item, dimension + offset + bonus)
    else:
        if (dimension + offset + bonus) < ITEMS_MIN_VALUE[item]:
            db.setDimension(group, user, item, ITEMS_MIN_VALUE[item])
            offset = (dimension + bonus) - ITEMS_MIN_VALUE[item]
        else:
            db.setDimension(group, user, item, dimension + offset + bonus)
    return (dimension + offset + bonus), offset


@dp.message(aiogram.F.text)
async def handle_message(message: types.message.Message):
    text = message.text
    group = message.chat.id
    group_name = message.chat.full_name
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
        gdb.append(str(group), str(group_name))
        udb.append(str(user_id), str(user_name), udb.getUserRole(user_id))
        if text == "/make_turn":
            dim = db.getCurrent(str(group), str(user_id))
            current_time = datetime.datetime.now()
            last_attempt = db.getLastAttempt(str(group), str(user_id), dim)
            diff = current_time - last_attempt
            # для дебага времени (если будет нужен)
            # logging.info(f"current: {str(current_time)}\nlast: {str(last_attempt)}\ndiff: {str(diff)}\nhours: {int(diff.total_seconds()) // 3600}")
            if (diff.total_seconds() // 3600) >= config.ITEMS_TIME_INTERVAL[dim]:
                current, offset = change_dimension(str(group), str(user_id), dim)
                offset_sign = ""
                smile = ""
                offset_val = abs(offset)
                if offset >= 0:
                    offset_sign = "увеличилось"
                    smile = "\U0001F4C8"
                else:
                    offset_sign = "уменьшилось"
                    smile = "\U0001F4C9"
                db.setLastAttempt(str(group), str(user_id), dim)
                await bot.send_message(group, msg.make_turn.format(smile=smile, name=user_name, dimension=ITEMS_LOC[dim], offset_sign=offset_sign,
                                                          offset_val=offset_val, current=current), thread)
            else:
                nextAttempt = last_attempt + datetime.timedelta(hours=config.ITEMS_TIME_INTERVAL[dim])
                await bot.send_message(group, msg.make_turn_too_fast.format(name=user_name, dimension=ITEMS_LOC[dim],
                                                                            current=db.getDimension(str(group), str(user_id), dim),
                                                                            next_time=nextAttempt.strftime("%d.%m.%Y в %H:%M:%S")), thread)
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
        elif text == "/top10_current_png":
            dim = db.getCurrent(str(group), str(user_id))
            if not config.ITEMS_SORT_DIRECTION[dim]:
                await bot.send_message(group, msg.top10_current_png_unable.format(item=ITEMS_LOC[dim]), thread)
            else:
                img_path = aiogram.types.FSInputFile(db.form_piechart_top_10(str(group), dim))
                await bot.send_photo(group, img_path, thread)
        # здесь начинается 0.8
        elif text == "/my_role":
            if group == user_id:
                role_id = udb.getUserRole(user_id)
                role = config.ROLES[role_id][0]
                desc = config.ROLES[role_id][1]
                await bot.send_message(group, msg.my_role.format(name=user_name, role=role, desc=desc), thread)
            else:
                await bot.send_message(group, msg.my_role_not_in_groups.format(name=user_name), thread)
        elif text == "/my_id":
            if group == user_id:
                await bot.send_message(group, msg.my_id.format(name=user_name, user_id=user_id), thread)
            else:
                await bot.send_message(group, msg.my_id_not_in_groups.format(name=user_name), thread)
        elif text == "/group_id":
            if group == user_id:
                await bot.send_message(group, msg.group_id_only_in_groups.format(name=user_name), thread)
            else:
                await bot.send_message(group, msg.group_id.format(name=user_name, group_id=group), thread)
        elif text == "/help_promo":
            if group == user_id:
                await bot.send_message(group, msg.help_promo, thread)
            else:
                await bot.send_message(group, msg.help_promo_not_in_groups.format(name=user_name), thread)
        elif text.split(" ")[0] == "/promo":
            if group == user_id:
                try:
                    promo_id = text.split(" ")[1]
                    target_group_id = text.split(" ")[2]
                    if not (promo_id in pdb.database):
                        await bot.send_message(group, msg.promo_error.format(name=user_name, promo_id=promo_id, desc="Такого промокода не существует."), thread)
                    else:
                        if not (target_group_id in db.database):
                            await bot.send_message(group, msg.promo_error.format(name=user_name, promo_id=promo_id,
                                                                                 desc=f"Группы с ID {target_group_id} нет в базе данных бота."),
                                                   thread)
                        else:
                            success, promo_message = db.usePromo(str(target_group_id), str(user_id), str(promo_id))
                            if success:
                                await bot.send_message(group, msg.promo_success.format(name=user_name, desc=promo_message), thread)
                            else:
                                await bot.send_message(group, msg.promo_error.format(name=user_name, promo_id=promo_id,
                                                                                     desc=promo_message), thread)
                except IndexError as e:
                    await bot.send_message(group, msg.invalid_syntax.format(desc=""), thread)

            else:
                await bot.send_message(group, msg.promo_not_in_groups.format(name=user_name), thread)
        # 0.8 - команды админа
        elif text == "/admin_features":
            if group == user_id:
                role = udb.getUserRole(user_id)
                if role != 2:
                    await bot.send_message(group, msg.unknown, thread)
                else:
                    await bot.send_message(group, msg.admin_help, thread)
            else:
                await bot.send_message(group, msg.unknown, thread)
        elif text == "/developer_features":
            if group == user_id:
                role = udb.getUserRole(user_id)
                if role != 3:
                    await bot.send_message(group, msg.unknown, thread)
                else:
                    await bot.send_message(group, msg.dev_help, thread)
            else:
                await bot.send_message(group, msg.unknown, thread)
        elif text.split()[0] == "/add_promo":
            if group == user_id and udb.getUserRole(user_id) >= 2:
                try:
                    promo, bonus, promo_uses, min_role = text.split()[1], text.split()[2], text.split()[3], text.split()[4]
                    if not (promo in pdb.database):
                        if not (int(min_role) in range(0, 4)):
                            await bot.send_message(group, msg.invalid_syntax.format(desc="Указана неверная минимальная роль (допустимые значения: 0,1,2,3)"), thread)
                        if not (int(promo_uses) > 0):
                            await bot.send_message(group, msg.invalid_syntax.format(
                                desc="Число использований должно быть целым положительным числом"), thread)
                        pdb.setPromo(promo, int(bonus), int(promo_uses), int(min_role))
                        await bot.send_message(group, msg.add_promo_success.format(name=user_name, promo_id=promo, promo_uses=promo_uses, min_role=config.ROLES[int(min_role)][0]))
                    else:
                        await bot.send_message(group, msg.add_promo_already_exists.format(name=user_name, promo_id=promo), thread)
                except IndexError as e:
                    await bot.send_message(group, msg.invalid_syntax.format(desc=""), thread)
            else:
                await bot.send_message(group, msg.unknown, thread)
        elif text.split()[0] == "/remove_promo":
            if group == user_id and udb.getUserRole(user_id) >= 2:
                try:
                    promo = text.split()[1]
                    if not (promo in pdb.database):
                        await bot.send_message(group,
                                               msg.remove_promo_dont_exist.format(name=user_name, promo_id=promo),
                                               thread)
                    else:
                        pdb.database.pop(promo)
                        await bot.send_message(group,
                                               msg.remove_promo_success.format(name=user_name, promo_id=promo),
                                               thread)
                except IndexError as e:
                    await bot.send_message(group, msg.invalid_syntax.format(desc=""), thread)
            else:
                await bot.send_message(group, msg.unknown, thread)
        elif text.split()[0] == "/set_role":
            if group == user_id and udb.getUserRole(user_id) >= 2:
                max_role_to_set = 1 if udb.getUserRole(user_id) == 2 else 2
                try:
                    player, role = text.split()[1], int(text.split()[2])
                    if not (role in range(0, 4)):
                        await bot.send_message(group, msg.invalid_syntax.format(
                            desc="Указана неверная роль (допустимые значения: 0,1,2,3)"), thread)
                    else:
                        if role > max_role_to_set:
                            await bot.send_message(group, msg.invalid_syntax.format(
                                desc=f"Указанная роль выше максимальной роли, которую вы можете назначить ({max_role_to_set})"), thread)
                        else:
                            if not (player in udb.database):
                                await bot.send_message(group, msg.set_role_fail.format(
                                        name=user_name, desc=f"Игрок с ID {player} ни разу не пользовался ботом."),
                                                       thread)
                            else:
                                if player == str(user_id):
                                    await bot.send_message(group, msg.set_role_fail.format(
                                        name=user_name, desc=f"Вы не можете изменить свою роль."),
                                                           thread)
                                else:
                                    if udb.getUserRole(player) > max_role_to_set:
                                        await bot.send_message(group, msg.set_role_fail.format(
                                            name=user_name, desc=f"Роль игрока с ID {player} выше или равна вашей."),
                                                               thread)
                                    else:
                                        udb.database[player]["role"] = role
                                        await bot.send_message(group, msg.set_role_success.format(name=user_name, target=player, target_name=udb.getUsername(player),
                                                                                              role=config.ROLES[role][0], role_desc=config.ROLES[role][1]), thread)
                except IndexError as e:
                    await bot.send_message(group, msg.invalid_syntax.format(desc=""), thread)
            else:
                await bot.send_message(group, msg.unknown, thread)
        else:
            await bot.send_message(group, msg.unknown, thread)


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
            if current is None:
                current = 0
            await bot.send_message(group, msg.switch_confirm.format(name=user_name, item=ITEMS_LOC[c.data], current=current), thread)


@dp.shutdown()
async def on_shutdown():
    logging.warning('Shutting down..')
    # выгрузка базы данных
    db.saveDatabase(config.DATABASE_LOC)
    udb.saveDatabase()
    gdb.saveDatabase()
    # удалить все сгенерированные файлы
    generated_dir = 'generated'
    for f in os.listdir(generated_dir):
        os.remove(os.path.join(generated_dir, f))
