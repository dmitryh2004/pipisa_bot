import datetime
import os
import logging
import traceback
import matplotlib.pyplot as plt
import pytz
import sqlite3

import config


class NameDatabase:
    """
    Класс базы данных с названиями групп
    """
    location = ""

    def __init__(self, location):
        self.location = location
        try:
            self.connection = sqlite3.connect(location)
            self.cursor = self.connection.cursor()
        except Exception as e:
            logging.error("An unknown error occured.\nException info is printed below.")
            logging.error(traceback.format_exc())

    def closeDatabase(self):
        """
        Сохраняет базу данных групп
        :return: none
        """
        try:
            self.cursor.close()
            self.connection.close()
        except Exception as e:
            logging.error("An unknown error occured.\nException info is printed below.")
            logging.error(traceback.format_exc())

    def append(self, group_id, group_name):
        """
        Добавляет новую запись в базу данных
        :param group_id: ИД группы
        :param group_name: Название группы
        :return: none
        """
        insert_query = "INSERT OR REPLACE INTO groupnames (group_id, group_name) VALUES (?, ?)"
        data = (group_id, group_name)
        self.cursor.execute(insert_query, data)
        self.connection.commit()

    def getName(self, group_id):
        """
        Возвращает имя группы по id
        :param group_id: ИД группы
        :return: название группы
        """
        select_query = "SELECT group_name FROM groupnames WHERE group_id = (?)"
        self.cursor.execute(select_query, (group_id, ))
        return self.cursor.fetchone()[0]

    def hasGroup(self, group_id):
        select_query = "SELECT * FROM groupnames WHERE group_id = (?)"
        self.cursor.execute(select_query, (group_id,))
        res = self.cursor.fetchone()
        return res is not None


groupsDatabaseEntity = NameDatabase(config.DATABASE_LOC)


class UserDatabase:
    """
    Класс базы данных о пользователях: их именах и ролях
    """
    location = ""

    def __init__(self, location):
        self.location = location
        try:
            self.connection = sqlite3.connect(location)
            self.cursor = self.connection.cursor()
        except Exception as e:
            logging.error("An unknown error occured.\nException info is printed below.")
            logging.error(traceback.format_exc())

    def closeDatabase(self):
        """
        Сохраняет базу данных групп
        :return: none
        """
        try:
            self.cursor.close()
            self.connection.close()
        except Exception as e:
            logging.error("An unknown error occured.\nException info is printed below.")
            logging.error(traceback.format_exc())

    def append(self, user_id, user_name, role=0):
        """
        Добавляет запись о новом пользователе или обновляет существующую
        :param user_id: ИД пользователя
        :param user_name: Имя пользователя
        :param role: Роль пользователя
        :return: none
        """
        insert_query = "INSERT OR REPLACE INTO usernames (user_id, username, role) VALUES (?, ?, ?)"
        data = (user_id, user_name, role)
        self.cursor.execute(insert_query, data)
        self.connection.commit()

    def getUsername(self, user_id):
        """
        Возвращает имя пользователя по ИД
        :param user_id: ИД пользователя
        :return: Имя пользователя
        """
        select_query = "SELECT username FROM usernames WHERE user_id = (?)"
        self.cursor.execute(select_query, (user_id,))
        return self.cursor.fetchone()[0]

    def getUserRole(self, user_id):
        """
        Возвращает роль пользователя по ИД
        :param user_id: ИД пользователя
        :return: Роль пользователя
        """
        select_query = "SELECT role FROM usernames WHERE user_id = (?)"
        self.cursor.execute(select_query, (user_id,))
        return self.cursor.fetchone()[0]

    def hasUser(self, user_id):
        select_query = "SELECT * FROM usernames WHERE user_id = (?)"
        self.cursor.execute(select_query, (user_id,))
        res = self.cursor.fetchone()
        return res is not None

    def getTesters(self):
        select_query = "SELECT * FROM usernames WHERE role >= 1"
        self.cursor.execute(select_query)
        res = self.cursor.fetchall()
        return res

    def getAdmins(self):
        select_query = "SELECT * FROM usernames WHERE role >= 2"
        self.cursor.execute(select_query)
        res = self.cursor.fetchall()
        return res


usernameDatabaseEntity = UserDatabase(config.DATABASE_LOC)


class PromoDatabase:
    """
    Класс базы данных промокодов
    """
    location = ""

    def __init__(self, location):
        self.location = location
        try:
            self.connection = sqlite3.connect(location)
            self.cursor = self.connection.cursor()
        except Exception as e:
            logging.error("An unknown error occured.\nException info is printed below.")
            logging.error(traceback.format_exc())

    def closeDatabase(self):
        """
        Сохраняет базу данных групп
        :return: none
        """
        try:
            self.cursor.close()
            self.connection.close()
        except Exception as e:
            logging.error("An unknown error occured.\nException info is printed below.")
            logging.error(traceback.format_exc())

    def setPromo(self, promo_id, bonus_size, max_uses, min_role):
        """
        Создает новый промокод или обновляет информацию о нем
        :param promo_id: название промокода
        :param bonus_size: бонус к измерению
        :param max_uses: максимальное число использований
        :param min_role: минимальная роль, необходимая для использования
        :return: none
        """
        insert_query = "INSERT OR REPLACE INTO promos (promo, bonus, max_uses, min_role) VALUES (?, ?, ?, ?)"
        data = (promo_id, bonus_size, max_uses, min_role)
        self.cursor.execute(insert_query, data)
        self.connection.commit()

    def getPromos(self):
        """
        Возвращает список всех промокодов из базы данных
        :return: строка с информацией о всех промокодах
        """
        select_query = "SELECT * FROM promos"
        self.cursor.execute(select_query)
        res = []
        for entry in self.cursor.fetchall():
            temp = f"{entry[0]}: бонус - {entry[1]}, максимальное число использований - {entry[2]}," \
                   f" минимальная роль для использования - {config.ROLES[entry[3]][0]}"
            res.append(temp)
        return "\n".join(res)

    def getPromoBonus(self, promo_id):
        """
        Возвращает бонус промокода по его ID
        :param promo_id: ID промокода
        :return: бонус промокода
        """
        select_query = "SELECT bonus FROM promos WHERE promo = (?)"
        self.cursor.execute(select_query, (promo_id, ))
        return self.cursor.fetchone()[0]

    def getPromoMaxUses(self, promo_id):
        """
        Возвращает максимальное число использований промокода по его ID
        :param promo_id: ID промокода
        :return: максимальное число использований промокода
        """
        select_query = "SELECT max_uses FROM promos WHERE promo = (?)"
        self.cursor.execute(select_query, (promo_id,))
        return self.cursor.fetchone()[0]

    def getPromoMinRole(self, promo_id):
        """
        Возвращает минимальную роль, необходимую для использования промокода, по его ID
        :param promo_id: ID промокода
        :return: минимальная роль, необходимая для использования
        """
        select_query = "SELECT min_role FROM promos WHERE promo = (?)"
        self.cursor.execute(select_query, (promo_id,))
        return self.cursor.fetchone()[0]

    def hasPromo(self, promo_id):
        select_query = "SELECT * FROM promos WHERE promo = (?)"
        self.cursor.execute(select_query, (promo_id,))
        res = self.cursor.fetchone()
        return res is not None


promoDatabaseEntity = PromoDatabase(config.DATABASE_LOC)


class Database:
    """
    Класс базы данных измерений
    """
    database = dict()

    def __init__(self, location):
        self.location = location
        try:
            self.connection = sqlite3.connect(location)
            self.cursor = self.connection.cursor()
        except Exception as e:
            logging.error("An unknown error occured.\nException info is printed below.")
            logging.error(traceback.format_exc())

    def checkForNonExistingUser(self, group, user):
        """
        Проверка на существование пользователя и группы в базе данных
        :param group: Группа, которую надо проверить
        :param user: Пользователь, которого надо проверить
        :return: none
        """
        currents_insert_query = "INSERT OR IGNORE INTO currents VALUES (?, ?, ?)"
        self.cursor.execute(currents_insert_query, (group, user, 1))
        for dim in config.ITEMS:
            dimensions_insert_query = "INSERT OR IGNORE INTO dimensions VALUES (?, ?, ?, ?)"
            self.cursor.execute(dimensions_insert_query, (group, user, dim, config.ITEMS_START_VALUE[dim]))
            bonuses_insert_query = "INSERT OR IGNORE INTO bonuses VALUES (?, ?, ?, ?)"
            self.cursor.execute(bonuses_insert_query, (group, user, dim, 0))
            attempts_insert_query = "INSERT OR IGNORE INTO attempts VALUES (?, ?, ?, ?)"
            default_last_attempt = str(datetime.datetime(2000, 1, 1))
            self.cursor.execute(attempts_insert_query, (group, user, dim, default_last_attempt))
        self.connection.commit()

    def checkForExistingPromoUsages(self, group, user, promo):
        """
        Проверка на существующую информацию о промокодах, использованных пользователем в группе
        :param group: Группа, которую надо проверить
        :param user: Пользователь, которого надо проверить
        :param promo: Проверяемый промокод
        :return: none
        """
        self.checkForNonExistingUser(group, user)
        promo_usages_insert_query = "INSERT OR IGNORE INTO promo_usages VALUES (?, ?, ?, ?)"
        self.cursor.execute(promo_usages_insert_query, (group, user, promo, 0))
        self.connection.commit()

    def checkForExistingAttempts(self, group, user):
        """
        Проверка на существование информации о попытках пользователя увеличить измерения
        :param group: Группа, которую надо проверить
        :param user: Пользователь, которого надо проверить
        :return: none
        """
        self.checkForNonExistingUser(group, user)
        for item in config.ITEMS:
            attempt_insert_query = "INSERT OR IGNORE INTO attempts VALUES (?, ?, ?, ?)"
            self.cursor.execute(attempt_insert_query, (group, user, item, str(datetime.datetime(2000, 1, 1))))
        self.connection.commit()

    def checkForExistingBonuses(self, group, user):
        """
        Проверка на существование информации о примененных бонусах к измерениям
        :param group: Группа, которую надо проверить
        :param user: Пользователь, которого надо проверить
        :return: none
        """
        self.checkForNonExistingUser(group, user)
        for item in config.ITEMS:
            bonus_insert_query = "INSERT OR IGNORE INTO bonuses VALUES (?, ?, ?, ?)"
            self.cursor.execute(bonus_insert_query, (group, user, item, 0))
        self.connection.commit()

    def getBonus(self, group, user, item):
        """
        Возвращает текущий бонус к измерению item игрока в группе.
        :param group: Группа
        :param user: Пользователь
        :param item: Измерение
        :return: Текущий бонус к измерению пользователя в этой группе
        """
        try:
            self.checkForExistingBonuses(group, user)
            select_query = "SELECT bonus FROM bonuses WHERE (group_id, user_id, dimension) = (?, ?, ?)"
            self.cursor.execute(select_query, (group, user, item))
            res = self.cursor.fetchone()
            return res[0] if res is not None else 0
        except Exception as e:
            logging.error("An unknown error occured.\nException info is printed below.")
            logging.error(traceback.format_exc())

    def useBonus(self, group, user, item):
        """
        Использует текущий бонус к измерению игрока в группе.
        :param group: Группа
        :param user: Пользователь
        :param item: Измерение
        :return: none
        """
        try:
            self.checkForExistingBonuses(group, user)
            update_query = "UPDATE bonuses SET bonus = 0 WHERE (group_id, user_id, dimension) = (?, ?, ?)"
            self.cursor.execute(update_query, (group, user, item))
            self.connection.commit()
        except Exception as e:
            logging.error("An unknown error occured.\nException info is printed below.")
            logging.error(traceback.format_exc())

    def getDimension(self, group, user, item):
        """
        Возвращает текущее измерение игрока в группе.
        :param group: Группа
        :param user: Пользователь
        :param item: Измерение
        :return: Размер измерения
        """
        try:
            self.checkForNonExistingUser(group, user)
            select_query = "SELECT size FROM dimensions WHERE (group_id, user_id, dimension) = (?, ?, ?)"
            self.cursor.execute(select_query, (group, user, item))
            res = self.cursor.fetchone()
            value = res[0] if res is not None else config.ITEMS_START_VALUE[item]
            return value
        except Exception as e:
            logging.error("An unknown error occured.\nException info is printed below.")
            logging.error(traceback.format_exc())

    def setDimension(self, group, user, item, value):
        """
        Устанавливает новое значение измерения игрока в группе.
        :param group: Группа
        :param user: Пользователь
        :param item: Измерение
        :param value: Новый размер
        :return: none
        """
        try:
            self.checkForNonExistingUser(group, user)
            update_query = "UPDATE dimensions SET size = ? WHERE (group_id, user_id, dimension) = (?, ?, ?)"
            self.cursor.execute(update_query, (value, group, user, item))
            self.connection.commit()
        except Exception as e:
            logging.error("An unknown error occured.\nException info is printed below.")
            logging.error(traceback.format_exc())

    def getLastAttempt(self, group, user, item):
        """
        Получает данные о времени, когда было совершено последнее изменение измерения игрока в группе.
        :param group: Группа
        :param user: Пользователь
        :param item: Измерение
        :return: Время последнего изменения
        """
        try:
            self.checkForExistingAttempts(group, user)
            select_query = "SELECT last_attempt FROM attempts WHERE (group_id, user_id, dimension) = (?, ?, ?)"
            self.cursor.execute(select_query, (group, user, item))
            attempt: datetime.datetime = datetime.datetime(2000, 1, 1)
            cursor_res = self.cursor.fetchone()
            if cursor_res is not None:
                attempt = datetime.datetime.strptime(cursor_res[0],
                                                     "%Y-%m-%d %H:%M:%S")
            return attempt
        except Exception as e:
            logging.error("An unknown error occured.\nException info is printed below.")
            logging.error(traceback.format_exc())

    def setLastAttempt(self, group, user, item):
        """
        Обновляет данные о последнем изменении измерения пользователя
        :param group: Группа
        :param user: Пользователь
        :param item: Измерение
        :return: none
        """
        try:
            self.checkForExistingAttempts(group, user)
            timezone = pytz.timezone("Europe/Moscow")
            attempt: datetime.datetime = datetime.datetime.now(timezone).replace(microsecond=0).replace(tzinfo=None)
            update_query = "UPDATE attempts SET last_attempt = ? WHERE (group_id, user_id, dimension) = (?, ?, ?)"
            self.cursor.execute(update_query, (str(attempt), group, user, item))
            self.connection.commit()
        except Exception as e:
            logging.error("An unknown error occured.\nException info is printed below.")
            logging.error(traceback.format_exc())

    def getCurrent(self, group, user):
        """
        Возвращает номер текущего измерения игрока в группе
        :param group: Группа
        :param user: Пользователь
        :return: Номер текущего измерения
        """
        try:
            self.checkForNonExistingUser(group, user)
            select_query = "SELECT current FROM currents WHERE (group_id, user_id) = (?, ?)"
            self.cursor.execute(select_query, (group, user))
            res = self.cursor.fetchone()
            value = res[0] if res is not None else 1
            return value
        except Exception as e:
            logging.error("An unknown error occured.\nException info is printed below.")
            logging.error(traceback.format_exc())

    def setCurrent(self, group, user, value):
        """
        Устанавливает номер текущего измерения игрока в группе
        :param group: Группа
        :param user: Пользователь
        :param value: Номер текущего измерения
        :return: none
        """
        try:
            self.checkForNonExistingUser(group, user)
            update_query = "UPDATE currents SET current = ? WHERE (group_id, user_id) = (?, ?)"
            self.cursor.execute(update_query, (value, group, user))
            self.connection.commit()
        except Exception as e:
            logging.error("An unknown error occured.\nException info is printed below.")
            logging.error(traceback.format_exc())

    def get_top(self, group, item, amount=None):
        """
        Возвращает топ всех пользователей по длине измерения в группе
        :param group: Группа
        :param item: Измерение
        :param amount: Количество мест, возвращаемых методом (по умолчанию возвращаются всё)
        :return: Список из первых amount мест по измерению в группе
        """
        select_query = "SELECT user_id, size from dimensions WHERE (group_id, dimension) = (?, ?)"
        self.cursor.execute(select_query, (group, item))
        results = self.cursor.fetchall()
        dimensions = []
        for user in results:
            dimensions.append((user[1], usernameDatabaseEntity.getUsername(user[0]) if usernameDatabaseEntity.getUsername(
                    user[0]) else user[0]))
        dimensions.sort(reverse=config.ITEMS_SORT_DIRECTION[item])
        if amount is not None:
            return dimensions[:amount]
        else:
            return dimensions

    def form_piechart_top_10(self, group, item):
        """
        Создает диаграмму с топ-10 измерений в группе и сохраняет ее в файл в папке generated
        :param group: Группа
        :param item: Измерение
        :return: Путь к сгенерированному файлу с диаграммой
        """
        topall = self.get_top(group, item)
        group_name = groupsDatabaseEntity.getName(group) if groupsDatabaseEntity.hasGroup(group) else group
        labels = []
        sizes = []
        total = 0
        for size, label in topall:  # создаем легенду и размеры
            if size <= 0:
                break
            total += 1
            if total <= 10:
                labels.append(label[:13] + "..." if len(label) > 13 else label)
                sizes.append(size)
            if total == 11:
                labels.append("other players")
                sizes.append(size)
            if total > 11:
                sizes[10] += size

        for i in range(len(sizes)):
            labels[i] = f"{sizes[i]} см. - {labels[i]}"

        fig, ax = plt.subplots(figsize=(10, 8))

        ax.pie(sizes, autopct='%1.1f%%', colors=config.PIE_CHART_COLORS, startangle=45, pctdistance=0.8)
        ax.set_title(f"Группа {group_name}, измерение {config.ITEMS_LOC[item]}\nСоздано ботом @{config.BOT_NAME}")
        ax.legend(labels, loc="center left", bbox_to_anchor=(0.9, 0, 0.5, 1))
        plt.tight_layout()

        file_path = f"generated\\{group}_{item}.png"
        plt.savefig(file_path)
        return file_path

    def getPromoUsages(self, group, user, promo):
        """
        Получает сведения об использовании промокода пользователем в группе
        :param group: Группа
        :param user: Пользователь
        :param promo: Промокод
        :return: Число использований промокода
        """
        try:
            self.checkForExistingPromoUsages(group, user, promo)
            val = 0
            select_query = "SELECT use_count FROM promo_usages WHERE (group_id, user_id, promo) = (?, ?, ?)"
            self.cursor.execute(select_query, (group, user, promo))
            res = self.cursor.fetchone()
            if res is not None:
                val = res[0]
            return val
        except Exception as e:
            logging.error("An unknown error occured.\nException info is printed below.")
            logging.error(traceback.format_exc())

    def usePromo(self, group, user, promo):
        """
        Проводит попытку использовать промокод. Возвращает сообщение об успехе или ошибке
        :param group: Группа
        :param user: Пользователь
        :param promo: Промокод
        :return: Сообщение об успехе или ошибке
        """
        try:
            self.checkForExistingPromoUsages(group, user, promo)
            message = ""
            success = False
            promo_usages = self.getPromoUsages(group, user, promo)
            self.checkForExistingBonuses(group, user)
            if promo_usages < promoDatabaseEntity.getPromoMaxUses(promo):
                if usernameDatabaseEntity.getUserRole(user) >= promoDatabaseEntity.getPromoMinRole(promo):
                    current_item = self.getCurrent(group, user)
                    current_bonus = self.getBonus(group, user, current_item)
                    current_bonus += promoDatabaseEntity.getPromoBonus(promo)
                    promo_usages += 1

                    update_query1 = "UPDATE bonuses SET bonus = ? WHERE (group_id, user_id, dimension) = (?, ?, ?)"
                    self.cursor.execute(update_query1, (current_bonus, group, user, current_item))
                    update_query2 = "UPDATE promo_usages SET use_count = ? WHERE (group_id, user_id, promo) = (?, ?, ?)"
                    self.cursor.execute(update_query2, (promo_usages, group, user, promo))
                    self.connection.commit()

                    message = "Промокод " + str(promo) + " успешно активирован. При следующей попытке роста в группе " + str(groupsDatabaseEntity.getName(group)) + \
                        " к измерению " + config.ITEMS_LOC[current_item] + " будет добавлено " + str(promoDatabaseEntity.getPromoBonus(promo)) + " см.\n" \
                        "Число использований промокода: " + str(promo_usages) + " / " + str(promoDatabaseEntity.getPromoMaxUses(promo))
                    success = True
                else:
                    message = "Этот промокод вам недоступен. Причина: ваших прав недостаточно для использования данного промокода (требуется роль " + \
                        config.ROLES[promoDatabaseEntity.getPromoMinRole(promo)][0] + " или выше)."
            else:
                message = "Этот промокод вам недоступен. Причина: превышено максимальное число использований (" + \
                          str(promo_usages) + " / " + str(promoDatabaseEntity.getPromoMaxUses(promo)) + ")."
            return success, message
        except Exception as e:
            logging.error("An unknown error occured.\nException info is printed below.")
            logging.error(traceback.format_exc())

    def closeDatabase(self):
        """
        Сохраняет базу данных измерений
        :return: none
        """
        try:
            self.cursor.close()
            self.connection.close()
        except Exception as e:
            logging.error("An unknown error occured.\nException info is printed below.")
            logging.error(traceback.format_exc())


databaseEntity = Database(config.DATABASE_LOC)


class BlackListDatabase:
    """
        Класс базы данных о заблокированных пользователях, причинах и длительности бана
        """
    location = ""

    def __init__(self, location):
        self.location = location
        try:
            self.connection = sqlite3.connect(location)
            self.cursor = self.connection.cursor()
        except Exception as e:
            logging.error("An unknown error occured.\nException info is printed below.")
            logging.error(traceback.format_exc())

    def closeDatabase(self):
        """
        Сохраняет базу данных групп
        :return: none
        """
        try:
            self.cursor.close()
            self.connection.close()
        except Exception as e:
            logging.error("An unknown error occured.\nException info is printed below.")
            logging.error(traceback.format_exc())

    def append(self, user_id, reason="Причина не указана", duration=None):
        """
        Добавляет запись о новом заблокированном пользователе или обновляет существующую
        :param user_id: ИД пользователя
        :param reason: Причина бана. Если не указана, то будет подставлена причина по умолчанию.
        :param duration: Длительность бана в днях. Если не указана, считается вечным баном
        :return: none
        """
        unban_date = None
        if duration is not None:
            timezone = pytz.timezone("Europe/Moscow")
            unban_date = datetime.datetime.now(tz=timezone)
            delta = datetime.timedelta(days=duration)
            unban_date += delta
            unban_date = unban_date.replace(microsecond=0, tzinfo=None)

        insert_query = "INSERT OR REPLACE INTO black_list (user_id, reason, unban_date) VALUES (?, ?, ?)"
        data = (user_id, reason, str(unban_date))
        self.cursor.execute(insert_query, data)
        self.connection.commit()

    def hasUser(self, user_id):
        select_query = "SELECT * FROM black_list WHERE user_id = (?)"
        self.cursor.execute(select_query, (user_id,))
        res = self.cursor.fetchone()
        return res is not None

    def unban(self, user_id):
        if not self.hasUser(user_id):
            return
        delete_query = "DELETE FROM black_list WHERE user_id = (?)"
        self.cursor.execute(delete_query, (user_id, ))
        self.connection.commit()

    def getUser(self, user_id):
        if not self.hasUser(user_id):
            return
        select_query = "SELECT * FROM black_list WHERE user_id = (?)"
        self.cursor.execute(select_query, (user_id,))
        res = self.cursor.fetchone()
        return res


blacklistDatabaseEntity = BlackListDatabase(config.DATABASE_LOC)
