from aiogram import types
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.text import Const, Format
from aiogram.fsm.state import StatesGroup, State
from src.bot.i18n import get_text


class ActivationStates(StatesGroup):
    waiting_code = State()
    success = State()


async def on_code_input(message: types.Message, message_input: MessageInput, manager: DialogManager):
    config = manager.middleware_data.get("config")
    db = manager.middleware_data.get("db")
    service = manager.middleware_data.get("service")
    
    code = message.text.strip()
    if code != config.secret_code:
        await message.answer(get_text("invalid-code"))
        return
    
    telegram_id = message.from_user.id
    
    user_uuid = await service.get_or_create_user(telegram_id)
    db.add_user(telegram_id, user_uuid)
    
    sub_url = await service.get_subscription_url(user_uuid)
    await message.answer(
        f"{get_text('success-dialog')}\n\n<code>{sub_url}</code>",
        parse_mode="HTML"
    )
    await manager.switch_to(ActivationStates.success)


activation_dialog = Dialog(
    Window(
        Const(get_text("welcome")),
        MessageInput(on_code_input, content_types=types.ContentType.TEXT),
        state=ActivationStates.waiting_code,
    ),
    Window(
        Const(get_text("success-dialog")),
        state=ActivationStates.success,
    ),
)