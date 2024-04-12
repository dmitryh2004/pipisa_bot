import datetime
import os
import logging
import json
import traceback
import matplotlib.pyplot as plt
import pytz

import config


class NameDatabase:
    """
    Класс базы данных с названиями групп
    """
    database = dict()
    location = ""

    def __init__(self, location):
        self.location = location
        self.readDatabase(self.location)

    def readDatabase(self, location):
        """
        Чтение базы данных групп
        :param location: путь к базе данных групп
        :return: none
        """
        try:
            with open(location, "r", encoding="utf-8") as file:
                self.database = json.load(file)
        except FileNotFoundError:
            logging.error(f"Database {location} not found!")
        except Exception as e:
            logging.error("An unknown error occured.\nException info is printed below.")
            logging.error(traceback.format_exc())

    def saveDatabase(self):
        """
        Сохраняет базу данных групп
        :return: none
        """
        try:
            with open(self.location, "w", encoding="utf-8") as file:
                json.dump(self.database, file)
                logging.info(f"Database {self.location} uploaded successfully.")
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
        self.database[str(group_id)] = group_name

    def getName(self, group_id):
        """
        Возвращает имя группы по id
        :param group_id: ИД группы
        :return: название группы
        """
        for entry in self.database:
            if entry == str(group_id):
                return self.database[entry]


groupsDatabaseEntity = NameDatabase(config.GROUP_DATABASE_LOC)


class UserDatabase:
    """
    Класс базы данных о пользователях: их именах и ролях
    """
    database = dict()
    location = ""

    def __init__(self, location):
        self.location = location
        self.readDatabase(self.location)

    def readDatabase(self, location):
        """
        Чтение базы данных пользователей
        :param location: путь к файлу базы данных пользователей
        :return: none
        """
        try:
            with open(location, "r", encoding="utf-8") as file:
                self.database = json.load(file)
        except FileNotFoundError:
            logging.error(f"Database {location} not found!")
        except Exception as e:
            logging.error("An unknown error occured.\nException info is printed below.")
            logging.error(traceback.format_exc())

    def saveDatabase(self):
        """
        Сохраняет базу данных групп
        :return: none
        """
        try:
            with open(self.location, "w", encoding="utf-8") as file:
                json.dump(self.database, file)
                logging.info(f"Database {self.location} uploaded successfully.")
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
        if not (str(user_id) in self.database):
            self.database[str(user_id)] = dict()
        self.database[str(user_id)]["name"] = user_name
        self.database[str(user_id)]["role"] = role

    def getUsername(self, user_id):
        """
        Возвращает имя пользователя по ИД
        :param user_id: ИД пользователя
        :return: Имя пользователя
        """
        for entry in self.database:
            if entry == str(user_id):
                return self.database[entry]["name"]

    def getUserRole(self, user_id):
        """
        Возвращает роль пользователя по ИД
        :param user_id: ИД пользователя
        :return: Роль пользователя
        """
        print(self.database)
        for entry in self.database:
            if entry == str(user_id):
                print(self.database[entry])
                return int(self.database[entry]["role"])
        return 0


usernameDatabaseEntity = UserDatabase(config.USERNAME_DATABASE_LOC)


class PromoDatabase:
    """
    Класс базы данных промокодов
    """
    database = dict()
    location = ""

    def __init__(self, location):
        self.location = location
        self.readDatabase(self.location)

    def readDatabase(self, location):
        """
        Чтение базы данных пользователей
        :param location: путь к файлу базы данных пользователей
        :return: none
        """
        try:
            with open(location, "r", encoding="utf-8") as file:
                self.database = json.load(file)
        except FileNotFoundError:
            logging.error(f"Database {location} not found!")
        except Exception as e:
            logging.error("An unknown error occured.\nException info is printed below.")
            logging.error(traceback.format_exc())

    def saveDatabase(self):
        """
        Сохраняет базу данных групп
        :return: none
        """
        try:
            with open(self.location, "w", encoding="utf-8") as file:
                json.dump(self.database, file)
                logging.info(f"Database {self.location} uploaded successfully.")
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
        if not (str(promo_id) in self.database):
            self.database[str(promo_id)] = dict()
        self.database[str(promo_id)]["bonus"] = bonus_size
        self.database[str(promo_id)]["max_uses"] = max_uses
        self.database[str(promo_id)]["min_role"] = min_role

    def getPromos(self):
        """
        Возвращает список всех промокодов из базы данных
        :return: строка с информацией о всех промокодах
        """
        res = []
        for key in self.database:
            value = self.database[key]
            temp = f"{key}: бонус - {value['bonus']}, максимальное число использований - {value['max_uses']}," \
                   f" минимальная роль для использования - {config.ROLES[value['min_role']][0]}"
            res.append(temp)
        return "\n".join(res)

    def getPromoBonus(self, promo_id):
        """
        Возвращает бонус промокода по его ID
        :param promo_id: ID промокода
        :return: бонус промокода
        """
        for entry in self.database:
            if entry == str(promo_id):
                return self.database[entry]["bonus"]

    def getPromoMaxUses(self, promo_id):
        """
        Возвращает максимальное число использований промокода по его ID
        :param promo_id: ID промокода
        :return: максимальное число использований промокода
        """
        for entry in self.database:
            if entry == str(promo_id):
                return self.database[entry]["max_uses"]

    def getPromoMinRole(self, promo_id):
        """
        Возвращает минимальную роль, необходимую для использования промокода, по его ID
        :param promo_id: ID промокода
        :return: минимальная роль, необходимая для использования
        """
        for entry in self.database:
            if entry == str(promo_id):
                return self.database[entry]["min_role"]


promoDatabaseEntity = PromoDatabase(config.PROMO_DATABASE_LOC)


class Database:
    """
    Класс базы данных измерений
    """
    database = dict()

    def __init__(self):
        self.readDatabase(config.DATABASE_LOC)

    def checkForNonExistingUser(self, group, user):
        """
        Проверка на существование пользователя и группы в базе данных
        :param group: Группа, которую надо проверить
        :param user: Пользователь, которого надо проверить
        :return: none
        """
        if not (group in self.database):
            self.database[group] = dict()
            logging.info("Added new group. Database's state: " + str(self.database))
        if not (user in self.database[group]):
            self.database[group][user] = dict()
            self.database[group][user]["current"] = "1"
            self.database[group][user]["promo_usages"] = dict()
            logging.info("Added new user. Database's state: " + str(self.database))

    def checkForExistingPromoUsages(self, group, user):
        """
        Проверка на существующую информацию о промокодах, использованных пользователем в группе
        :param group: Группа, которую надо проверить
        :param user: Пользователь, которого надо проверить
        :return: none
        """
        self.checkForNonExistingUser(group, user)
        if not ("promo_usages" in self.database[group][user]):
            self.database[group][user]["promo_usages"] = dict()

    def checkForExistingAttempts(self, group, user):
        """
        Проверка на существование информации о попытках пользователя увеличить измерения
        :param group: Группа, которую надо проверить
        :param user: Пользователь, которого надо проверить
        :return: none
        """
        self.checkForNonExistingUser(group, user)
        if not ("attempts" in self.database[group][user]):
            self.database[group][user]["attempts"] = dict()
            for item in config.ITEMS:
                self.database[group][user]["attempts"][item] = str(datetime.datetime(2000, 1, 1))

    def checkForExistingBonuses(self, group, user):
        """
        Проверка на существование информации о примененных бонусах к измерениям
        :param group: Группа, которую надо проверить
        :param user: Пользователь, которого надо проверить
        :return: none
        """
        self.checkForNonExistingUser(group, user)
        if not ("bonuses" in self.database[group][user]):
            self.database[group][user]["bonuses"] = dict()
            for item in config.ITEMS:
                self.database[group][user]["bonuses"][item] = 0

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
            return self.database[group][user]["bonuses"][item]
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
            self.database[group][user]["bonuses"][item] = 0
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
            value = config.ITEMS_START_VALUE[item]
            if item in self.database[group][user]:
                value = self.database[group][user][item]
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
            self.database[group][user][item] = value
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
            self.checkForNonExistingUser(group, user)
            self.checkForExistingAttempts(group, user)
            attempt: datetime.datetime = datetime.datetime(2000, 1, 1)
            if "attempts" in self.database[group][user]:
                if item in self.database[group][user]["attempts"]:
                    attempt = datetime.datetime.strptime(self.database[group][user]["attempts"][item],
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
            self.checkForNonExistingUser(group, user)
            self.checkForExistingAttempts(group, user)
            timezone = pytz.timezone("Europe/Moscow")
            attempt: datetime.datetime = datetime.datetime.now(timezone).replace(microsecond=0).replace(tzinfo=None)
            if "attempts" in self.database[group][user]:
                if item in self.database[group][user]["attempts"]:
                    self.database[group][user]["attempts"][item] = str(attempt)
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
            value = self.database[group][user]["current"]
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
            self.database[group][user]["current"] = value
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
        dimensions = []
        for user in self.database[group]:
            dim = self.getDimension(group, user, item)
            if dim is not None:
                dimensions.append((dim, usernameDatabaseEntity.getUsername(user) if usernameDatabaseEntity.getUsername(
                    user) else user))
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
        group_name = groupsDatabaseEntity.getName(group) if groupsDatabaseEntity.getName(group) else group
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
            self.checkForExistingPromoUsages(group, user)
            val = 0
            if promo in self.database[group][user]["promo_usages"]:
                val = self.database[group][user]["promo_usages"][promo]
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
            self.checkForExistingPromoUsages(group, user)
            message = ""
            success = False
            if promo in self.database[group][user]["promo_usages"]:
                self.database[group][user]["promo_usages"][promo] += 1
            else:
                self.database[group][user]["promo_usages"][promo] = 1
            self.checkForExistingBonuses(group, user)
            if self.database[group][user]["promo_usages"][promo] <= promoDatabaseEntity.getPromoMaxUses(promo):
                if usernameDatabaseEntity.getUserRole(user) >= promoDatabaseEntity.getPromoMinRole(promo):
                    self.database[group][user]["bonuses"][self.getCurrent(group, user)] += promoDatabaseEntity.getPromoBonus(promo)
                    message = "Промокод " + str(promo) + " успешно активирован. При следующей попытке роста в группе " + groupsDatabaseEntity.getName(group) + \
                        " к измерению " + config.ITEMS_LOC[self.getCurrent(group, user)] + " будет добавлено " + str(promoDatabaseEntity.getPromoBonus(promo)) + " см.\n" \
                        "Число использований промокода: " + str(self.database[group][user]["promo_usages"][promo]) + " / " + str(promoDatabaseEntity.getPromoMaxUses(promo))
                    success = True
                else:
                    message = "Этот промокод вам недоступен. Причина: ваших прав недостаточно для использования данного промокода (требуется роль " + \
                        config.ROLES[promoDatabaseEntity.getPromoMinRole(promo)][0] + " или выше)."
                    self.database[group][user]["promo_usages"][promo] -= 1
            else:
                self.database[group][user]["promo_usages"][promo] -= 1
                message = "Этот промокод вам недоступен. Причина: превышено максимальное число использований (" + \
                          str(self.database[group][user]["promo_usages"][promo]) + " / " + str(promoDatabaseEntity.getPromoMaxUses(promo)) + ")."
            return success, message
        except Exception as e:
            logging.error("An unknown error occured.\nException info is printed below.")
            logging.error(traceback.format_exc())

    def readDatabase(self, location):
        """
        Считывает базу данных измерений
        :param location: Путь к файлу базы данных
        :return: none
        """
        try:
            with open(location, "r", encoding="utf-8") as file:
                self.database = json.load(file)
        except FileNotFoundError:
            logging.error(f"Database {location} not found!")
        except Exception as e:
            logging.error("An unknown error occured.\nException info is printed below.")
            logging.error(traceback.format_exc())

    def saveDatabase(self, location):
        """
        Сохраняет базу данных измерений
        :param location: Путь к файлу базы данных
        :return: none
        """
        try:
            with open(location, "w", encoding="utf-8") as file:
                json.dump(self.database, file)
                logging.info(f"Database {location} uploaded successfully.")
        except Exception as e:
            logging.error("An unknown error occured.\nException info is printed below.")
            logging.error(traceback.format_exc())


databaseEntity = Database()
