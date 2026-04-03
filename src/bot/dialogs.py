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
    if code not in config.codes_list:
        await message.answer(get_text("invalid-code"))
        return
    
    telegram_id = message.from_user.id
    first_name = message.from_user.first_name
    username = message.from_user.username
    
    user_uuid = await service.get_or_create_user(telegram_id, first_name, username, code)
    db.add_user(telegram_id, user_uuid, code)
    
    sub_url = await service.get_subscription_url(user_uuid)
    manager.dialog_data["sub_url"] = sub_url
    await manager.switch_to(ActivationStates.success)


async def get_success_data(dialog_manager: DialogManager, **kwargs):
    return {
        "success_dialog_text": get_text("success-dialog"),
        "sub_url": dialog_manager.dialog_data.get("sub_url", "")
    }


activation_dialog = Dialog(
    Window(
        Const(get_text("welcome")),
        MessageInput(on_code_input, content_types=types.ContentType.TEXT),
        state=ActivationStates.waiting_code,
    ),
    Window(
        Format("{success_dialog_text}\n\n<code>{sub_url}</code>"),
        state=ActivationStates.success,
        getter=get_success_data,
        parse_mode="HTML"
    ),
)