import os
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).parent.parent


class BotConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(PROJECT_ROOT / ".env"))

    bot_token: str
    secret_code: str
    remnawave_api_url: str
    remnawave_api_key: str
    default_squad_name: str = "Default Squad"


class UserDatabase:
    def __init__(self, path: str = None):
        if path is None:
            path = PROJECT_ROOT / "users.toml"
        self.path = str(path)
        self.users: dict[str, str] = {}
        self._last_modified: float = 0
        self.load()

    def load(self):
        import toml
        if os.path.exists(self.path):
            self._last_modified = os.path.getmtime(self.path)
            with open(self.path, "r") as f:
                data = toml.load(f)
                self.users = {str(k): str(v) for k, v in data.get("users", {}).items()}

    def reload_if_changed(self):
        if not os.path.exists(self.path):
            return
        current_mtime = os.path.getmtime(self.path)
        if current_mtime != self._last_modified:
            self.load()

    def save(self):
        import toml
        with open(self.path, "w") as f:
            toml.dump({"users": self.users}, f)
        self._last_modified = os.path.getmtime(self.path)

    def get_user_uuid(self, telegram_id: int) -> Optional[str]:
        self.reload_if_changed()
        return self.users.get(str(telegram_id))

    def add_user(self, telegram_id: int, uuid: str):
        self.users[str(telegram_id)] = uuid
        self.save()

    def has_user(self, telegram_id: int) -> bool:
        self.reload_if_changed()
        return str(telegram_id) in self.users

    def remove_user(self, telegram_id: int):
        if str(telegram_id) in self.users:
            del self.users[str(telegram_id)]
            self.save()