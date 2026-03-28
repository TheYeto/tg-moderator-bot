import asyncio
import logging

from aiogram import Bot, Dispatcher

from bot.config import Settings
from bot.handlers.join_cleanup import router as join_cleanup_router


async def main() -> None:
    settings = Settings.from_env()

    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    )
    logger = logging.getLogger(__name__)

    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()

    dp.include_router(join_cleanup_router)

    logger.info("Bot starting, polling for updates...")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
