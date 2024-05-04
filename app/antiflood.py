from aiogram import types, Dispatcher, BaseMiddleware
import aiogram.types.message
import bot


def on_flood():
    return None