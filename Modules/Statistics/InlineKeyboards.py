from telebot import types

def Extract():
	"""Строит Inline-интерфейс: выгрузка."""

	Menu = types.InlineKeyboardMarkup()
	Extract = types.InlineKeyboardButton("Выгрузить", callback_data = "ap_extract")
	Menu.add(Extract)

	return Menu