from . import InlineKeyboards, Moderators, ReplyKeyboards
from .ModerationOptions import ModerationOptions
from ...Core.BaseModule import BaseModule
from .Storage import Storage

from dublib.TelebotUtils import UserData

from typing import Callable, TYPE_CHECKING
import enum

from telebot import types

if TYPE_CHECKING:
	from dublib.TelebotUtils.Users import UserData

class ModeratorsModes(enum.Enum):
	View = 1
	Editable = 2

class SM_Moderation(BaseModule):
	"""Модуль модерации контента."""

	#==========================================================================================#
	# >>>>> ЗАЩИЩЁННЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _PostInitMethod(self):
		"""Метод, выполняющийся после инициализации объекта."""

		self.__Moderators: dict[str, Moderators.BaseModerator] = dict()

	#==========================================================================================#
	# >>>>> ОБЩИЕ ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def close(self, user: "UserData"):
		"""
		Обрабатывает закрытие модуля.

		:param user: Данные пользователя.
		:type user: UserData
		"""

		super().close(user)
		LayerMarkup = self._Panel.get_current_layer_reply_markup(user)
		ModuleData = ModerationOptions(user)
		ModuleData.set_current_moderator(None)
		ModuleData.set_value(None)

		self._Panel.bot.send_message(
			chat_id = user.id,
			text = "Модуль модерации закрыт.",
			reply_markup = LayerMarkup
		)
		
	def open(self, user: "UserData"):
		"""
		Обрабатывает открытие модуля.

		:param user: Данные пользователя.
		:type user: UserData
		"""
		
		if not self.__Moderators:
			self._Panel.bot.send_message(
				chat_id = user.id,
				text = "Модераторы не инициализированы."
			)
			super().close(user)
			return
		
		self._Panel.bot.send_message(
			chat_id = user.id,
			text = "Выберите модератор:",
			reply_markup = ReplyKeyboards.Start(self.__Moderators.keys())
		)

	def process_call(self, call: types.CallbackQuery):
		"""
		Обрабатывает вызов от пользователя.

		:param call: Данные вызова.
		:type call: types.CallbackQuery
		"""

		User = self._Panel.users_manager.auth(call.from_user)
		ModuleData = ModerationOptions(User)

		if not ModuleData.current_moderator:
			self._Panel.bot.answer_callback_query(call.id, "Не указан модератор.")
			return
		
		Storage = self.__Moderators[ModuleData.current_moderator].storage

		if call.data.startswith("ap_moderate"):
			Status = call.data[11:].lstrip("_")
			self._Panel.master_bot.safely_delete_messages(User.id, call.message.id)
			Status: bool = Status == "true"
			self.__Moderators[ModuleData.current_moderator].emit_callback(ModuleData.value, Status)
			ModuleData.set_value(None)
			self.__Moderators[ModuleData.current_moderator].run(User)

		elif call.data == "ap_edit":
			self._Panel.bot.answer_callback_query(call.id)
			self._Panel.bot.send_message(
				chat_id = User.id,
				text = "Отправьте изменённый текст."
			)
			User.set_expected_type("ap_moderation_edit")

		elif call.data == "ap_previous":
			Element = Storage.get_element_with_offset(ModuleData.value, offset = -1)

			if not Element:
				self._Panel.bot.answer_callback_query(call.id, "Первый элемент.")
				return
			
			ModuleData.set_value(Element)
			
			if ModuleData.canvas_id:
				self._Panel.bot.edit_message_text(Element, User.id, ModuleData.canvas_id, reply_markup = InlineKeyboards.View())

			else:
				self._Panel.master_bot.safely_delete_messages(User.id, call.message.id)
				self.__Moderators[ModuleData.current_moderator].run(User)

		elif call.data == "ap_next":
			Element = Storage.get_element_with_offset(ModuleData.value, offset = 1)

			if not Element:
				self._Panel.bot.answer_callback_query(call.id, "Последний элемент.")
				return
			
			ModuleData.set_value(Element)

			if ModuleData.canvas_id:
				self._Panel.bot.edit_message_text(Element, User.id, ModuleData.canvas_id, reply_markup = InlineKeyboards.View())

			else:
				self._Panel.master_bot.safely_delete_messages(User.id, call.message.id)
				self.__Moderators[ModuleData.current_moderator].run(User)

	def process_message(self, message: types.Message):
		"""
		Обрабатывает текстовое сообщение от пользователя.

		:param message: Данные сообщения.
		:type message: types.Message
		"""

		User = self._Panel.users_manager.auth(message.from_user)
		ModuleData = ModerationOptions(User)

		match message.text:
			
			case "↩️ Назад":
				ModuleData.set_value(None)
				ModuleData.set_current_moderator(None)
				self.close(User)

			case _:

				if User.expected_type == "ap_moderation_edit":
					User.reset_expected_type()
					ModuleData = ModerationOptions(User)
					self.__Moderators[ModuleData.current_moderator].storage.replace(ModuleData.value, message.html_text)
					ModuleData.set_value(message.html_text)
					self.__Moderators[ModuleData.current_moderator].run(User)

				elif message.text in self.__Moderators:
					ModuleData.set_current_moderator(message.text)
					self.__Moderators[message.text].run(User)

	#==========================================================================================#
	# >>>>> СПЕЦИАЛЬНЫЕ ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def add_moderator(self, id: str, name: str, mode: ModeratorsModes | int, callback: Callable | None = None) -> Storage:
		"""
		Добавляет модератор и подключает его к хранилищу с указанным ID.

		:param id: Идентификатор хранилища.
		:type id: str
		:param name: Отображаемое в Reply-меню имя модератора.
		:type name: str
		:param mode: Режим обработки элементов хранилища.
		:type mode: ModeratorsModes | int
		:param callback: Функция или метод, куда направляются результаты модерации.
		:type callback: Callable | None
		:return: Хранилище элементов ожидающих модерации.
		:rtype: Storage
		"""

		if type(mode) == int: mode = ModeratorsModes(mode)
		ModeratorType = None

		match mode:
			case ModeratorsModes.Editable: ModeratorType = Moderators.Moderator_Editable
			case ModeratorsModes.View: ModeratorType = Moderators.Moderator_View

		StorageObject = Storage(self._Panel, id)
		Moderator: "Moderators.BaseModerator" = ModeratorType(self._Panel, StorageObject)
		Moderator.set_callback(callback)
		self.__Moderators[name.strip()] = Moderator

		return StorageObject