from loguru import logger

from aiogram import Router, types
from aiogram.filters import Command
from aiogram_dialog import DialogManager, StartMode
from src.bot.dialogs import ActivationStates
from src.bot.i18n import get_text

router = Router()


@router.message(Command("start"))
async def start(message: types.Message, dialog_manager: DialogManager):
    logger.info(f"Received /start from user {message.from_user.id}")
    db = dialog_manager.middleware_data.get("db")
    telegram_id = message.from_user.id
    
    if db.has_user(telegram_id):
        await message.answer(get_text("already-active"))
    else:
        await dialog_manager.start(ActivationStates.waiting_code, mode=StartMode.RESET_STACK)


@router.message(Command("sub"))
async def sub_command(message: types.Message, dialog_manager: DialogManager):
    logger.info(f"Received /sub from user {message.from_user.id}")
    db = dialog_manager.middleware_data.get("db")
    service = dialog_manager.middleware_data.get("service")
    telegram_id = message.from_user.id
    
    user_uuid = db.get_user_uuid(telegram_id)
    if user_uuid:
        try:
            sub_url = await service.get_subscription_url(user_uuid)
            text = f"{get_text('sub-link')}\n\n<code>{sub_url}</code>"
            await message.answer(text, parse_mode="HTML")
        except Exception as e:
            logger.error(f"Error getting subscription URL: {e}")
            db.remove_user(telegram_id)
            await message.answer(get_text("no-subscription"))
    else:
        await message.answer(get_text("no-subscription"))


@router.message(Command("help"))
async def help_command(message: types.Message, dialog_manager: DialogManager):
    logger.info(f"Received /help from user {message.from_user.id}")
    await message.answer(get_text("help"))
