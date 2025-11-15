from .Moderation import ModerationReplyFunctions
from ...Core.Moderation import ModeratorsStorage
from .Uploading import UploadingReplyFunctions
from ..InlineKeyboards import InlineKeyboards
from .Mailing import MailingReplyKeyboards
from ...Core.Uploading import Uploader
from ...Core.Structs import UserInput
from ...Core.Mailer import Mailer

from dublib.TelebotUtils import UsersManager

from telebot import TeleBot, types

class ReplyKeyboards:
	"""Шаблоны Reply-интерфейсов."""

	def admin() -> types.ReplyKeyboardMarkup:
		"""Строит кнопочный интерфейс: панель управления."""

		Menu = types.ReplyKeyboardMarkup(resize_keyboard = True)
		Mailing = types.KeyboardButton("👤 Рассылка")
		Statistics = types.KeyboardButton("📊 Статистика")
		Menu.add(Mailing, Statistics, row_width = 2)
		
		Buffer = list()
		if ModeratorsStorage.MODERATORS: Buffer.append(types.KeyboardButton("🛡️ Модерация"))
		if Uploader.FILES: Buffer.append(types.KeyboardButton("📤 Выгрузка"))
		Menu.add(*Buffer, row_width = 2)

		Close = types.KeyboardButton("❌ Закрыть")
		Menu.add(Close)

		return Menu

	def cancel() -> types.ReplyKeyboardMarkup:
		"""Строит кнопочный интерфейс: отмена."""

		Menu = types.ReplyKeyboardMarkup(resize_keyboard = True)
		Cancel = types.KeyboardButton("❌ Отмена")
		Menu.add(Cancel)

		return Menu
	
	def editing() -> types.ReplyKeyboardMarkup:
		"""Строит кнопочный интерфейс: редактирование сообщения."""

		Menu = types.ReplyKeyboardMarkup(resize_keyboard = True)
		Ok = types.KeyboardButton("✅ Завершить")
		Cancel = types.KeyboardButton("❌ Отмена")
		Menu.add(Ok, Cancel, row_width = 1)

		return Menu

class ReplyFunctions(ModerationReplyFunctions, UploadingReplyFunctions):
	"""Набор функций обработки Reply-кнопок."""

	def Selection(bot: TeleBot, users: UsersManager, message: types.Message):
		"""
		Обрабатывает Reply-кнопку: 🎯 Выборка
			bot – бот Telegram;\n
			users – менеджер пользователей;\n
			message – сообщение от пользователя.
		"""

		User = users.auth(message.from_user)
		User.set_expected_type(UserInput.Sampling.value)
		Options = User.get_property("ap")
		Sampling = Options["sampling"]

		if type(Sampling) == int: Sampling = f"<i>{Sampling} пользователей</i>"
		elif type(Sampling) == str: Sampling = f"@{Sampling}"
		elif Sampling == None: Sampling = "🚫"

		bot.send_message(
			chat_id = message.chat.id,
			text = f"<b>Укажите выборку</b>\n\nТекущее количество пользователей: {len(users.users)}\nТекущая выборка: {Sampling}",
			parse_mode = "HTML",
			reply_markup = InlineKeyboards.sampling(User)
		)

	def AddButton(bot: TeleBot, users: UsersManager, message: types.Message):
		"""
		Обрабатывает Reply-кнопку: 🕹️ Добавить кнопку
			bot – бот Telegram;\n
			users – менеджер пользователей;\n
			message – сообщение от пользователя.
		"""

		User = users.auth(message.from_user)
		User.set_expected_type(UserInput.ButtonLabel.value)
		bot.send_message(
			chat_id = message.chat.id,
			text = "Введите подпись для кнопки.",
			reply_markup = ReplyKeyboards.cancel()
		)

	def Done(bot: TeleBot, users: UsersManager, message: types.Message):
		"""
		Обрабатывает Reply-кнопку: ✅ Завершить
			bot – бот Telegram;\n
			users – менеджер пользователей;\n
			message – сообщение от пользователя.
		"""

		User = users.auth(message.from_user)
		User.set_expected_type(None)
		bot.send_message(
			chat_id = message.chat.id,
			text = "Сообщение сохранено.",
			reply_markup = MailingReplyKeyboards.mailing(User)
		)

	def Close(bot: TeleBot, users: UsersManager, message: types.Message):
		"""
		Обрабатывает Reply-кнопку: ❌ Закрыть
			bot – бот Telegram;\n
			users – менеджер пользователей;\n
			message – сообщение от пользователя.
		"""

		User = users.auth(message.from_user)
		Options = User.get_property("ap")
		Options["is_open"] = False
		User.set_property("ap", Options)
		bot.send_message(
			chat_id = message.chat.id,
			text = "Панель управления закрыта.",
			reply_markup = types.ReplyKeyboardRemove()
		)

	def StartMailing(bot: TeleBot, users: UsersManager, message: types.Message):
		"""
		Обрабатывает Reply-кнопку: 🟢 Запустить
			bot – бот Telegram;\n
			users – менеджер пользователей;\n
			message – сообщение от пользователя.
		"""
		
		User = users.auth(message.from_user)
		User.attach_object("mailer", Mailer(bot))
		Options = User.get_property("ap")

		if not Options["mailing_caption"] and not Options["mailing_content"]:
			bot.send_message(
				chat_id = message.chat.id,
				text = "Вы не задали сообщение для рассылки."
			)

		else: 
			Object: Mailer = User.get_object("mailer")
			Object.start_mailing(User, users)

	def Back(bot: TeleBot, users: UsersManager, message: types.Message):
		"""
		Обрабатывает Reply-кнопку: ↩️ Назад
			bot – бот Telegram;\n
			users – менеджер пользователей;\n
			message – сообщение от пользователя.
		"""

		User = users.auth(message.from_user)
		bot.send_message(
			chat_id = message.chat.id,
			text = "Панель управления.",
			reply_markup = ReplyKeyboards.admin()
		)

	def Cancel(bot: TeleBot, users: UsersManager, message: types.Message):
		"""
		Обрабатывает Reply-кнопку: ❌ Отмена
			bot – бот Telegram;\n
			users – менеджер пользователей;\n
			message – сообщение от пользователя.
		"""

		User = users.auth(message.from_user)
		
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
			chat_id = message.chat.id,
			text = "Действие отменено.",
			reply_markup = MailingReplyKeyboards.mailing(User)
		)

	def StopMailing(bot: TeleBot, users: UsersManager, message: types.Message):
		"""
		Обрабатывает Reply-кнопку: "🔴 Остановить"
			bot – бот Telegram;\n
			users – менеджер пользователей;\n
			message – сообщение от пользователя.
		"""

		User = users.auth(message.from_user)
		Options = User.get_property("ap")
		Options["mailing"] = None
		User.set_property("ap", Options)

	def View(bot: TeleBot, users: UsersManager, message: types.Message):
		"""
		Обрабатывает Reply-кнопку: 🔎 Просмотр
			bot – бот Telegram;\n
			users – менеджер пользователей;\n
			message – сообщение от пользователя.
		"""

		User = users.auth(message.from_user)
		Options = User.get_property("ap")

		if not Options["mailing_caption"] and not Options["mailing_content"]:
			bot.send_message(
				chat_id = message.chat.id,
				text = "Вы не задали сообщение для рассылки."
			)

		else: Mailer(bot).send_message(User, User)

	def Mailing(bot: TeleBot, users: UsersManager, message: types.Message):
		"""
		Обрабатывает Reply-кнопку: 👤 Рассылка
			bot – бот Telegram;\n
			users – менеджер пользователей;\n
			message – сообщение от пользователя.
		"""

		User = users.auth(message.from_user)
		bot.send_message(
			chat_id = message.chat.id,
			text = "Управление рассылкой.",
			reply_markup = MailingReplyKeyboards.mailing(User)
		)

	def Edit(bot: TeleBot, users: UsersManager, message: types.Message):
		"""
		Обрабатывает Reply-кнопку: ✏️ Редактировать
			bot – бот Telegram;\n
			users – менеджер пользователей;\n
			message – сообщение от пользователя.
		"""
		User = users.auth(message.from_user)
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
			chat_id = message.chat.id,
			text = "Отправьте сообщение, которое будет использоваться в рассылке.\n\nЕсли вы прикрепляете несколько вложений, для их упорядочивания рекомендуется выполнять загрузку файлов последовательно.",
			reply_markup = ReplyKeyboards.editing()
		)

	def Statistics(bot: TeleBot, users: UsersManager, message: types.Message):
		"""
		Обрабатывает Reply-кнопку: 📊 Статистика
			bot – бот Telegram;\n
			users – менеджер пользователей;\n
			message – сообщение от пользователя.
		"""

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
			chat_id = message.chat.id,
			text = "\n".join(Text),
			parse_mode = "HTML",
			reply_markup = InlineKeyboards.extract() 
		)

	def RemoveButton(bot: TeleBot, users: UsersManager, message: types.Message):
		"""
		Обрабатывает Reply-кнопку: 🕹️ Удалить кнопку
			bot – бот Telegram;\n
			users – менеджер пользователей;\n
			message – сообщение от пользователя.
		"""
		User = users.auth(message.from_user)
		Options = User.get_property("ap")
		Options["button_label"] = None
		Options["button_link"] = None
		User.set_property("ap", Options)
		bot.send_message(
			chat_id = message.chat.id,
			text = "Кнопка удалена.",
			reply_markup = MailingReplyKeyboards.mailing(User)
		)