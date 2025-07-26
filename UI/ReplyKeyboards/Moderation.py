from ..InlineKeyboards.Moderation import ModerationInlineKeyboards
from ...Core.Moderation import Moderator, ModeratorsStorage

from dublib.TelebotUtils import UsersManager

from telebot import TeleBot, types

class ModerationReplyKeyboards:
	"""Генератор Reply-интерфейса."""

	def moderators() -> types.ReplyKeyboardMarkup:
		"""Строит кнопочный интерфейс: модераторы."""

		Menu = types.ReplyKeyboardMarkup(resize_keyboard = True)
		for ModeratorName in ModeratorsStorage.get_names(): Menu.add(types.KeyboardButton(ModeratorName), row_width = 1)
		Back = types.KeyboardButton("↩️ Назад")
		Menu.add(Back, row_width = 1)

		return Menu

class ModerationReplyFunctions:
	"""Набор функций обработки Reply-кнопок: модерация."""

	def Moderation(bot: TeleBot, users: UsersManager, message: types.Message):
		"""
		Обрабатывает Reply-кнопку: 🛡️ Модерация
			bot – бот Telegram;\n
			users – менеджер пользователей;\n
			message – сообщение от пользователя.
		"""

		bot.send_message(
			chat_id = message.chat.id,
			text = "Выберите модерируемый контент.",
			parse_mode = "HTML",
			reply_markup = ModerationReplyKeyboards.moderators()
		)

	def ShowModerationCategory(bot: TeleBot, users: UsersManager, message: types.Message, name: str):
		"""
		Запускает модератор.

		:param bot: Бот Telegram.
		:type bot: TeleBot
		:param users: Менеджер пользователей.
		:type users: UsersManager
		:param message: Сообщение от пользователя.
		:type message: types.Message
		:param name: Имя модератора.
		:type name: str
		"""

		LENGTH = ModeratorsStorage.get_moderator_by_name(name).items_count

		Text = (
			"<b>🛡️ Модерация</b>\n",
			f"В категории <i>{name}</i> записей: {LENGTH}." if LENGTH else f"В категории <i>{name}</i> записи отсутствуют."
		)

		bot.send_message(
			chat_id = message.chat.id,
			text = "\n".join(Text),
			parse_mode = "HTML",
			reply_markup = ModerationInlineKeyboards.moderation_start(name)
		)