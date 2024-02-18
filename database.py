import datetime
import os
import logging
import json
import traceback
import matplotlib.pyplot as plt

import config


class NameDatabase:
    database = dict()
    location = ""

    def __init__(self, location):
        self.location = location
        self.readDatabase(self.location)

    def readDatabase(self, location):
        try:
            with open(location, "r", encoding="utf-8") as file:
                self.database = json.load(file)
        except FileNotFoundError:
            logging.error(f"Database {location} not found!")
        except Exception as e:
            logging.error("An unknown error occured.\nException info is printed below.")
            logging.error(traceback.format_exc())

    def saveDatabase(self):
        try:
            with open(self.location, "w", encoding="utf-8") as file:
                json.dump(self.database, file)
                logging.info(f"Database {self.location} uploaded successfully.")
        except Exception as e:
            logging.error("An unknown error occured.\nException info is printed below.")
            logging.error(traceback.format_exc())

    def append(self, user_id, user_name):
        self.database[str(user_id)] = user_name

    def getName(self, user_id):
        for entry in self.database:
            if entry == str(user_id):
                return self.database[entry]


groupsDatabaseEntity = NameDatabase(config.GROUP_DATABASE_LOC)


class UserDatabase:
    database = dict()
    location = ""

    def __init__(self, location):
        self.location = location
        self.readDatabase(self.location)

    def readDatabase(self, location):
        try:
            with open(location, "r", encoding="utf-8") as file:
                self.database = json.load(file)
        except FileNotFoundError:
            logging.error(f"Database {location} not found!")
        except Exception as e:
            logging.error("An unknown error occured.\nException info is printed below.")
            logging.error(traceback.format_exc())

    def saveDatabase(self):
        try:
            with open(self.location, "w", encoding="utf-8") as file:
                json.dump(self.database, file)
                logging.info(f"Database {self.location} uploaded successfully.")
        except Exception as e:
            logging.error("An unknown error occured.\nException info is printed below.")
            logging.error(traceback.format_exc())

    def append(self, user_id, user_name, role=0):
        if not (str(user_id) in self.database):
            self.database[str(user_id)] = dict()
        self.database[str(user_id)]["name"] = user_name
        self.database[str(user_id)]["role"] = role

    def getUsername(self, user_id):
        for entry in self.database:
            if entry == str(user_id):
                return self.database[entry]["name"]

    def getUserRole(self, user_id):
        for entry in self.database:
            if entry == str(user_id):
                return int(self.database[entry]["role"])
        return 0


usernameDatabaseEntity = UserDatabase(config.USERNAME_DATABASE_LOC)


class PromoDatabase:
    database = dict()
    location = ""

    def __init__(self, location):
        self.location = location
        self.readDatabase(self.location)

    def readDatabase(self, location):
        try:
            with open(location, "r", encoding="utf-8") as file:
                self.database = json.load(file)
        except FileNotFoundError:
            logging.error(f"Database {location} not found!")
        except Exception as e:
            logging.error("An unknown error occured.\nException info is printed below.")
            logging.error(traceback.format_exc())

    def saveDatabase(self):
        try:
            with open(self.location, "w", encoding="utf-8") as file:
                json.dump(self.database, file)
                logging.info(f"Database {self.location} uploaded successfully.")
        except Exception as e:
            logging.error("An unknown error occured.\nException info is printed below.")
            logging.error(traceback.format_exc())

    def setPromo(self, promo_id, bonus_size, max_uses, min_role):
        if not (str(promo_id) in self.database):
            self.database[str(promo_id)] = dict()
        self.database[str(promo_id)]["bonus"] = bonus_size
        self.database[str(promo_id)]["max_uses"] = max_uses
        self.database[str(promo_id)]["min_role"] = min_role

    def getPromoBonus(self, promo_id):
        for entry in self.database:
            if entry == str(promo_id):
                return self.database[entry]["bonus"]

    def getPromoMaxUses(self, promo_id):
        for entry in self.database:
            if entry == str(promo_id):
                return self.database[entry]["max_uses"]

    def getPromoMinRole(self, promo_id):
        for entry in self.database:
            if entry == str(promo_id):
                return self.database[entry]["min_role"]


promoDatabaseEntity = PromoDatabase("promos.json")


class Database:
    database = dict()

    def __init__(self):
        self.readDatabase(config.DATABASE_LOC)

    def checkForNonExistingUser(self, group, user):
        if not (group in self.database):
            self.database[group] = dict()
            logging.info("Added new group. Database's state: " + str(self.database))
        if not (user in self.database[group]):
            self.database[group][user] = dict()
            self.database[group][user]["current"] = "1"
            self.database[group][user]["promo_usages"] = dict()
            logging.info("Added new user. Database's state: " + str(self.database))

    def checkForExistingPromoUsages(self, group, user):
        self.checkForNonExistingUser(group, user)
        if not ("promo_usages" in self.database[group][user]):
            self.database[group][user]["promo_usages"] = dict()

    def checkForExistingAttempts(self, group, user):
        self.checkForNonExistingUser(group, user)
        if not ("attempts" in self.database[group][user]):
            self.database[group][user]["attempts"] = dict()
            for item in config.ITEMS:
                self.database[group][user]["attempts"][item] = str(datetime.datetime(2000, 1, 1))

    def checkForExistingBonuses(self, group, user):
        self.checkForNonExistingUser(group, user)
        if not ("bonuses" in self.database[group][user]):
            self.database[group][user]["bonuses"] = dict()
            for item in config.ITEMS:
                self.database[group][user]["bonuses"][item] = 0

    def getBonus(self, group, user, item):
        try:
            self.checkForExistingBonuses(group, user)
            return self.database[group][user]["bonuses"][item]
        except Exception as e:
            logging.error("An unknown error occured.\nException info is printed below.")
            logging.error(traceback.format_exc())

    def useBonus(self, group, user, item):
        try:
            self.checkForExistingBonuses(group, user)
            self.database[group][user]["bonuses"][item] = 0
        except Exception as e:
            logging.error("An unknown error occured.\nException info is printed below.")
            logging.error(traceback.format_exc())

    def getDimension(self, group, user, item):
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
        try:
            self.checkForNonExistingUser(group, user)
            self.database[group][user][item] = value
        except Exception as e:
            logging.error("An unknown error occured.\nException info is printed below.")
            logging.error(traceback.format_exc())

    def getLastAttempt(self, group, user, item):
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
        try:
            self.checkForNonExistingUser(group, user)
            self.checkForExistingAttempts(group, user)
            attempt: datetime.datetime = datetime.datetime.now().replace(microsecond=0)
            if "attempts" in self.database[group][user]:
                if item in self.database[group][user]["attempts"]:
                    self.database[group][user]["attempts"][item] = str(attempt)
        except Exception as e:
            logging.error("An unknown error occured.\nException info is printed below.")
            logging.error(traceback.format_exc())

    def getCurrent(self, group, user):
        try:
            self.checkForNonExistingUser(group, user)
            value = self.database[group][user]["current"]
            return value
        except Exception as e:
            logging.error("An unknown error occured.\nException info is printed below.")
            logging.error(traceback.format_exc())

    def setCurrent(self, group, user, value):
        try:
            self.checkForNonExistingUser(group, user)
            self.database[group][user]["current"] = value
        except Exception as e:
            logging.error("An unknown error occured.\nException info is printed below.")
            logging.error(traceback.format_exc())

    def get_top(self, group, item, amount=None):
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
        try:
            with open(location, "r", encoding="utf-8") as file:
                self.database = json.load(file)
        except FileNotFoundError:
            logging.error(f"Database {location} not found!")
        except Exception as e:
            logging.error("An unknown error occured.\nException info is printed below.")
            logging.error(traceback.format_exc())

    def saveDatabase(self, location):
        try:
            with open(location, "w", encoding="utf-8") as file:
                json.dump(self.database, file)
                logging.info("Dimensions database uploaded successfully.")
        except Exception as e:
            logging.error("An unknown error occured.\nException info is printed below.")
            logging.error(traceback.format_exc())


databaseEntity = Database()
