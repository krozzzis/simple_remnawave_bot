import asyncio
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from loguru import logger
from aiogram import Bot, Dispatcher
from aiogram_dialog import setup_dialogs
from src.config_loader import BotConfig, UserDatabase
from remnawave import RemnawaveSDK
from src.remnawave_service import RemnawaveService
from src.bot.handlers import router as handlers_router
from src.bot.dialogs import activation_dialog


async def main():
    logger.info("Loading config...")
    config = BotConfig()
    logger.info(f"Config loaded: bot_token={config.bot_token[:10]}..., remnawave_api_url={config.remnawave_api_url}")
    
    logger.info("Loading database...")
    db = UserDatabase()
    logger.info(f"Database loaded: {len(db.users)} users")
    
    logger.info("Initializing Remnawave SDK...")
    sdk = RemnawaveSDK(
        base_url=config.remnawave_api_url,
        token=config.remnawave_api_key
    )
    service = RemnawaveService(sdk, config.default_squad_name)
    logger.info("Remnawave service initialized")
    
    logger.info("Initializing bot...")
    bot = Bot(token=config.bot_token)
    dp = Dispatcher()
    
    dp.include_router(handlers_router)
    dp.include_router(activation_dialog)
    setup_dialogs(dp)
    
    dp["config"] = config
    dp["db"] = db
    dp["service"] = service
    
    logger.info("Starting polling...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
