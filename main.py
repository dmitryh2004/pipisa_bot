import asyncio

import config
import logging
import os
from app import bot


AUTOSAVE_INTERVAL = 300  # 5 минут


def save():
    """
    Функция для сохранения баз данных бота
    :return: none
    """
    logging.info('Autosaving...')
    # выгрузка базы данных
    bot.db.saveDatabase(config.DATABASE_LOC)
    bot.udb.saveDatabase()
    bot.gdb.saveDatabase()
    bot.pdb.saveDatabase()
    logging.info('Autosaving successful.')
    # удалить все сгенерированные файлы
    logging.info('Deleting generated files...')
    generated_dir = 'generated'
    for f in os.listdir(generated_dir):
        os.remove(os.path.join(generated_dir, f))
    logging.info('Deletion complete.')


async def autosave() -> None:  # автосохранение, удаление сгенерированных файлов
    """
    Функция для автосохранения: запускается параллельно с ботом в функции __main__
    :return: none
    """
    while True:
        save()
        await asyncio.sleep(AUTOSAVE_INTERVAL)


async def run_bot() -> None:  # сам бот
    """
    Функция для запуска бота
    :return: none
    """
    await bot.dp.start_polling(bot.bot, polling_timeout=24*60*60)
    bot.dp.stop_polling()
    await bot.dp.wait_closed()
    await bot.bot.close()


if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        main_task = loop.create_task(run_bot())
        autosave_task = loop.create_task(autosave())
        loop.run_until_complete(main_task)
        loop.stop()
        loop.close()
    except asyncio.CancelledError:
        pass
    except KeyboardInterrupt:
        save()
        logging.warning("Bot stopped by keyboard interrupt")