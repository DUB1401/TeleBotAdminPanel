from ..UI.ReplyKeyboards import MailingReplyKeyboards

from dublib.TelebotUtils import UserData, UsersManager
from dublib.TelebotUtils.Master import Decorators

from threading import Thread
import random

from telebot import TeleBot, types

class Mailer:
	"""Рассыльщик."""

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __BuildButton(self, text: str, link: str) -> types.InlineKeyboardButton:
		"""
		Создаёт кнопку-ссылку.
			text – подпись кнопки;
			link – ссылка.
		"""

		Markup = types.InlineKeyboardMarkup()
		if text and link: Markup.add(types.InlineKeyboardButton(text, link))

		return Markup

	def __BuildMediaGroup(self, caption: str, files: dict) -> list[types.InputMedia]:
		"""
		Строит медиа группу из описания.
			caption – подпись для первого файла;
			types – словарь данных файлов.
		"""

		MediaGroup = list()

		for File in files:
			Caption = None if MediaGroup else caption
			if File["type"] == "photo": MediaGroup.append(types.InputMediaPhoto(media = File["file_id"], caption = Caption))
			if File["type"] == "video": MediaGroup.append(types.InputMediaVideo(media = File["file_id"], caption = Caption))
			if File["type"] == "audio": MediaGroup.append(types.InputMediaAudio(media = File["file_id"], caption = Caption))
			if File["type"] == "document": MediaGroup.append(types.InputMediaDocument(media = File["file_id"], caption = Caption))

		return MediaGroup

	def __Mailing(self, admin: UserData, targets: list[UserData]):
		"""
		Метод ведения рассылки.
			admin – администратор;\n
			targets – список целей.
		"""

		Progress = 0.0
		Sended = 0
		Errors = 0
		self.__Bot.send_message(
			chat_id = admin.id,
			text = "Рассылка начата.",
			reply_markup = MailingReplyKeyboards.mailing(admin)
		)
		MessageID = self.__Bot.send_message(
			chat_id = admin.id,
			text = f"<b>📨 Рассылка</b>\n\n⏳ Прогресс: {Progress}%\n✉️ Отправлено: {Sended}\n❌ Ошибок: {Errors}",
			parse_mode = "HTML"
		).id

		Options = admin.get_property("ap")

		for Index in range(len(targets)):
			if Options["mailing"] == None: break

			try:
				if not targets[Index].is_chat_forbidden: self.send_message(admin, targets[Index])
				else: continue

			except: 
				Options["mailing"] = False
				admin.set_property("ap", Options)
				Errors += 1
				return
			else: Sended += 1

			Progress = (Sended + Errors) / len(targets) * 100
			Progress = round(Progress, 2)
			if str(Progress).endswith(".0"): Progress = int(Progress)
			
			self.__Bot.edit_message_text(
				chat_id = admin.id,
				message_id = MessageID,
				text = f"<b>📨 Рассылка</b>\n\n⏳ Прогресс: {Progress}% ({Index + 1} из {len(targets)})\n✉️ Отправлено: {Sended}\n❌ Ошибок: {Errors}",
				parse_mode = "HTML"
			)

		Options["mailing"] = False
		admin.set_property("ap", Options)

		self.__Bot.edit_message_text(
			chat_id = admin.id,
			message_id = MessageID,
			text = f"<b>📨 Рассылка</b>\n\n⏳ Прогресс: {Progress}% ({Index + 1} из {len(targets)})\n✉️ Отправлено: {Sended}\n❌ Ошибок: {Errors}",
			parse_mode = "HTML"
		)
		self.__Bot.send_message(
			chat_id = admin.id,
			text = "Рассылка завершена.",
			reply_markup = MailingReplyKeyboards.mailing(admin)
		)

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, bot: TeleBot):
		"""
		Хранилище данных медиа-файлов.
			bot – бот Telegram.
		"""

		#---> Генерация динамических атрибутов.
		#==========================================================================================#
		self.__Bot = bot
		self.__MailingThread = None

	@Decorators.ignore_frecuency_errors
	def send_message(self, admin: UserData, user: UserData):
		"""
		Отправляет сообщение пользователю.
			admin – администратор;\n
			user – целевой пользователь.
		"""

		Options = admin.get_property("ap")
		Text = Options["mailing_caption"]
		Files = Options["mailing_content"]
		ButtonLabel = Options["button_label"]
		ButtonLink = Options["button_link"]
		SendMethods = {
			"photo": self.__Bot.send_photo,
			"video": self.__Bot.send_video,
			"audio": self.__Bot.send_audio,
			"document": self.__Bot.send_document
		}

		try:
			if len(Files) > 1:
				self.__Bot.send_media_group(
					chat_id = user.id,
					media = self.__BuildMediaGroup(Text, Files)
				)

			elif len(Files) == 1:
				FileType = Files[0]["type"]
				FileID = Files[0]["file_id"]
				SendMethods[FileType](
					user.id,
					FileID,
					caption = Text,
					parse_mode = "HTML",
					reply_markup = self.__BuildButton(ButtonLabel, ButtonLink)
				)
				
			else:
				self.__Bot.send_message(
					chat_id = user.id,
					text = Text,
					parse_mode = "HTML",
					disable_web_page_preview = True,
					reply_markup = self.__BuildButton(ButtonLabel, ButtonLink)
				)

		except: user.set_chat_forbidden(True)

	def start_mailing(self, admin: UserData, users_manager: UsersManager):
		"""
		Отправляет сообщение пользователю.
			admin – администратор;\n
			users_manager – менеджер управления пользователями.
		"""

		Options = admin.get_property("ap")
		Sampling = Options["sampling"]
		Targets = None

		if type(Sampling) == int:
			try: Targets = random.sample(users_manager.users, Sampling)
			except ValueError: Targets = users_manager.users

		elif type(Sampling) == str:
			IsSended = False

			for User in users_manager.users:

				if User.username == Sampling: 
					try: self.send_message(admin, User)
					except: User.set_chat_forbidden(True)
					else: IsSended = True
					break

			if IsSended: self.__Bot.send_message(admin.id, f"✅ Сообщение отправлено пользователю @{Sampling}.")
			else: self.__Bot.send_message(admin.id, f"❌ Не удалось отправить сообщение пользователю @{Sampling}.")

			return

		elif Sampling == None: Targets = users_manager.users

		Options["mailing"] = True
		admin.set_property("ap", Options)
		self.__MailingThread = Thread(target = self.__Mailing, args = [admin, Targets])
		self.__MailingThread.start()