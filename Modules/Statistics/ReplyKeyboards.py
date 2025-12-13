from telebot import types

def Start() -> types.ReplyKeyboardMarkup:
	"""Строит Reply-интерфейс: главное меню."""

	Menu = types.ReplyKeyboardMarkup(row_width = 1, resize_keyboard = True)
	Menu.add(types.KeyboardButton("📊 Отобразить"))
	Menu.add(types.KeyboardButton("↩️ Назад"))

	return Menu