from .InlineKeyboards import InlineKeyboards
from .Extractor import GenerateExtractFile
from .ReplyKeyboards import ReplyKeyboards
from .Mailer import Mailer

from dublib.TelebotUtils import UserData, UsersManager

from telebot import TeleBot, types
from datetime import datetime

import enum
import os

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
				"mailing_caption": None,
				"mailing_content": [],
				"button_label": None,
				"button_link": None,
				"sampling": None,
				"mailing": False
			}
			User.set_property("ap", Options, force = False)
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

	def inline_keyboards(self, bot: TeleBot = None, users: UsersManager = None):
		"""
		Набор декораторов: Inline-кнопки.
			bot – экземпляр бота;\n
			users – менеджер пользователей.
		"""

		@bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("ap_sampling"))
		def InlineButton(Call: types.CallbackQuery):
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
				reply_markup = ReplyKeyboards.mailing(User)
			)
				
			else: User.set_expected_type(None)

		@bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("ap_extract"))
		def InlineButton(Call: types.CallbackQuery):
			User = users.auth(Call.from_user)
			Date = datetime.now().date().strftime("%d.%m.%Y")
			Filename = f"{Date}.xlsx"
			GenerateExtractFile(Filename, users.users)

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

		@bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("ap_one_user"))
		def InlineButton(Call: types.CallbackQuery):
			User = users.auth(Call.from_user)
			bot.send_message(User.id, "Отправьте полный ник пользователя или ссылку на него.", reply_markup = ReplyKeyboards.cancel())
			User.set_expected_type(UserInput.Username.value)
			bot.answer_callback_query(Call.id)

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
		def Button(Message: types.Message):
			User = users.auth(Message.from_user)
			User.set_expected_type(UserInput.Sampling.value)
			Options = User.get_property("ap")
			Sampling = Options["sampling"]

			if type(Sampling) == int: Sampling = f"<i>{Sampling} пользователей</i>"
			elif type(Sampling) == str: Sampling = f"@{Sampling}"
			elif Sampling == None: Sampling = "🚫"

			bot.send_message(
				chat_id = Message.chat.id,
				text = f"<b>Укажите выборку</b>\n\nТекущее количество пользователей: {len(users.users)}\nТекущая выборка: {Sampling}",
				parse_mode = "HTML",
				reply_markup = InlineKeyboards.sampling(User)
			)

		@bot.message_handler(content_types = ["text"], regexp = "🕹️ Добавить кнопку")
		def Button(Message: types.Message):
			User = users.auth(Message.from_user)
			User.set_expected_type(UserInput.ButtonLabel.value)
			bot.send_message(
				chat_id = Message.chat.id,
				text = "Введите подпись для кнопки.",
				reply_markup = ReplyKeyboards.cancel()
			)

		@bot.message_handler(content_types = ["text"], regexp = "✅ Завершить")
		def Button(Message: types.Message):
			User = users.auth(Message.from_user)
			User.set_expected_type(None)
			bot.send_message(
				chat_id = Message.chat.id,
				text = "Сообщение сохранено.",
				reply_markup = ReplyKeyboards.mailing(User)
			)

		@bot.message_handler(content_types = ["text"], regexp = "❌ Закрыть")
		def Button(Message: types.Message):
			User = users.auth(Message.from_user)
			bot.send_message(
				chat_id = Message.chat.id,
				text = "Панель управления закрыта.",
				reply_markup = types.ReplyKeyboardRemove()
			)

		@bot.message_handler(content_types = ["text"], regexp = "🟢 Запустить")
		def Button(Message: types.Message):
			User = users.auth(Message.from_user)
			User.set_object("mailer", Mailer(bot))
			Options = User.get_property("ap")

			if not Options["mailing_caption"] and not Options["mailing_content"]:
				bot.send_message(
					chat_id = Message.chat.id,
					text = "Вы не задали сообщение для рассылки."
				)

			else: User.get_object("mailer").start_mailing(User, users)

		@bot.message_handler(content_types = ["text"], regexp = "↩️ Назад")
		def Button(Message: types.Message):
			User = users.auth(Message.from_user)
			bot.send_message(
				chat_id = Message.chat.id,
				text = "Панель управления.",
				reply_markup = ReplyKeyboards.admin()
			)

		@bot.message_handler(content_types = ["text"], regexp = "❌ Отмена")
		def Button(Message: types.Message):
			User = users.auth(Message.from_user)
			
			if User.expected_type == UserInput.Message.value:
				Options = User.get_property("ap")
				User.set_expected_type(UserInput.Message.value)
				Caption = Options["temp_mailing_caption"]
				Content = Options["temp_mailing_content"]
				Options["mailing_caption"] = Caption
				Options["mailing_content"] = Content
				del Options["temp_mailing_caption"]
				del Options["temp_mailing_content"]
				User.set_property("ap", Options)

			User.set_expected_type(None)
			bot.send_message(
				chat_id = Message.chat.id,
				text = "Действие отменено.",
				reply_markup = ReplyKeyboards.mailing(User)
			)

		@bot.message_handler(content_types = ["text"], regexp = "🔴 Остановить")
		def Button(Message: types.Message):
			User = users.auth(Message.from_user)
			Options = User.get_property("ap")
			Options["mailing"] = None
			User.set_property("ap", Options)

		@bot.message_handler(content_types = ["text"], regexp = "🔎 Просмотр")
		def Button(Message: types.Message):
			User = users.auth(Message.from_user)
			Options = User.get_property("ap")

			if not Options["mailing_caption"] and not Options["mailing_content"]:
				bot.send_message(
					chat_id = Message.chat.id,
					text = "Вы не задали сообщение для рассылки."
				)

			else: Mailer(bot).send_message(User, User)

		@bot.message_handler(content_types = ["text"], regexp = "👤 Рассылка")
		def Button(Message: types.Message):
			User = users.auth(Message.from_user)
			bot.send_message(
				chat_id = Message.chat.id,
				text = "Управление рассылкой.",
				reply_markup = ReplyKeyboards.mailing(User)
			)

		@bot.message_handler(content_types = ["text"], regexp = "✏️ Редактировать")
		def Button(Message: types.Message):
			User = users.auth(Message.from_user)
			Options = User.get_property("ap")
			User.set_expected_type(UserInput.Message.value)
			Caption = Options["mailing_caption"]
			Content = Options["mailing_content"]
			Options["temp_mailing_caption"] = Caption
			Options["temp_mailing_content"] = Content
			Options["mailing_caption"] = None
			Options["mailing_content"] = list()
			User.set_property("ap", Options)
			bot.send_message(
				chat_id = Message.chat.id,
				text = "Отправьте сообщение, которое будет использоваться в рассылке.\n\nЕсли вы прикрепляете несколько вложений, для их упорядочивания рекомендуется выполнять загрузку файлов последовательно.",
				reply_markup = ReplyKeyboards.editing()
			)

		@bot.message_handler(content_types = ["text"], regexp = "📊 Статистика")
		def Button(Message: types.Message):
			User = users.auth(Message.from_user)

			UsersCount = len(users.users)
			BlockedUsersCount = 0

			for user in users.users:
				if user.is_chat_forbidden: BlockedUsersCount += 1

			Counts = [len(users.premium_users), len(users.get_active_users()), BlockedUsersCount]
			Percentages = [None, None, None]

			for Index in range(len(Counts)):
				Percentages[Index] = round(Counts[Index] / UsersCount * 100, 1)
				if str(Percentages[Index]).endswith(".0"): Percentages[Index] = int(Percentages[Index])

			Text = (
				"<b>📊 Статистика</b>\n",
				f"👤 Всего пользователей: <b>{UsersCount}</b>",
				f"⭐ Из них Premium: <b>{Counts[0]}</b> (<i>{Percentages[0]}%</i>)",
				f"🧩 Активных за сутки: <b>{Counts[1]}</b> (<i>{Percentages[1]}%</i>)",
				f"⛔ Заблокировали: <b>{Counts[2]}</b> (<i>{Percentages[2]}%</i>)"
			)

			bot.send_message(
				chat_id = Message.chat.id,
				text = "\n".join(Text),
				parse_mode = "HTML",
				reply_markup = InlineKeyboards.extract() 
			)

		@bot.message_handler(content_types = ["text"], regexp = "🕹️ Удалить кнопку")
		def Button(Message: types.Message):
			User = users.auth(Message.from_user)
			Options = User.get_property("ap")
			Options["button_label"] = None
			Options["button_link"] = None
			User.set_property("ap", Options)
			bot.send_message(
				chat_id = Message.chat.id,
				text = "Кнопка удалена.",
				reply_markup = ReplyKeyboards.mailing(User)
			)

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

	def text(self, bot: TeleBot, user: UserData, message: types.Message) -> bool:
		"""
		Набор процедур: текст.
			bot – экземпляр бота;\n
			user – пользователь;\n
			message – сообщение.
		"""

		if not user.expected_type: return False
		elif not user.expected_type.startswith("ap_"): return False
		elif not user.has_permissions("admin"): return False

		Options = user.get_property("ap")

		if user.expected_type == UserInput.Message.value:
			Options["mailing_caption"] = message.html_text
			user.set_property("ap", Options)

		elif user.expected_type == UserInput.ButtonLabel.value:
			Options["button_label"] = message.text
			user.set_property("ap", Options)
			user.set_expected_type(UserInput.ButtonLink.value)
			bot.send_message(
				chat_id = message.chat.id,
				text = "Отправьте ссылку, которая будет помещена в кнопку.",
				reply_markup = ReplyKeyboards.cancel()
			)
		
		elif user.expected_type == UserInput.ButtonLink.value:
			Options["button_link"] = message.text
			user.set_property("ap", Options)
			user.set_expected_type(None)
			bot.send_message(
				chat_id = message.chat.id,
				text = "Кнопка прикреплена к сообщению.",
				reply_markup = ReplyKeyboards.mailing(user)
			)
		
		elif user.expected_type == UserInput.Username.value:
			Username = message.text.lstrip("@")
			if Username.startswith("https://t.me/"): Username = Username[len("https://t.me/"):]

			Options["sampling"] = Username
			user.set_property("ap", Options)
			user.set_expected_type(None)
			bot.send_message(
				chat_id = message.chat.id,
				text = "Никнейм сохранён.",
				reply_markup = ReplyKeyboards.mailing(user)
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

class UserInput(enum.Enum):
	ButtonLabel = "ap_button_label"
	ButtonLink = "ap_button_link"
	Message = "ap_message"
	Sampling = "ap_sampling"
	Username = "ap_username"
	
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