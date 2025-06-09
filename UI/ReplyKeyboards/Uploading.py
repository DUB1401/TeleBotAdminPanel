from ..InlineKeyboards.Uploading import UploadingInlineKeyboards
from ...Core.Uploading import Uploader

from dublib.TelebotUtils import UsersManager

from telebot import TeleBot, types

class UploadingReplyFunctions:
	"""Набор функций обработки Reply-кнопок: выгрузка."""

	def Uploading(bot: TeleBot, users: UsersManager, message: types.Message):
		"""
		Обрабатывает Reply-кнопку: 📤 Выгрузка
			bot – бот Telegram;\n
			users – менеджер пользователей;\n
			message – сообщение от пользователя.
		"""

		Text = (
			"<b>📤 Выгрузка</b>\n",
			"Нажмите на одну из кнопок ниже, чтобы получить файл."
		)

		bot.send_message(
			chat_id = message.chat.id,
			text = "\n".join(Text),
			parse_mode = "HTML",
			reply_markup = UploadingInlineKeyboards.files()
		)