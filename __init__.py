from .UI.InlineKeyboards.Moderation import ModerationInlineDecorators
from .UI.InlineKeyboards.Uploading import UploadingInlineDecorators
from .UI.ReplyKeyboards import ReplyFunctions, ReplyKeyboards
from .UI.ReplyKeyboards.Mailing import MailingReplyKeyboards
from .Core.Structs import OptionsStruct, UserInput
from .UI.InlineKeyboards import InlineKeyboards
from .Core.Extractor import Extractor

from dublib.TelebotUtils import UserData, UsersManager

from datetime import datetime
import os

from telebot import TeleBot, types

#==========================================================================================#
# >>>>> СТРУКТУРЫ <<<<< #
#==========================================================================================#

class Decorators:
	"""Наборы декораторов."""

	def __init__(self, panel: "Panel", bot: TeleBot, users_manager: UsersManager):
		"""
		Наборы декораторов.

		:param panel: Панель управления.
		:type panel: Panel
		:param bot: Бот Telegram.
		:type bot: TeleBot
		:param users_manager: Менеджер пользователей.
		:type users_manager: UsersManager
		"""

		self.__Panel = panel
		self.__Bot = bot
		self.__UsersManager = users_manager

	def commands(self):
		"""Набор декораторов: команды."""

		@self.__Bot.message_handler(commands = ["admin"])
		def CommandAdmin(Message: types.Message):
			User = self.__UsersManager.auth(Message.from_user)
			Options = OptionsStruct(User)
			Options.set_open_state(True)

			MessageWords = Message.text.split(" ")

			if not User.has_permissions("admin") and len(MessageWords) == 2:
				User.add_permissions("admin")

				if MessageWords[1] == self.__Panel.password:
					self.__Bot.send_message(
						chat_id = Message.chat.id,
						text = "Пароль принят. Доступ разрешён.",
						reply_markup = ReplyKeyboards.admin()
					)

				else: self.__Bot.send_message(Message.chat.id, "Неверный пароль.")

			else:

				if User.has_permissions("admin"):
					self.__Bot.send_message(
						chat_id = Message.chat.id,
						text = "Доступ разрешён.",
						reply_markup = ReplyKeyboards.admin()
					)

				else: self.__Bot.send_message(Message.chat.id, "Доступ запрещён.")

	def files(self):
		"""Набор декораторов: файлы."""

		@self.__Bot.message_handler(content_types = ["audio", "document", "photo", "video"])
		def Files(Message: types.Message):
			User = self.__UsersManager.auth(Message.from_user)
			Options = OptionsStruct(User)

			if User.has_permissions("admin") and User.expected_type == UserInput.Message.value:
				if Message.caption: Options.mailing.set_caption(Message.html_caption)

				match Message.content_type:
					case "audio": Options.mailing.add_attachment("audio", Message.audio.file_id)
					case "document": Options.mailing.add_attachment("document", Message.document.file_id)
					case "video": Options.mailing.add_attachment("video", Message.video.file_id)
					case "photo": Options.mailing.add_attachment("photo", Message.photo[-1].file_id)

	def inline_keyboards(self):
		"""Набор декораторов: Inline-кнопки."""

		@self.__Bot.callback_query_handler(func = lambda Callback: Callback.data == "ap_delete")
		def Delete(Call: types.CallbackQuery):
			self.__Bot.delete_message(Call.message.chat.id, Call.message.id)

		@self.__Bot.callback_query_handler(func = lambda Callback: Callback.data == "ap_extract")
		def Extract(Call: types.CallbackQuery):
			User = self.__UsersManager.auth(Call.from_user)
			Date = datetime.now().date().strftime("%d.%m.%Y")
			Filename = f"{Date}.xlsx"
			Extractor().generate_file(Filename, self.__UsersManager.users)

			try:
				self.__Bot.delete_message(User.id, Call.message.id)
				self.__Bot.send_document(
					chat_id = User.id,
					document = open(Filename, "rb"), 
					caption = f"Выписка из статистики бота за {Date}. Данный файл совместим с системой <a href=\"https://github.com/DUB1401/SpamBot\">SpamBot</a>.",
					parse_mode = "HTML"
				)
				os.remove(Filename)

			except Exception as ExceptionData: print(ExceptionData)

		@self.__Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("ap_sampling"))
		def Sampling(Call: types.CallbackQuery):
			User = self.__UsersManager.auth(Call.from_user)
			Options = OptionsStruct(User)

			if Call.data.endswith("all"): Options.mailing.set_sampling(None)
			elif Call.data.endswith("last"): Options.mailing.set_sampling(1000)

			self.__Bot.answer_callback_query(Call.id)
			self.__Bot.delete_message(chat_id = User.id, message_id = Call.message.id)

			if not Call.data.endswith("cancel"): self.__Bot.send_message(
				chat_id = User.id,
				text = "Выборка установлена.",
				reply_markup = MailingReplyKeyboards.mailing(User)
			)
				
			else: User.set_expected_type(None)

		@self.__Bot.callback_query_handler(func = lambda Callback: Callback.data == "ap_one_user")
		def SamplingOneUser(Call: types.CallbackQuery):
			User = self.__UsersManager.auth(Call.from_user)
			self.__Bot.send_message(User.id, "Отправьте полный ник пользователя или ссылку на него.", reply_markup = ReplyKeyboards.cancel())
			User.set_expected_type(UserInput.Username.value)
			self.__Bot.answer_callback_query(Call.id)

		ModerationInlineDecorators(self.__Bot, self.__UsersManager)
		UploadingInlineDecorators(self.__Bot, self.__UsersManager)
		
class Keyboards:
	"""Контейнер разметок кнопок."""

	@property
	def inline(self) -> types.InlineKeyboardMarkup:
		"""Inline-разметки кнопок."""

		return self.__Inline

	@property
	def reply(self) -> types.ReplyKeyboardMarkup:
		"""Reply-разметки кнопок."""

		return self.__Reply

	def __init__(self):
		"""Контейнер разметок кнопок."""

		self.__Inline = InlineKeyboards()
		self.__Reply = ReplyKeyboards

class Procedures:
	"""Наборы процедур."""

	def text(self, bot: TeleBot, users: UsersManager, message: types.Message) -> bool:
		"""
		Набор процедур: текст.
			bot – экземпляр бота;\n
			users – менеджер пользователей;\n
			message – сообщение.
		"""

		User = users.auth(message.from_user)
		if not User.has_permissions("admin"): return False
		Options = User.get_property("ap")

		if Options["is_open"]:
			IsReplyButton = True

			match message.text:
				case "🎯 Выборка": ReplyFunctions.Selection(bot, users, message)
				case "🕹️ Добавить кнопку": ReplyFunctions.AddButton(bot, users, message)
				case "✅ Завершить": ReplyFunctions.Done(bot, users, message)
				case "❌ Закрыть": ReplyFunctions.Close(bot, users, message)
				case "🟢 Запустить": ReplyFunctions.StartMailing(bot, users, message)
				case "↩️ Назад": ReplyFunctions.Back(bot, users, message)
				case "❌ Отмена": ReplyFunctions.Cancel(bot, users, message)
				case "🔴 Остановить": ReplyFunctions.StopMailing(bot, users, message)
				case "🔎 Просмотр": ReplyFunctions.View(bot, users, message)
				case "👤 Рассылка": ReplyFunctions.Mailing(bot, users, message)
				case "✏️ Редактировать": ReplyFunctions.Edit(bot, users, message)
				case "📊 Статистика": ReplyFunctions.Statistics(bot, users, message)
				case "🕹️ Удалить кнопку": ReplyFunctions.RemoveButton(bot, users, message)

				case "📤 Выгрузка": ReplyFunctions.Uploading(bot, users, message)
				case "🛡️ Модерация": ReplyFunctions.Moderation(bot, users, message)

				case _ : IsReplyButton = False

			if IsReplyButton: return True

		if not User.expected_type or not User.expected_type.startswith("ap_"): return False

		if User.expected_type == UserInput.Message.value:
			Options["mailing_caption"] = message.html_text
			User.set_property("ap", Options)

		elif User.expected_type == UserInput.ButtonLabel.value:
			Options["button_label"] = message.text
			User.set_property("ap", Options)
			User.set_expected_type(UserInput.ButtonLink.value)
			bot.send_message(
				chat_id = message.chat.id,
				text = "Отправьте ссылку, которая будет помещена в кнопку.",
				reply_markup = ReplyKeyboards.cancel()
			)
		
		elif User.expected_type == UserInput.ButtonLink.value:
			Options["button_link"] = message.text
			User.set_property("ap", Options)
			User.set_expected_type(None)
			bot.send_message(
				chat_id = message.chat.id,
				text = "Кнопка прикреплена к сообщению.",
				reply_markup = MailingReplyKeyboards.mailing(User)
			)
		
		elif User.expected_type == UserInput.Username.value:
			Username = message.text.lstrip("@")
			if Username.startswith("https://t.me/"): Username = Username[len("https://t.me/"):]

			Options["sampling"] = Username
			User.set_property("ap", Options)
			User.set_expected_type(None)
			bot.send_message(
				chat_id = message.chat.id,
				text = "Никнейм сохранён.",
				reply_markup = MailingReplyKeyboards.mailing(User)
			)

		return True

	def files(self, bot: TeleBot, user: UserData = None, message: types.Message = None):
		"""
		Набор процедур: файлы.
			bot – экземпляр бота;\n
			message – сообщение;\n
			user – пользователь.
		"""

		if user.has_permissions("admin") and user.expected_type == UserInput.Message.value:
			Options = user.get_property("ap")
			if message.caption: Options["mailing_caption"] = message.html_caption
			if message.content_type == "audio": Options["mailing_content"].append({"type": "audio", "file_id": message.audio.file_id})
			elif message.content_type == "document": Options["mailing_content"].append({"type": "document", "file_id": message.document.file_id})
			elif message.content_type == "video": Options["mailing_content"].append({"type": "video", "file_id": message.video.file_id})
			elif message.content_type == "photo": Options["mailing_content"].append({"type": "photo", "file_id": message.photo[-1].file_id})

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class Panel:
	"""Панель управления."""

	@property
	def decorators(self) -> Decorators:
		"""Наборы декораторов."""

		return self.__Decorators

	@property
	def keyboards(self) -> Keyboards:
		"""Наборы разметок кнопок."""

		return self.__Keyboards
	
	@property
	def password(self) -> str:
		"""Пароль для доступа в панель управления."""

		return self.__Password

	@property
	def procedures(self) -> Procedures:
		"""Наборы процедур."""

		return self.__Procedures

	def __init__(self, bot: TeleBot, users_manager: UsersManager, password: str):
		"""
		Панель управления.

		:param panel: Панель управления.
		:type panel: Panel
		:param bot: Бот Telegram.
		:type bot: TeleBot
		:param password: Пароль для входа в панель управления.
		:type password: str
		"""

		self.__Password = password

		self.__Decorators = Decorators(self, bot, users_manager)
		self.__Keyboards = Keyboards()
		self.__Procedures = Procedures()