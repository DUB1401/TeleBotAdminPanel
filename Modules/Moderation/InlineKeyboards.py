from telebot import types

def Editable():
	"""Строит Inline-интерфейс: просмотр элемента модерации с возможностью редактирования."""

	Menu = types.InlineKeyboardMarkup()
	Deny = types.InlineKeyboardButton("❌ Отклонить", callback_data = "ap_moderate_false")
	Accept = types.InlineKeyboardButton("✅ Принять", callback_data = "ap_moderate_true")
	Edit = types.InlineKeyboardButton("✍️ Изменить", callback_data = "ap_edit")
	Menu.add(Deny, Accept, Edit, row_width = 2)

	return Menu

def View():
	"""Строит Inline-интерфейс: просмотр элемента модерации."""

	Menu = types.InlineKeyboardMarkup(row_width = 2)
	Previous = types.InlineKeyboardButton("⬅️ Назад", callback_data = "ap_previous")
	Next = types.InlineKeyboardButton("Вперёд ➡️", callback_data = "ap_next")
	Modearate = types.InlineKeyboardButton("❌ Удалить", callback_data = "ap_moderate")
	Menu.add(Previous, Next, Modearate)

	return Menu