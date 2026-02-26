from .Enums import Actions

from typing import TYPE_CHECKING

from telebot import types

if TYPE_CHECKING:
	from . import MailingData

	from dublib.TelebotUtils.Users import UserData

def Start(module_data: "MailingData") -> types.ReplyKeyboardMarkup:
	"""
	Строит Reply-интерфейс: главное меню.

	:param module_data: Данные модуля.
	:type module_data: MailingData
	:return: Reply-разметка.
	:rtype: types.ReplyKeyboardMarkup
	"""

	Menu = types.ReplyKeyboardMarkup(row_width = 1, resize_keyboard = True)

	ButtonText = "Удалить" if module_data.button_link else "Добавить"
	Status = "🟢 Запустить"

	match module_data.action:

		case Actions.Mailing:
			Status = "🟡 Приостановить"
			Menu.add(types.KeyboardButton("🔴 Отменить"))

		case Actions.StopMailing:
			Status = "🟢 Возобновить"
	
	Menu.add(types.KeyboardButton(Status))
	Menu.add(types.KeyboardButton("🔎 Просмотр"))

	if module_data.action != Actions.Mailing: 
		Menu.add(types.KeyboardButton("✏️ Редактировать"))
		Menu.add(types.KeyboardButton(f"🕹️ {ButtonText} кнопку"))
		
	Menu.add(types.KeyboardButton("↩️ Назад"))

	return Menu

def Save() -> types.ReplyKeyboardMarkup:
	"""Строит Reply-интерфейс: сохранение сообщения."""

	Menu = types.ReplyKeyboardMarkup(row_width = 1, resize_keyboard = True)
	Menu.add(types.KeyboardButton("💾 Сохранить"))

	return Menu