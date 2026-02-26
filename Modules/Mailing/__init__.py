from . import InlineKeyboards, ReplyKeyboards
from ...Core.BaseModule import BaseModule
from .Enums import Actions
from . import Functions

from dublib.TelebotUtils.Master.Decorators import ignore_frecuency_errors

from typing import Any, Literal, TYPE_CHECKING
from types import MappingProxyType
from time import sleep

from telebot import types, apihelper

if TYPE_CHECKING:
	from ... import Panel

	from dublib.TelebotUtils.Users import UserData

#==========================================================================================#
# >>>>> ВСПОМОГАТЕЛЬНЫЕ СТРУКТУРЫ ДАННЫХ <<<<< #
#==========================================================================================#

MODULE_DATA_TEMPLATE = MappingProxyType({
	"action": None,
	"text": None,
	"attachments": [],
	"button_label": None,
	"button_link": None
})

class MailingData:
	"""Данные модуля рассылки."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def action(self) -> Actions | None:
		"""Режим взаимодействия."""

		try: return Actions(self.__Data["action"])
		except ValueError: pass

	@property
	def attachments(self) -> tuple[dict[str, str]]:
		"""Набор данных вложений."""

		return tuple(self.__Data["attachments"])

	@property
	def button_label(self) -> str | None:
		"""Надпись кнопки."""

		return self.__Data.get("button_label")
	
	@property
	def button_link(self) -> str | None:
		"""Ссылка кнопки."""

		return self.__Data.get("button_link")

	@property
	def media_group(self) -> tuple[types.InputMedia]:
		"""Медиа группа сообщения."""

		MediaGroup = list()

		for File in self.attachments:
			Caption = None if MediaGroup else self.text
			if File["type"] == "photo": MediaGroup.append(types.InputMediaPhoto(media = File["file_id"], caption = Caption, parse_mode = "HTML"))
			if File["type"] == "video": MediaGroup.append(types.InputMediaVideo(media = File["file_id"], caption = Caption, parse_mode = "HTML"))
			if File["type"] == "audio": MediaGroup.append(types.InputMediaAudio(media = File["file_id"], caption = Caption, parse_mode = "HTML"))
			if File["type"] == "document": MediaGroup.append(types.InputMediaDocument(media = File["file_id"], caption = Caption, parse_mode = "HTML"))
			if File["type"] == "animation": MediaGroup.append(types.InputMediaAnimation(media = File["file_id"], caption = Caption, parse_mode = "HTML"))

		return tuple(MediaGroup)

	@property
	def text(self) -> str | None:
		"""Текст сообщения."""

		return self.__Data.get("text")

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __FillModuleData(self):
		"""Заполняет отсутствующие данные модуля."""

		IsChanged = False

		for Key in MODULE_DATA_TEMPLATE.keys():
			if Key not in self.__Data:
				self.__Data[Key] = MODULE_DATA_TEMPLATE[Key]
				IsChanged = True

		if IsChanged: self.save()

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, panel: "Panel", user: "UserData"):
		"""
		Данные модуля рассылки.

		:param panel: Панель управления.
		:type panel: Panel
		:param user: Данные пользователя.
		:type user: UserData
		"""

		self.__Panel = panel
		self.__User = user

		self.__Options = self.__Panel.load_options_for_user(self.__User)

		self.refresh_data()
		self.__FillModuleData()

	def __getitem__(self, key: str) -> Any:
		"""
		Возвращает значение по ключу.

		:param key: Ключ.
		:type key: str
		:return: Значение.
		:rtype: Any
		:raise KeyError: Выбрасывается при отсутствии ключа в данных модуля.
		"""

		return self.__Data[key]

	def add_attachment(self, type: Literal["animation", "audio", "document", "photo", "video"], file_id: str):
		"""
		Прикрепляет вложение к сообщению.

		:param type: Тип вложения.
		:type type: Literal["animation", "audio", "document", "photo", "video"]
		:param file_id: ID файла.
		:type file_id: str
		"""

		self.__Data["attachments"].append({"type": type, "file_id": file_id})
		self.save()

	def build_button_keyboard(self, user: "UserData") -> types.InlineKeyboardButton | None:
		"""
		Создаёт кнопку-ссылку.

		:param user: Данные пользователя.
		:type user: UserData
		:return: Структура кнопки для прикрепления к сообщению или `None` в случае неудачи.
		:rtype: types.InlineKeyboardButton | None
		"""

		self.refresh_data()

		if not all((self.button_label, self.button_link)): return

		Markup = types.InlineKeyboardMarkup()
		Markup.add(types.InlineKeyboardButton(self.button_label, self.button_link))

		return Markup

	def clear_attachments(self):
		"""Удаляет данные вложений."""

		self.__Data["attachments"] = list()
		self.save()

	def refresh_data(self):
		"""Обновляет данные модуля."""

		self.__Data = self.__Options.get_module_data(SM_Mailing.__name__)

	def save(self):
		"""Сохраняет данные модуля."""

		self.__Options.set_module_data(SM_Mailing.__name__, self.__Data)

	def set_action(self, action: Actions | None):
		"""
		Задаёт текущий режим взаимодействия.

		:param action: Режим взаимодействия.
		:type action: Actions | None
		"""

		self.__Data["action"] = action.value if action else None
		self.save()

	def set_text(self, text: str | None):
		"""
		Задаёт текст сообщения.

		:param text: Текст сообщения.
		:type text: str | None
		"""

		self.__Data["text"] = text
		self.save()

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ РЕДАКТИРОВАНИЯ СВОЙСТВ <<<<< #
	#==========================================================================================#

	def set_button(self, label: str, link: str):
		"""
		Задаёт данные кнопки.

		:param label: Подпись кнопки.
		:type label: str
		:param link: Ссылка кнопки.
		:type link: str
		:raise ValueError: Выбрасывается, если ссылка имеет неверный формат.
		"""

		if not Functions.IsLinkValid(link): raise ValueError("Invalid link scheme.")
		self.__Data["button_label"] = label
		self.__Data["button_link"] = link
		self.save()

	def remove_button(self):
		"""Удаляет данные кнопки."""

		self.__Data["button_label"] = None
		self.__Data["button_link"] = None
		self.save()

#==========================================================================================#
# >>>>> ОСНОВОЙ КЛАСС <<<<< #
#==========================================================================================#

class SM_Mailing(BaseModule):
	"""Модуль рассылки."""

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __GetUnsendedUsers(self, sender: "UserData") -> "tuple[UserData]":
		"""
		Возвращает последовательность пользователей, не получивших текущую рассылку.

		:param sender: Данные отправителя.
		:type sender: UserData
		:return: Набор данных пользователей, не получивших сообщение рассылки.
		:rtype: tuple[UserData]
		"""

		ProgressKey = f"ap_mailing_by_{sender.id}"
		UnsendedUsersBuffer = list()

		for CurrentUser in self._Panel.users_manager.users:
			try: 
				if not CurrentUser.get_property(ProgressKey): UnsendedUsersBuffer.append(CurrentUser)
			except KeyError: UnsendedUsersBuffer.append(CurrentUser)

		return tuple(UnsendedUsersBuffer)

	@ignore_frecuency_errors
	def __SendMessage(self, user: "UserData", data: MailingData) -> int | None:
		"""
		Отправляет сообщение для просмотра.

		:param user: Данные пользователя.
		:type user: UserData
		:param data: Данные модуля рассылки.
		:type data: MailingData
		"""

		Attachments = data.attachments
		AttachmentsCount = len(Attachments)
		MessageID = None

		if not Attachments and not data.text: return

		SendMethods = {
			"animation": self._Bot.send_animation,
			"audio": self._Bot.send_audio,
			"document": self._Bot.send_document,
			"photo": self._Bot.send_photo,
			"video": self._Bot.send_video
		}

		if AttachmentsCount > 1:
			MessageID = self._Bot.send_media_group(user.id, data.media_group).id

		elif AttachmentsCount == 1:
				Attachment = data.attachments[0]
				FileType = Attachment["type"]

				MessageID = SendMethods[FileType](
					user.id,
					Attachment["file_id"],
					caption = data.text,
					parse_mode = "HTML",
					reply_markup = data.build_button_keyboard(user)
				).id
				
		else:
			MessageID = self._Bot.send_message(
				chat_id = user.id,
				text = data.text,
				parse_mode = "HTML",
				disable_web_page_preview = True,
				reply_markup = data.build_button_keyboard(user)
			).id

		if user.is_chat_forbidden: user.set_chat_forbidden(False)

		return MessageID

	def __UpdateProgressMessage(self, user: "UserData", message_id: int, total: int, current: int):
		"""
		Обновляет сообщение с прогрессом.

		:param user: Данные пользователя.
		:type user: UserData
		:param message_id: ID сообщения.
		:type message_id: int
		:param total: Количество пользователей.
		:type total: int
		:param current: Индекс текущего пользователя.
		:type current: int
		"""

		Progress = float(current) / float(total) * 100.0
		Progress = round(Progress, 1)
		if str(Progress).endswith(".0"): Progress = int(Progress)

		Text = (
			"<b>Прогресс рассылки</b>\n",
			f"{current} / {total} ({Progress}%)"
		)

		try:
			self._Bot.edit_message_text(
				text = "\n".join(Text),
				chat_id = user.id,
				message_id = message_id,
				parse_mode = "HTML"
			)

		except apihelper.ApiTelegramException as ExceptionData:
			ExceptionData = str(ExceptionData)
			if "Error code: 400" not in ExceptionData: print(ExceptionData)

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ ОБРАБОТКИ REPLY-КНОПОК <<<<< #
	#==========================================================================================#

	def __AddButton(self, user: "UserData"):
		"""
		Запускает процедуру добавления кнопки.

		:param user: Данные пользователя.
		:type user: UserData
		"""

		user.set_expected_type("ap_button_label")
		self._Bot.send_message(
			chat_id = user.id,
			text = "Отправьте подпись для кнопки.",
			reply_markup = InlineKeyboards.Cancel()
		)

	def __CancelMailing(self, user: "UserData", data: MailingData):
		"""
		Приостанавливает рассылку.

		:param user: Данные пользователя.
		:type user: UserData
		:param data: Данные модуля рассылки.
		:type data: MailingData
		"""

		data.set_action(Actions.CancelMailing)
		self._Bot.send_message(
			chat_id = user.id,
			text = "Сигнал отмены рассылки отправлен. Новая рассылка затронет всех пользователей.",
			reply_markup = ReplyKeyboards.Start(data)
		)

	def __EditMessage(self, user: "UserData", data: MailingData):
		"""
		Запускает процедуру редактирования сообщения.

		:param user: Данные пользователя.
		:type user: UserData
		:param data: Данные модуля рассылки.
		:type data: MailingData
		"""

		user.suppress_saving(True)
		data.set_text(None)
		data.clear_attachments()
		data.set_action(Actions.Editing)
		user.suppress_saving(False)

		self._Bot.send_message(
			chat_id = user.id,
			text = "Отправьте ваше сообщение, после чего нажмите кнопку ниже.",
			reply_markup = ReplyKeyboards.Save()
		)

	def __PauseMailing(self, user: "UserData", data: MailingData):
		"""
		Приостанавливает рассылку.

		:param user: Данные пользователя.
		:type user: UserData
		:param data: Данные модуля рассылки.
		:type data: MailingData
		"""

		data.set_action(Actions.StopMailing)
		self._Bot.send_message(
			chat_id = user.id,
			text = "Сигнал остановки рассылки отправлен.",
			reply_markup = ReplyKeyboards.Start(data)
		)

	def __RemoveButton(self, user: "UserData"):
		"""
		Удаляет данные кнопки.

		:param user: Данные пользователя.
		:type user: UserData
		"""

		ModuleData = self._GetModuleData(user)
		ModuleData.remove_button()
		self._Bot.send_message(chat_id = user.id, text = "Кнопка удалена.", reply_markup = ReplyKeyboards.Start(ModuleData))

	def __ResumeMailing(self, user: "UserData", data: MailingData):
		"""
		Возобновляет рассылку.

		:param user: Данные пользователя.
		:type user: UserData
		:param data: Данные модуля рассылки.
		:type data: MailingData
		"""

		Text = (
			"Нажимая <b>Продолжить</b> вы возобновляете рассылку для тех пользователей, что её ещё не получили.",
			"Если вы редактировали сообщение, оставшиеся пользователи получат его новую версию."
		)

		self._Bot.send_message(
			chat_id = user.id,
			text = "\n\n".join(Text),
			parse_mode = "HTML",
			reply_markup = InlineKeyboards.Resume()
		)

	def __SaveMessage(self, user: "UserData", data: MailingData):
		"""
		Сохраняет данные сообщения.

		:param user: Данные пользователя.
		:type user: UserData
		:param data: Данные модуля рассылки.
		:type data: MailingData
		"""

		data.set_action(None)
		self._Bot.send_message(
			chat_id = user.id,
			text = "Ваше сообщение сохранено.",
			reply_markup = ReplyKeyboards.Start(data)
		)

	def __StartMailing(self, user: "UserData", data: MailingData):
		"""
		Запускает рассылку сообщения.

		:param user: Данные пользователя.
		:type user: UserData
		:param data: Данные модуля рассылки.
		:type data: MailingData
		"""

		ProgressKey = f"ap_mailing_by_{user.id}"
		data.set_action(Actions.Mailing)
		Users = self.__GetUnsendedUsers(user)
		TotalUsersCount = len(self._Panel.users_manager.users)
		ProcessedUsersCount = TotalUsersCount - len(Users)

		self._Bot.send_message(chat_id = user.id, text = "Начата рассылка", reply_markup = ReplyKeyboards.Start(data))
		ProgressMessageID = self._Bot.send_message(
			chat_id = user.id,
			text = "Загрузка прогресса...",
			parse_mode = "HTML"
		).id

		sleep(self.__Delay)

		for CurrentUser in Users:
			ProcessedUsersCount += 1
			IsSended = False
			
			try:
				if CurrentUser.id == user.id or CurrentUser.get_property(ProgressKey): continue
			except KeyError: pass
			
			match data.action:
				
				case Actions.StopMailing:
					self._Bot.send_message(user.id, "Рассылка приостановлена.", reply_markup = ReplyKeyboards.Start(data))
					return
				
				case Actions.CancelMailing:
					self._Bot.send_message(user.id, "Рассылка отменена.", reply_markup = ReplyKeyboards.Start(data))
					self._Panel.users_manager.remove_property(ProgressKey)
					data.set_action(None)
					return

			try: IsSended = bool(self.__SendMessage(CurrentUser, data))
			except apihelper.ApiTelegramException as ExceptionData:
				if "bot was blocked" in str(ExceptionData): user.set_chat_forbidden(True)

			CurrentUser.set_property(ProgressKey, IsSended)
			sleep(self.__Delay / 2.0)
			self.__UpdateProgressMessage(user, ProgressMessageID, TotalUsersCount, ProcessedUsersCount)
			sleep(self.__Delay / 2.0)

		self.__UpdateProgressMessage(user, ProgressMessageID, TotalUsersCount, ProcessedUsersCount)

		self._Panel.users_manager.remove_property(ProgressKey)
		data.set_action(None)
		self._Bot.send_message(chat_id = user.id, text = "Рассылка завершена.", reply_markup = ReplyKeyboards.Start(data))

	def __ViewMessage(self, user: "UserData", data: MailingData):
		"""
		Отправляет сообщение для предварительного просмотра.

		:param user: Данные пользователя.
		:type user: UserData
		:param data: Данные модуля рассылки.
		:type data: MailingData
		"""

		if not data.attachments and not data.text:
			self._Bot.send_message(user.id, "Вы не задали сообщение.")
			return
		
		self.__SendMessage(user, data)

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _GetModuleData(self, user: "UserData") -> MailingData:
		"""
		Возвращает данные модуля для конкретного пользователя.

		:param user: Данные пользователя.
		:type user: UserData
		:return: Данные модуля.
		:rtype: MailingData
		"""

		return MailingData(self._Panel, user)

	def _PostInitMethod(self):
		"""Метод, выполняющийся после инициализации объекта."""

		self.__Delay = 1.0

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def close(self, user: "UserData"):
		"""
		Обрабатывает закрытие модуля.

		:param user: Данные пользователя.
		:type user: UserData
		"""

		super().close(user)
		LayerMarkup = self._Panel.get_current_layer_reply_markup(user)

		self._Panel.bot.send_message(
			chat_id = user.id,
			text = "Модуль рассылки закрыт.",
			reply_markup = LayerMarkup
		)
		
	def open(self, user: "UserData"):
		"""
		Обрабатывает открытие модуля.

		:param user: Данные пользователя.
		:type user: UserData
		"""
		
		self._Panel.bot.send_message(
			chat_id = user.id,
			text = "Модуль рассылки открыт.",
			reply_markup = ReplyKeyboards.Start(self._GetModuleData(user))
		)

	def process_attachment(self, message: types.Message):
		"""
		Обрабатывает сообщение с вложением от пользователя.

		:param message: Сообщение с вложением.
		:type message: types.Message
		"""

		User = self._Panel.users_manager.auth(message.from_user)
		ModuleData = self._GetModuleData(User)
		if ModuleData.action != Actions.Editing: return

		if message.caption: ModuleData.set_text(message.html_caption)

		match message.content_type:
			case "animation": ModuleData.add_attachment("animation", message.animation.file_id)
			case "audio": ModuleData.add_attachment("audio", message.audio.file_id)
			case "document": ModuleData.add_attachment("document", message.document.file_id)
			case "photo": ModuleData.add_attachment("photo", message.photo[-1].file_id)
			case "video": ModuleData.add_attachment("video", message.video.file_id)

	def process_call(self, call: types.CallbackQuery):
		"""
		Обрабатывает вызов от пользователя.

		:param call: Данные вызова.
		:type call: types.CallbackQuery
		"""

		User = self._Panel.users_manager.auth(call.from_user)
		ModuleData = self._GetModuleData(User)

		match call.data:

			case "ap_cancel":
				self._MasterBot.safely_delete_messages(User.id, call.message.id)
				User.suppress_saving(True)
				User.reset_expected_type()
				User.remove_flags("ap_mailing")
				User.suppress_saving(False)
				self._Bot.send_message(User.id, "Действие отменено.")

			case "ap_mailing_cancel":
				self._MasterBot.safely_delete_messages(User.id, call.message.id)
				ModuleData.set_action(None)
				self._Bot.send_message(User.id, "Рассылка отменена.", reply_markup = ReplyKeyboards.Start(ModuleData))
				self._Panel.users_manager.remove_property(f"ap_mailing_by_{User.id}")

			case "ap_mailing_resume":
				self._MasterBot.safely_delete_messages(User.id, call.message.id)
				self.__StartMailing(User, ModuleData)

	def process_message(self, message: types.Message):
		"""
		Обрабатывает текстовое сообщение от пользователя.

		:param message: Данные сообщения.
		:type message: types.Message
		"""

		User = self._Panel.users_manager.auth(message.from_user)
		ModuleData = self._GetModuleData(User)
		IsExpectedValue = True

		#---> Обработка ожидаемых типов.
		#==========================================================================================#
		match User.expected_type:

			case "ap_button_label":
				User.suppress_saving(True)
				User.set_temp_property("ap_button_label", message.text)
				User.set_expected_type("ap_button_link")
				User.suppress_saving(False)

				self._Bot.send_message(
					chat_id = User.id,
					text = "Отправьте ссылку для кнопки.",
					reply_markup = InlineKeyboards.Cancel()
				)

			case "ap_button_link":

				try:
					User.suppress_saving(True)
					ModuleData.set_button(User.get_property("ap_button_label"), message.text)
					User.reset_expected_type()
					User.clear_temp_properties()
					User.suppress_saving(False)
					self._Bot.send_message(User.id, "Кнопка успешно установлена.", reply_markup = ReplyKeyboards.Start(ModuleData))

				except ValueError:
					self._Bot.send_message(
						chat_id = User.id,
						text = "Неверный формат ссылки. Попробуйте снова.",
						reply_markup = InlineKeyboards.Cancel()
					)

			case _: IsExpectedValue = False

		if IsExpectedValue: return

		#---> Обработка Reply-кнопок.
		#==========================================================================================#
		match message.text:
			case "🔴 Отменить": self.__CancelMailing(User, ModuleData)
			case "🟡 Приостановить": self.__PauseMailing(User, ModuleData)
			case "🟢 Запустить": self.__StartMailing(User, ModuleData)
			case "🟢 Возобновить": self.__ResumeMailing(User, ModuleData)

			case "🔎 Просмотр": self.__ViewMessage(User, ModuleData)
			case "💾 Сохранить": self.__SaveMessage(User, ModuleData)
			case "✏️ Редактировать": self.__EditMessage(User, ModuleData)
			case "🕹️ Добавить кнопку": self.__AddButton(User)
			case "🕹️ Удалить кнопку": self.__RemoveButton(User)
			case "↩️ Назад": self.close(User)

	def set_delay(self, delay: float):
		"""
		Задаёт интервал между отправкой сообщений во время рассылки.

		:param delay: Интервал в секундах.
		:type delay: int
		"""

		self.__Delay = delay