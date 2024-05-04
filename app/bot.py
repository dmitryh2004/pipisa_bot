import aiogram
from aiogram import Bot, types
from aiogram.dispatcher.dispatcher import Dispatcher

import logging

from aiogram.utils.keyboard import InlineKeyboardBuilder

import config
from app.message_logging import MessageLogger
from config import *
from app.dialogs import msg
from database import databaseEntity as db
from database import usernameDatabaseEntity as udb
from database import groupsDatabaseEntity as gdb
from database import promoDatabaseEntity as pdb
from database import blacklistDatabaseEntity as bldb

import random

import datetime
import pytz

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
ml = MessageLogger()


last_save_time = datetime.datetime.now()


def build_top_10(group, item):
    """
    Строит топ-10 по текущему измерению в группе.
    :param group: Группа
    :param item: Текущее измерение
    :return: Строка с топ-10 по текущему измерению в группе
    """
    raw_text = db.get_top(group, item, amount=10)
    string = ""
    total = 0
    for entry in raw_text:
        total += 1
        string += f"{total_emojis[total]} | {entry[1]} - {entry[0]} см.\n"
    return string


def change_dimension(group, user, item):
    """
    Изменяет измерение на случайную величину согласно конфигурации
    :param group: Группа
    :param user: Пользователь
    :param item: Измерение
    :return: Новое измерение; изменение измерения
    """
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
    """
    Обработка сообщения, полученного ботом
    :param message: Сообщение
    :return: none
    """
    ml.log_message(message)
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
    if config.DEBUG:  # проверка на дебаг
        if group not in config.DEBUG_GROUPS:
            await bot.send_message(group, msg.unavailable, thread)
            return

    # проверка на чс
    if bldb.hasUser(user_id):
        ban_entry = bldb.getUser(user_id)
        reason, unban_date = ban_entry[1], ban_entry[2]
        if unban_date is not None:
            unban_date = datetime.datetime.strptime(bldb.getUser(user_id)[2], "%Y-%m-%d %H:%M:%S")
            if datetime.datetime.now() < unban_date:
                unban_date = unban_date.strftime("%d.%m.%Y в %H:%M:%S по московскому времени")
                await bot.send_message(group, msg.banned.format(name=user_name, reason=reason, unban_date=unban_date), thread)
                return
            else:
                bldb.unban(user_id)
        else:
            await bot.send_message(group, msg.banned_forever.format(name=user_name, reason=reason),
                                   thread)
            return

    if text == "/help":
        await bot.send_message(group, msg.help, thread)
    else:
        # добавить имя юзера в базу данных юзернеймов
        gdb.append(group, group_name)
        udb.append(user_id, user_name, udb.getUserRole(user_id))
        if text == "/make_turn":
            if group != user_id:
                dim = db.getCurrent(group, user_id)
                timezone = pytz.timezone("Europe/Moscow")
                current_time = datetime.datetime.now(timezone).replace(tzinfo=None)
                last_attempt = db.getLastAttempt(group, user_id, dim)
                diff = current_time - last_attempt
                # для дебага времени (если будет нужен)
                # logging.info(f"current: {str(current_time)}\nlast: {str(last_attempt)}\ndiff: {str(diff)}\nhours: {int(diff.total_seconds()) // 3600}")
                if (diff.total_seconds() // 3600) >= config.ITEMS_TIME_INTERVAL[dim]:
                    current, offset = change_dimension(group, user_id, dim)
                    offset_sign = ""
                    smile = ""
                    offset_val = abs(offset)
                    if offset >= 0:
                        offset_sign = "увеличилось"
                        smile = "\U0001F4C8"
                    else:
                        offset_sign = "уменьшилось"
                        smile = "\U0001F4C9"
                    db.setLastAttempt(group, user_id, dim)
                    await bot.send_message(group, msg.make_turn.format(smile=smile, name=user_name, dimension=ITEMS_LOC[dim], offset_sign=offset_sign,
                                                              offset_val=offset_val, current=current), thread)
                else:
                    nextAttempt = last_attempt + datetime.timedelta(hours=config.ITEMS_TIME_INTERVAL[dim])
                    await bot.send_message(group, msg.make_turn_too_fast.format(name=user_name, dimension=ITEMS_LOC[dim],
                                                                                current=db.getDimension(group, user_id, dim),
                                                                                next_time=nextAttempt.strftime("%d.%m.%Y в %H:%M:%S")), thread)
            else:
                await bot.send_message(group, msg.dimensions_only_in_groups.format(name=user_name), thread)
        elif text == "/current":
            if group != user_id:
                dim = db.getCurrent(group, user_id)
                await bot.send_message(group, msg.current_dimension.format(name=user_name, item=ITEMS_LOC[dim],
                                                                  current=db.getDimension(group, user_id, dim)), thread)
            else:
                await bot.send_message(group, msg.dimensions_only_in_groups.format(name=user_name), thread)
        elif text == "/switch":
            if group != user_id:
                btns = InlineKeyboardBuilder()
                btn = []
                for item in ITEMS_LOC:
                    btn.append(types.InlineKeyboardButton(text=ITEMS_LOC[item], callback_data=str(item)))
                for i in range(0, len(btn), 2):
                    if i+1 < len(btn):
                        btns.row(btn[i], btn[i+1])
                    else:
                        btns.row(btn[i])
                await bot.send_message(group, msg.switch.format(name=user_name), thread, reply_markup=btns.as_markup())
            else:
                await bot.send_message(group, msg.dimensions_only_in_groups.format(name=user_name), thread)
        elif text == "/top10_current":
            if group != user_id:
                dim = db.getCurrent(group, user_id)
                top10 = build_top_10(group, dim)
                await bot.send_message(group, msg.top10_current.format(item=ITEMS_LOC[dim], top10=top10), thread)
            else:
                await bot.send_message(group, msg.dimensions_only_in_groups.format(name=user_name), thread)
        elif text == "/top10_current_png":
            if group != user_id:
                dim = db.getCurrent(group, user_id)
                if not config.ITEMS_SORT_DIRECTION[dim]:
                    await bot.send_message(group, msg.top10_current_png_unable.format(item=ITEMS_LOC[dim]), thread)
                else:
                    img_path = aiogram.types.FSInputFile(db.form_piechart_top_10(group, dim))
                    await bot.send_photo(group, img_path, thread)
            else:
                await bot.send_message(group, msg.dimensions_only_in_groups.format(name=user_name), thread)
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
                    if not pdb.hasPromo(promo_id):
                        await bot.send_message(group, msg.promo_error.format(name=user_name, promo_id=promo_id, desc="Такого промокода не существует."), thread)
                    else:
                        if not gdb.hasGroup(target_group_id):
                            await bot.send_message(group, msg.promo_error.format(name=user_name, promo_id=promo_id,
                                                                                 desc=f"Группы с ID {target_group_id} нет в базе данных бота."),
                                                   thread)
                        else:
                            success, promo_message = db.usePromo(target_group_id, user_id, promo_id)
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
                    if not pdb.hasPromo(promo):
                        if not (int(min_role) in range(0, 4)):
                            await bot.send_message(group, msg.invalid_syntax.format(desc="Указана неверная минимальная роль (допустимые значения: 0,1,2,3)"), thread)
                        if not (int(promo_uses) > 0):
                            await bot.send_message(group, msg.invalid_syntax.format(
                                desc="Число использований должно быть целым положительным числом"), thread)
                        pdb.setPromo(promo, bonus, promo_uses, min_role)
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
                    if not pdb.hasPromo(promo):
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
        elif text.split()[0] == "/promo_list":
            if group == user_id and udb.getUserRole(user_id) >= 2:
                try:
                    promos = pdb.getPromos()
                    if promos == "":
                        promos = "(нет промокодов)"
                    await bot.send_message(group,
                                           msg.promo_list.format(promos=promos),
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
                            if not udb.hasUser(player):
                                await bot.send_message(group, msg.set_role_fail.format(
                                        name=user_name, desc=f"Игрок с ID {player} ни разу не пользовался ботом."),
                                                       thread)
                            else:
                                if player == user_id:
                                    await bot.send_message(group, msg.set_role_fail.format(
                                        name=user_name, desc=f"Вы не можете изменить свою роль."),
                                                           thread)
                                else:
                                    if udb.getUserRole(player) > max_role_to_set:
                                        await bot.send_message(group, msg.set_role_fail.format(
                                            name=user_name, desc=f"Роль игрока с ID {player} выше или равна вашей."),
                                                               thread)
                                    else:
                                        udb.append(player, udb.getUsername(player), role)
                                        await bot.send_message(group, msg.set_role_success.format(name=user_name, target=player, target_name=udb.getUsername(player),
                                                                                              role=config.ROLES[role][0], role_desc=config.ROLES[role][1]), thread)
                except IndexError as e:
                    await bot.send_message(group, msg.invalid_syntax.format(desc=""), thread)
            else:
                await bot.send_message(group, msg.unknown, thread)
        # версия 0.9
        elif text == "/testers_list":
            if group == user_id and udb.getUserRole(user_id) >= 2:
                testers_list = udb.getTesters()
                string = "\n".join([f"{entry[1]} (ID = {entry[0]}): {config.ROLES[entry[2]][0]}" for entry in testers_list])
                await bot.send_message(group, msg.testers_list.format(testers=string), thread)
            else:
                await bot.send_message(group, msg.unknown, thread)
        elif text == "/admins_list":
            if group == user_id and udb.getUserRole(user_id) >= 3:
                admins_list = udb.getAdmins()
                string = "\n".join([f"{entry[1]} (ID = {entry[0]}): {config.ROLES[entry[2]][0]}" for entry in admins_list])
                await bot.send_message(group, msg.admins_list.format(admins=string), thread)
            else:
                await bot.send_message(group, msg.unknown, thread)
        elif text.split()[0] == "/ban":
            if group == user_id and udb.getUserRole(user_id) >= 2:
                max_role_to_ban = 1 if udb.getUserRole(user_id) == 2 else 2
                try:
                    target_user = int(text.split()[1])
                    if udb.getUserRole(int(target_user)) > max_role_to_ban:
                        await bot.send_message(group, msg.ban_fail.format(name=user_name,
                                                                             target_name=udb.getUsername(target_user),
                                                                             target=target_user), thread)
                        return
                    reason = config.BAN_REASONS["0"]
                    duration = None
                    if len(text.split()) >= 3:
                        reason = config.BAN_REASONS[text.split()[2]] if text.split()[2] in config.BAN_REASONS else config.BAN_REASONS["0"]
                        if len(text.split()) >= 4:
                            duration = int(text.split()[3])
                    bldb.append(target_user, reason, duration)
                    unban_date = None
                    if duration is not None:
                        unban_date = datetime.datetime.strptime(bldb.getUser(target_user)[2], "%Y-%m-%d %H:%M:%S")
                        unban_date = unban_date.strftime("%d.%m.%Y в %H:%M:%S по московскому времени")
                    if unban_date is not None:
                        await bot.send_message(group, msg.ban_success.format(name=user_name,
                                                                             target_name=udb.getUsername(target_user),
                                                                             target=target_user,
                                                                             reason=reason,
                                                                             unban_date=unban_date),
                                               thread)
                    else:
                        await bot.send_message(group, msg.ban_forever_success.format(name=user_name,
                                                                             target_name=udb.getUsername(target_user),
                                                                             target=target_user,
                                                                             reason=reason),
                                               thread)
                except IndexError as e:
                    await bot.send_message(group, msg.invalid_syntax.format(desc=""), thread)
            else:
                await bot.send_message(group, msg.unknown, thread)
        elif text.split()[0] == "/unban":
            if group == user_id and udb.getUserRole(user_id) >= 2:
                try:
                    target_user = int(text.split()[1])
                    if not bldb.hasUser(target_user):
                        await bot.send_message(group, msg.unban_fail.format(
                            name=user_name,
                            target_name=udb.getUsername(target_user),
                            target=target_user), thread)
                    else:
                        bldb.unban(target_user)
                        await bot.send_message(group, msg.unban_success.format(
                            name=user_name,
                            target_name=udb.getUsername(target_user),
                            target=target_user), thread)
                except IndexError as e:
                    await bot.send_message(group, msg.invalid_syntax.format(desc=""), thread)
            else:
                await bot.send_message(group, msg.unknown, thread)
        else:
            await bot.send_message(group, msg.unknown, thread)


@dp.callback_query(lambda c: True)
async def callback_handler(c):
    """
    Обработка нажатия на кнопку выбора измерения
    :param c: Нажатая кнопка
    :return: none
    """
    callback_item = int(c.data)
    for item in ITEMS:
        if callback_item == item:
            message = c.message
            user_name = c.from_user.first_name
            user_id = c.from_user.id
            group = message.chat.id
            thread = message.message_thread_id if message.is_topic_message else None
            db.setCurrent(group, user_id, callback_item)
            current = db.getDimension(group, user_id, db.getCurrent(group, user_id))
            if current is None:
                current = 0
            await bot.send_message(group, msg.switch_confirm.format(name=user_name, item=ITEMS_LOC[callback_item], current=current), thread)


@dp.shutdown()
async def on_shutdown():
    """
    Метод, вызываемый при выключении бота
    :return: none
    """
    logging.warning('Shutting down..')
    # выгрузка базы данных
    db.closeDatabase()
    udb.closeDatabase()
    gdb.closeDatabase()
    pdb.closeDatabase()
    # удалить все сгенерированные файлы
    generated_dir = 'generated'
    for f in os.listdir(generated_dir):
        os.remove(os.path.join(generated_dir, f))
