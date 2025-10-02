from pathlib import Path

import i18n

locales_dir = Path(__file__).parent.parent / "locales"

print(locales_dir)

i18n.load_path.append(str(locales_dir))
i18n.set("filename_format", "{locale}.{format}")
i18n.set("skip_locale_root_data", True)
# i18n.set("use_locale_dirs", True)
i18n.set("fallback", "en")


def set_locale(locale: str) -> None:
    """Set the current locale for translations."""
    i18n.unload_everything()
    i18n.load_everything(locale=locale, lock=True)
    i18n.set("locale", locale)


_ = i18n.t
