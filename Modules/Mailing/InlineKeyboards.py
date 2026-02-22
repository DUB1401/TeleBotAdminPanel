from telebot import types

def Cancel():
	"""Строит Inline-интерфейс: отмена текущего действия."""

	Menu = types.InlineKeyboardMarkup()
	Menu.add(types.InlineKeyboardButton("🚫 Отмена", callback_data = "ap_cancel"))

	return Menu

def Resume():
	"""Строит Inline-интерфейс: возобновление рассылки."""

	Menu = types.InlineKeyboardMarkup()
	Menu.add(types.InlineKeyboardButton("🚫 Отмена", callback_data = "ap_mailing_cancel"))
	Menu.add(types.InlineKeyboardButton("▶️ Возобновить", callback_data = "ap_mailing_resume"))

	return Menu