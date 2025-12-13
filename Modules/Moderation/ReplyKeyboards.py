from typing import Iterable

from telebot import types

def Start(moderators_names: Iterable[str]) -> types.ReplyKeyboardMarkup:
	"""
	Строит Reply-интерфейс: Список модераторов.

	:param moderators_names: Список имён модераторов.
	:type moderators_names: Iterable[str]
	:return: Reply-интерфейс.
	:rtype: types.ReplyKeyboardMarkup
	"""

	Menu = types.ReplyKeyboardMarkup(row_width = 1, resize_keyboard = True)
	for Element in moderators_names: Menu.add(types.KeyboardButton(Element))
	Menu.add(types.KeyboardButton("↩️ Назад"))

	return Menu