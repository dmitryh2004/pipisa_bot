import asyncio

import config
import database
from app import bot


async def main() -> None:  # сам бот
    await bot.dp.start_polling(bot.bot)
    bot.dp.stop_polling()
    await bot.dp.wait_closed()
    await bot.bot.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except asyncio.CancelledError:
        pass
