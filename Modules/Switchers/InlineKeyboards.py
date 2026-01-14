from telebot import types

from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from . import Flag

def FlagsSwitchers(flags: "dict[str, Flag]"):
	"""Строит Inline-интерфейс: список флагов."""

	Menu = types.InlineKeyboardMarkup()

	for CurrentFlag in flags.values():
		StatusEmoji = "🟢" if CurrentFlag.value else "🔴"
		Buffer = types.InlineKeyboardButton(f"{StatusEmoji} {CurrentFlag.label}", callback_data = f"ap_switch_{CurrentFlag.id}")
		Menu.add(Buffer)
	
	return Menu