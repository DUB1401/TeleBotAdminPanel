from ..InlineKeyboards.Moderation import ModerationInlineKeyboards
from ...Core.Moderation import Moderator

from dublib.TelebotUtils import UsersManager

from telebot import TeleBot, types

class ModerationReplyFunctions:
	"""Набор функций обработки Reply-кнопок: модерация."""

	def Moderation(bot: TeleBot, users: UsersManager, message: types.Message):
		"""
		Обрабатывает Reply-кнопку: 🛡️ Модерация
			bot – бот Telegram;\n
			users – менеджер пользователей;\n
			message – сообщение от пользователя.
		"""

		LENGTH = Moderator.get_content_length()

		Text = (
			"<b>🛡️ Модерация</b>\n",
			f"Элементов: {LENGTH}" if LENGTH else "Элементы для модерации отсутствуют."
		)

		bot.send_message(
			chat_id = message.chat.id,
			text = "\n".join(Text),
			parse_mode = "HTML",
			reply_markup = ModerationInlineKeyboards.moderation_start()
		)