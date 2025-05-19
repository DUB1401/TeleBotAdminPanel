from .UI.ReplyKeyboards import ReplyFunctions, ReplyKeyboards
from .UI.ReplyKeyboards.Mailing import MailingReplyKeyboards
from .UI.InlineKeyboards import InlineKeyboards
from .UI.InlineKeyboards.Moderation import ModerationInlineDecorators
from .Core.Extractor import Extractor
from .Core.Structs import UserInput

from dublib.TelebotUtils import UserData, UsersManager

from datetime import datetime
import os

from telebot import TeleBot, types

#==========================================================================================#
# >>>>> СТРУКТУРЫ <<<<< #
#==========================================================================================#

class Decorators:
	"""Наборы декораторов."""

	def commands(self, bot: TeleBot, users: UsersManager, password: str):
		"""
		Набор декораторов: команды.
			bot – экземпляр бота;\n
			users – менеджер пользователей;\n
			password – пароль администратора.
		"""

		@bot.message_handler(commands = ["admin"])
		def CommandAdmin(Message: types.Message):
			User = users.auth(Message.from_user)
			Options = {
				"is_open": True,
				"mailing_caption": None,
				"mailing_content": [],
				"button_label": None,
				"button_link": None,
				"sampling": None,
				"mailing": False
			}
			User.set_property("ap", Options, force = False)

			Options = User.get_property("ap")
			Options["is_open"] = True
			User.set_property("ap", Options)

			MessageWords = Message.text.split(" ")

			if not User.has_permissions("admin") and len(MessageWords) == 2:
				User.add_permissions("admin")

				if MessageWords[1] == password:
					bot.send_message(
						chat_id = Message.chat.id,
						text = "Пароль принят. Доступ разрешён.",
						reply_markup = ReplyKeyboards.admin()
					)

				else:
					bot.send_message(
						chat_id = Message.chat.id,
						text = "Неверный пароль."
					)

			else:

				if User.has_permissions("admin"):
					bot.send_message(
						chat_id = Message.chat.id,
						text = "Доступ разрешён.",
						reply_markup = ReplyKeyboards.admin()
					)

				else:
					bot.send_message(
						chat_id = Message.chat.id,
						text = "Доступ запрещён."
					)

	def files(self, bot: TeleBot, users: UsersManager):
		"""
		Набор декораторов: файлы.
			bot – экземпляр бота;\n
			users – менеджер пользователей.
		"""

		@bot.message_handler(content_types = ["audio", "document", "photo", "video"])
		def Files(Message: types.Message):
			User = users.auth(Message.from_user)
			Options = User.get_property("ap")

			if User.has_permissions("admin") and User.expected_type == UserInput.Message.value:
				
				if Message.caption:
					Options["mailing_caption"] = Message.html_caption
					User.set_property("ap", Options)

				if Message.content_type == "audio": Options["mailing_content"].append({"type": "audio", "file_id": Message.audio.file_id})
				elif Message.content_type == "document": Options["mailing_content"].append({"type": "document", "file_id": Message.document.file_id})
				elif Message.content_type == "video": Options["mailing_content"].append({"type": "video", "file_id": Message.video.file_id})
				elif Message.content_type == "photo": Options["mailing_content"].append({"type": "photo", "file_id": Message.photo[-1].file_id})

	def inline_keyboards(self, bot: TeleBot, users: UsersManager):
		"""
		Набор декораторов: Inline-кнопки.
			bot – экземпляр бота;\n
			users – менеджер пользователей.
		"""

		@bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("ap_delete"))
		def Delete(Call: types.CallbackQuery):
			bot.delete_message(Call.message.chat.id, Call.message.id)

		@bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("ap_extract"))
		def Extract(Call: types.CallbackQuery):
			User = users.auth(Call.from_user)
			Date = datetime.now().date().strftime("%d.%m.%Y")
			Filename = f"{Date}.xlsx"
			Extractor().generate_file(Filename, users.users)

			try:
				bot.delete_message(User.id, Call.message.id)
				bot.send_document(
					chat_id = User.id,
					document = open(Filename, "rb"), 
					caption = f"Выписка из статистики бота за {Date}. Данный файл совместим с системой <a href=\"https://github.com/DUB1401/SpamBot\">SpamBot</a>.",
					parse_mode = "HTML"
				)
				os.remove(Filename)

			except Exception as ExceptionData: print(ExceptionData)

		@bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("ap_sampling"))
		def Sampling(Call: types.CallbackQuery):
			User = users.auth(Call.from_user)
			Options = User.get_property("ap")
			if Call.data.endswith("all"): Options["sampling"] = None
			if Call.data.endswith("last"): Options["sampling"] = 1000
			User.set_property("ap", Options)

			bot.answer_callback_query(Call.id)
			bot.delete_message(chat_id = User.id, message_id = Call.message.id)

			if not Call.data.endswith("cancel"): bot.send_message(
				chat_id = User.id,
				text = "Выборка установлена.",
				reply_markup = MailingReplyKeyboards.mailing(User)
			)
				
			else: User.set_expected_type(None)

		@bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("ap_one_user"))
		def SamplingOneUser(Call: types.CallbackQuery):
			User = users.auth(Call.from_user)
			bot.send_message(User.id, "Отправьте полный ник пользователя или ссылку на него.", reply_markup = ReplyKeyboards.cancel())
			User.set_expected_type(UserInput.Username.value)
			bot.answer_callback_query(Call.id)

		ModerationInlineDecorators(bot, users)

	def photo(self, bot: TeleBot, users: UsersManager):
		"""
		Набор декораторов: фото.
			bot – экземпляр бота;\n
			users – менеджер пользователей.
		"""

		@bot.message_handler(content_types = ["photo"])
		def Photo(Message: types.Message):
			User = users.auth(Message.from_user)
			Options = User.get_property("ap")

			if User.has_permissions("admin") and User.expected_type == "message":
				if Message.caption: Options["mailing_caption"] = Message.html_caption
				Options["mailing_content"].append({"type": "photo", "file_id": Message.photo[-1].file_id})
				User.set_property("ap", Options)

	def reply_keyboards(self, bot: TeleBot, users: UsersManager):
		"""
		Набор декораторов: Reply-кнопки.
			bot – экземпляр бота;\n
			users – менеджер пользователей.
		"""

		@bot.message_handler(content_types = ["text"], regexp = "🎯 Выборка")
		def Button(Message: types.Message): ReplyFunctions.Selection(bot, users, Message)

		@bot.message_handler(content_types = ["text"], regexp = "🕹️ Добавить кнопку")
		def Button(Message: types.Message): ReplyFunctions.AddButton(bot, users, Message)

		@bot.message_handler(content_types = ["text"], regexp = "✅ Завершить")
		def Button(Message: types.Message): ReplyFunctions.Done(bot, users, Message)

		@bot.message_handler(content_types = ["text"], regexp = "❌ Закрыть")
		def Button(Message: types.Message): ReplyFunctions.Close(bot, users, Message)
		
		@bot.message_handler(content_types = ["text"], regexp = "🟢 Запустить")
		def Button(Message: types.Message): ReplyFunctions.StartMailing(bot, users, Message)
		
		@bot.message_handler(content_types = ["text"], regexp = "↩️ Назад")
		def Button(Message: types.Message): ReplyFunctions.Back(bot, users, Message)
		
		@bot.message_handler(content_types = ["text"], regexp = "❌ Отмена")
		def Button(Message: types.Message): ReplyFunctions.Cancel(bot, users, Message)
		
		@bot.message_handler(content_types = ["text"], regexp = "🔴 Остановить")
		def Button(Message: types.Message): ReplyFunctions.StopMailing(bot, users, Message)
		
		@bot.message_handler(content_types = ["text"], regexp = "🔎 Просмотр")
		def Button(Message: types.Message): ReplyFunctions.View(bot, users, Message)
		
		@bot.message_handler(content_types = ["text"], regexp = "👤 Рассылка")
		def Button(Message: types.Message): ReplyFunctions.Mailing(bot, users, Message)
		
		@bot.message_handler(content_types = ["text"], regexp = "✏️ Редактировать")
		def Button(Message: types.Message): ReplyFunctions.Edit(bot, users, Message)
		
		@bot.message_handler(content_types = ["text"], regexp = "📊 Статистика")
		def Button(Message: types.Message): ReplyFunctions.Statistics(bot, users, Message)
		
		@bot.message_handler(content_types = ["text"], regexp = "🕹️ Удалить кнопку")
		def Button(Message: types.Message): ReplyFunctions.RemoveButton(bot, users, Message)
		
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

		#---> Генерация динамических атрибутов.
		#==========================================================================================#
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
	def procedures(self) -> Procedures:
		"""Наборы процедур."""

		return self.__Procedures

	def __init__(self):
		"""Панель управления."""

		#---> Генерация динамических атрибутов.
		#==========================================================================================#
		self.__Decorators = Decorators()
		self.__Keyboards = Keyboards()
		self.__Procedures = Procedures()