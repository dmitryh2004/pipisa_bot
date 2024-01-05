import os
import logging
import json
import traceback
import matplotlib.pyplot as plt

import config

'''
# Данные для диаграммы
labels = ['A', 'B', 'C', 'D']
sizes = [25, 30, 20, 25]

# Создание круговой диаграммы
plt.pie(sizes, labels=labels, autopct='%1.1f%%')

# Добавление легенды
plt.legend()

# Сохранение диаграммы в файл png
plt.savefig('pie_chart.png')

# Отображение диаграммы
plt.show()
'''


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
                logging.warning(f"Database {self.location} uploaded successfully.")
        except Exception as e:
            logging.error("An unknown error occured.\nException info is printed below.")
            logging.error(traceback.format_exc())

    def append(self, user_id, user_name):
        self.database[str(user_id)] = user_name

    def getUsername(self, user_id):
        for entry in self.database:
            if entry == str(user_id):
                return self.database[entry]


usernameDatabaseEntity = NameDatabase(config.USERNAME_DATABASE_LOC)
groupsDatabaseEntity = NameDatabase(config.GROUP_DATABASE_LOC)


class Database:
    database = dict()

    def __init__(self):
        self.readDatabase(config.DATABASE_LOC)

    def checkForNonExistingUser(self, group, user):
        if not(group in self.database):
            self.database[group] = dict()
            logging.warning("Added new group. Database's state: " + str(self.database))
        if not(user in self.database[group]):
            self.database[group][user] = dict()
            self.database[group][user]["current"] = "1"
            logging.warning("Added new user. Database's state: " + str(self.database))

    def getDimension(self, group, user, item):
        try:
            self.checkForNonExistingUser(group, user)
            value = None
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
                dimensions.append((dim, usernameDatabaseEntity.getUsername(user) if usernameDatabaseEntity.getUsername(user) else user))
        dimensions.sort(reverse=config.ITEMS_SORT_DIRECTION[item])
        if amount is not None:
            return dimensions[:amount]
        else:
            return dimensions

    def form_piechart_top_10(self, group, item):
        topall = self.get_top(group, item)
        group_name = groupsDatabaseEntity.getUsername(group) if groupsDatabaseEntity.getUsername(group) else group
        labels = []
        sizes = []
        total = 0
        for size, label in topall:  # создаем легенду и размеры
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

        file_path = f"generated\\{group}_{item}.png"
        plt.savefig(file_path)
        return file_path

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
                logging.warning("Dimensions database uploaded successfully.")
        except Exception as e:
            logging.error("An unknown error occured.\nException info is printed below.")
            logging.error(traceback.format_exc())


databaseEntity = Database()