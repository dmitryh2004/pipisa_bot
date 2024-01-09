import asyncio

import config
import logging
import os
from app import bot


AUTOSAVE_INTERVAL = 300  # 5 минут


async def autosave() -> None:  # автосохранение, удаление сгенерированных файлов
    while True:
        logging.warning('Autosaving...')
        # выгрузка базы данных
        bot.db.saveDatabase(config.DATABASE_LOC)
        bot.udb.saveDatabase()
        bot.gdb.saveDatabase()
        logging.warning('Autosaving successful.')
        # удалить все сгенерированные файлы
        logging.warning('Deleting generated files...')
        generated_dir = 'generated'
        for f in os.listdir(generated_dir):
            os.remove(os.path.join(generated_dir, f))
        logging.warning('Deletion complete.')
        await asyncio.sleep(AUTOSAVE_INTERVAL)


async def main() -> None:  # сам бот
    await bot.dp.start_polling(bot.bot)
    bot.dp.stop_polling()
    await bot.dp.wait_closed()
    await bot.bot.close()


if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        main_task = loop.create_task(main())
        autosave_task = loop.create_task(autosave())
        loop.run_until_complete(main_task)
        loop.stop()
        loop.close()
    except asyncio.CancelledError:
        pass
