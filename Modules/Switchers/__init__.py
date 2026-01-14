from . import InlineKeyboards, ReplyKeyboards
from ...Core.BaseModule import BaseModule

from dublib.Methods.Filesystem import ReadJSON, WriteJSON

from types import MappingProxyType
from typing import TYPE_CHECKING
import os
import re

from telebot import apihelper, types

if TYPE_CHECKING:
	from dublib.TelebotUtils.Users import UserData

#==========================================================================================#
# >>>>> ДОПОЛНИТЕЛЬНЫЕ СТРУКТУРЫ ДАННЫХ <<<<< #
#==========================================================================================#

class Flag:
	"""Логический флаг."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def id(self) -> str:
		"""Уникальный идентификатор флага."""

		return self.__ID
	
	@property
	def label(self) -> str:
		"""Подпись кнопки переключения."""

		return self.__Label

	@property
	def value(self) -> bool:
		"""Состояние флага."""

		return self.__Value

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, id: str, label: str, value: bool):
		"""
		Логический флаг.

		:param id: Уникальный идентификатор флага. Может содержать только латиницу и цифры.
		:type id: str
		:param label: Подпись для кнопки переключения.
		:type label: str
		:param value: Состояние флага.
		:type value: bool
		"""

		self.__ID = id
		self.__Label = label
		self.__Value = value

	def __bool__(self) -> bool:
		"""
		Интерпретирует объект в логическое значение.

		:return: Логическое значение.
		:rtype: bool
		"""

		return self.__Value

	def disable(self):
		"""Отключает флаг."""

		self.__Value = False

	def enable(self):
		"""Включает флаг."""

		self.__Value = True

	def set(self, value: bool):
		"""
		Задаёт значение флага.

		:param value: Значение флага.
		:type value: bool
		"""

		self.__Value = value

	def switch(self):
		"""Интвертирует логическое значение."""

		self.__Value = not self.__Value

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class SM_Switchers(BaseModule):
	"""Модуль переключателей."""

	#==========================================================================================#
	# >>>>> СТАТИЧЕСКИЕ АТРИБУТЫ <<<<< #
	#==========================================================================================#

	SWITCHERS: MappingProxyType[str, Flag] = MappingProxyType({})

	#==========================================================================================#
	# >>>>> ЗАЩИЩЁННЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _IsValidID(self, id: str) -> bool:
		"""
		Проверяет валидность ID.

		:param id: Уникальный идентификатор флага.
		:type id: str
		:return: Возвращает `True`, если ID валиден.
		:rtype: bool
		"""

		return bool(self._PatternID.fullmatch(id))

	def _Load(self):
		"""Загружает данные флагов из файла."""

		if os.path.exists(self._Path):
			Data = ReadJSON(self._Path)
			Buffer = dict()

			for FlagID in Data.keys():
				Buffer[FlagID] = Flag(FlagID, Data[FlagID]["label"], Data[FlagID]["value"])

			SM_Switchers.SWITCHERS = MappingProxyType(Buffer)

	def _Save(self):
		"""Сохраняет состояния флагов в файле."""

		Data = dict()

		for CurrentFlag in SM_Switchers.SWITCHERS.values():
			Data[CurrentFlag.id] = {"label": CurrentFlag.label, "value": CurrentFlag.value}

		WriteJSON(self._Path, Data, pretty = False)

	def _SendFlagsSwitchers(self, user: "UserData"):
		"""
		Отправляет сообщение с переключателями флагов.

		:param user: Данные пользователя.
		:type user: UserData
		"""
		
		self._Bot.send_message(
			chat_id = user.id,
			text = "<b>Список переключателей</b>",
			parse_mode = "HTML",
			reply_markup = InlineKeyboards.FlagsSwitchers(SM_Switchers.SWITCHERS)
		)

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _PostInitMethod(self):
		"""Метод, выполняющийся после инициализации объекта."""

		self._Path = self._Panel.get_module_workdir(SM_Switchers.__name__) + "/flags.json"
		self._PatternID = re.compile("[A-Za-z0-9]+")
		self._Load()

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
			text = "Модуль статистики закрыт.",
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
			text = "Модуль переключаетелей открыт.",
			reply_markup = ReplyKeyboards.Start()
		)

	def process_call(self, call: types.CallbackQuery):
		"""
		Обрабатывает вызов от пользователя.

		:param call: Данные вызова.
		:type call: types.CallbackQuery
		"""

		User = self._Panel.users_manager.auth(call.from_user)

		if call.data.startswith("ap_switch_"):
			FlagID = call.data[10:]
			self.get_flag(FlagID).switch()
			
			try: 
				self._Bot.edit_message_reply_markup(
					chat_id = User.id,
					message_id = call.message.id,
					reply_markup = InlineKeyboards.FlagsSwitchers(SM_Switchers.SWITCHERS)
				)

			except apihelper.ApiTelegramException: self._Bot.answer_callback_query(call.id, "Состояние не изменено.")

			self._Save()

	def process_message(self, message: types.Message):
		"""
		Обрабатывает текстовое сообщение от пользователя.

		:param message: Данные сообщения.
		:type message: types.Message
		"""

		User = self._Panel.users_manager.auth(message.from_user)

		match message.text:
			case "🕹️ Отобразить": self._SendFlagsSwitchers(User)
			case "↩️ Назад": self.close(User)

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ РАБОТЫ С ПЕРЕКЛЮЧАТЕЛЯМИ <<<<< #
	#==========================================================================================#

	def add_flag(self, id: str, label: str, value: bool, ignore_if_exists: bool = True):
		"""
		Добавляет флаг.

		:param id: Уникальный идентификатор флага. Может содержать только латиницу и цифры.
		:type id: str
		:param label: Подпись для кнопки переключения.
		:type label: str
		:param value: Состояние флага.
		:type value: bool
		:param ignore_if_exists: Если включено, добавление не будет произведено при наличии флага с таким же ID в системе.
		:type ignore_if_exists: bool
		:raise ValueError: Выбрасывается при неверном определении идентификатора флага.
		"""

		IsExists = id in SM_Switchers.SWITCHERS
		if IsExists and not ignore_if_exists: raise ValueError("ID must be unique.")
		elif IsExists: return

		if not self._IsValidID(id): raise ValueError("ID must contain only latin characters and digits.")

		Buffer = dict(SM_Switchers.SWITCHERS)
		Buffer[id] = Flag(id, label, value)
		SM_Switchers.SWITCHERS = MappingProxyType(Buffer)
		self._Save()

	def get_flag(self, id: str) -> Flag:
		"""
		Возвращает флаг.

		:param id: Уникальный идентификатор флага.
		:type id: str
		:return: Логический флаг.
		:rtype: Flag
		:raise KeyError: Выбрасывается при отсутствии флага с переданным ID.
		"""

		return SM_Switchers.SWITCHERS[id]
	
	def remove_flag(self, id: str) -> Flag:
		"""
		Удаляет флаг.

		:param id: Уникальный идентификатор флага.
		:type id: str
		:raise KeyError: Выбрасывается при отсутствии флага с переданным ID.
		"""

		Buffer = dict(SM_Switchers.SWITCHERS)
		del Buffer[id]
		SM_Switchers.SWITCHERS = MappingProxyType(Buffer)
		self._Save()