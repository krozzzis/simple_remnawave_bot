from pathlib import Path

from fluentogram import TranslatorHub
from fluentogram.storage.file import FileStorage


def create_translator() -> TranslatorHub:
    storage = FileStorage(Path(__file__).parent.parent.parent / "locales" / "{locale}/")

    locales_map = {
        "ru": ("ru",),
    }

    return TranslatorHub(
        locales_map=locales_map,
        storage=storage,
        root_locale="ru",
    )


i18n = create_translator()


def get_text(key: str, **kwargs):
    return i18n.get_translator_by_locale("ru").get(key, **kwargs)