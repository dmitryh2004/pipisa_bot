import os
import logging
import json
import traceback

import config


class UsernameDatabase:
    database = dict()

    def __init__(self):
        self.readDatabase(config.USERNAME_DATABASE_LOC)

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
                logging.warning("Usernames database uploaded successfully.")
        except Exception as e:
            logging.error("An unknown error occured.\nException info is printed below.")
            logging.error(traceback.format_exc())

    def append(self, user_id, user_name):
        self.database[str(user_id)] = user_name

    def getUsername(self, user_id):
        for entry in self.database:
            if entry == str(user_id):
                return self.database[entry]


usernameDatabaseEntity = UsernameDatabase()


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

    def get_top_10(self, group, item):
        dimensions = []
        for user in self.database[group]:
            dimensions.append((self.getDimension(group, user, item),
                        usernameDatabaseEntity.getUsername(user) if usernameDatabaseEntity.getUsername(user) else user))
        dimensions.sort(reverse=config.ITEMS_SORT_DIRECTION[item])
        return dimensions[:10]

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