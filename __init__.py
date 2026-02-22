from .Core.PanelOptions import PanelOptions
from .Core.Tree import Tree

from dublib.TelebotUtils import TeleMaster

from typing import Callable, TYPE_CHECKING
from os import PathLike
import os

from telebot import TeleBot, types

if TYPE_CHECKING:
	from .Core.BaseModule import BaseModule
	from .Core.PanelOptions import Path

	from dublib.TelebotUtils import UserData, UsersManager

#==========================================================================================#
# >>>>> КОНТЕЙНЕРЫ ОБРАБОТЧИКОВ ВЗАИМОДЕЙСТВИЙ <<<<< #
#==========================================================================================#

class Decorators:
	"""Наборы декораторов."""

	def __init__(self, panel: "Panel"):
		"""
		Наборы декораторов.

		:param panel: Панель управления.
		:type panel: Panel
		"""

		self.__Panel = panel

		self.__UsersManager = self.__Panel.users_manager
		self.__Bot = self.__Panel.bot

	def inline_keyboards(self):
		"""Набор декораторов: Inline-кнопки."""

		@self.__Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("ap_"))
		def Callback(Call: types.CallbackQuery):
			User = self.__UsersManager.auth(Call.from_user)
			Options = self.__Panel.load_options_for_user(User)

			if Options.current_module:
				ModuleObject: "BaseModule" = self.__Panel.get_module_object(Options.current_module)
				ModuleObject.process_call(Call)

class Procedures:
	"""Наборы процедур."""

	def __init__(self, panel: "Panel"):
		"""
		Наборы процедур.

		:param panel: Панель управления.
		:type panel: Panel
		"""

		self.__Panel = panel

		self.__UsersManager = self.__Panel.users_manager
		self.__Bot = self.__Panel.bot

	def attachments(self, message: types.Message) -> bool:
		"""
		Обрабатывает сообщение с вложением.

		:param message: Данные сообщения.
		:type message: types.Message
		:return: Возвращает `True`, если сообщение предназначалось для обработки панелью.
		:rtype: bool
		"""

		User = self.__UsersManager.auth(message.from_user)
		Options = self.__Panel.load_options_for_user(User)
		if not Options.is_open: return False

		if Options.current_module:
			ModuleObject: "BaseModule" = self.__Panel.get_module_object(Options.current_module)
			ModuleObject.process_attachment(message)

		return True

	def text(self, message: types.Message) -> bool:
		"""
		Обрабатывает сообщение.

		:param message: Данные сообщения.
		:type message: types.Message
		:return: Возвращает `True`, если сообщение предназначалось для обработки панелью.
		:rtype: bool
		"""

		User = self.__UsersManager.auth(message.from_user)
		Options = self.__Panel.load_options_for_user(User)
		if not Options.is_open: return False

		if Options.current_module:
			ModuleObject: "BaseModule" = self.__Panel.get_module_object(Options.current_module)
			ModuleObject.process_message(message)
			return True

		Layer = self.__Panel.tree.get_layer_by_path(Options.path) if Options.path else self.__Panel.tree.data

		if Options.path.value and message.text == "↩️ Назад":
			Options.path.up()
			self.__Bot.send_message(
				chat_id = User.id,
				text = f"Переход в предыдущий каталог.",
				reply_markup = self.__Panel.get_current_layer_reply_markup(User)
			)

		for Element in Layer:
			if message.text == Element:

				if type(Layer[Element]) == dict:
					Options.path.append(Element)
					self.__Bot.send_message(
						chat_id = User.id,
						text = f"Переход в каталог <b>{Element}</b>.",
						parse_mode = "HTML",
						reply_markup = self.__Panel.get_current_layer_reply_markup(User)
					)

				else:
					Options.set_current_module(Layer[Element].__name__)
					self.__Panel.get_module_object(Options.current_module).open(User)

		return True

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class Panel:
	"""Панель управления."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def bot(self) -> TeleBot:
		"""Бот Telegram."""

		return self.__Bot

	@property
	def close_callback(self) -> Callable | None:
		"""Функция, вызываемая при закрытии панели администрирования."""

		return self.__CloseCallback
	
	@property
	def master_bot(self) -> TeleMaster:
		"""Набор дополнительного функционала для бота Telegram."""

		return self.__Master

	@property
	def password(self) -> str:
		"""Пароль для доступа в панель управления."""

		return self.__Password
	
	@property
	def tree(self) -> Tree:
		"""Древо навигации по модулям."""

		return self.__Tree

	@property
	def users_manager(self) -> "UsersManager":
		"""Менеджер пользователей."""

		return self.__UsersManager

	@property
	def workdir(self) -> PathLike:
		"""Каталог для хранения файлов панели управления."""

		return self.__WorkDirectory

	#==========================================================================================#
	# >>>>> КОНТЕЙНЕРЫ ОБРАБОТЧИКОВ ВЗАИМОДЕЙСТВИЙ <<<<< #
	#==========================================================================================#

	@property
	def decorators(self) -> Decorators:
		"""Наборы декораторов."""

		return self.__Decorators

	@property
	def procedures(self) -> Procedures:
		"""Наборы процедур."""

		return self.__Procedures

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __BuilReplyMarkupForLayer(self, path: "Path") -> types.ReplyKeyboardMarkup:
		"""
		Строит Reply-интерфейс для слоя древа по указанному пути.

		:param path: Путь для построения.
		:type path: Path
		:return: Reply-интерфейс.
		:rtype: types.ReplyKeyboardMarkup
		"""

		Layer = self.__Tree.get_layer_by_path(path) if path.value else self.__Tree.data
		
		Menu = types.ReplyKeyboardMarkup(resize_keyboard = True)
		for Element in Layer: Menu.add(types.KeyboardButton(Element))
		if path.value: Menu.add(types.KeyboardButton("↩️ Назад"))

		return Menu

	def __GetModulesFromTree(self, tree: dict) -> list:
		"""
		Возвращает список модулей.

		:param tree: Древо слоёв.
		:type tree: dict
		:return: Список модулей.
		:rtype: list
		"""

		ModulesList = list()

		for Element in tree.values():
			if type(Element) == dict: ModulesList += self.__GetModulesFromTree(Element)
			else: ModulesList.append(Element)

		return ModulesList

	def __InitializeModules(self):
		"""Инициализирует модули древа."""

		ModulesList = self.__GetModulesFromTree(self.__Tree.data)

		for CurrentModule in ModulesList:
			if CurrentModule.__name__ not in self.__Modules: self.__Modules[CurrentModule.__name__] = CurrentModule(self)

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, bot: TeleBot, users_manager: "UsersManager", password: str):
		"""
		Панель управления.

		:param panel: Панель управления.
		:type panel: Panel
		:param bot: Бот Telegram.
		:type bot: TeleBot
		:param password: Пароль для входа в панель управления.
		:type password: str
		"""

		self.__Bot = bot
		self.__UsersManager = users_manager
		self.__Password = password

		self.__Master = TeleMaster(self.__Bot)
		self.__Decorators = Decorators(self)
		self.__Procedures = Procedures(self)

		self.__CloseCallback: Callable | None = None
		self.__CallbackArguments = tuple()
		self.__Modules = dict()
		self.__Tree = Tree()
		self.__WorkDirectory = ".tbap"

		if not os.path.exists(self.__WorkDirectory): os.makedirs(self.__WorkDirectory)

	def login(self, user: "UserData", password: str | None = None) -> bool:
		"""
		Проверяет, имеет ли пользователь доступ к панели управления. При передаче пароля выполняет авторизацию (выдаётся разрешение _ap_access_, при наличии которого повторный ввод пароля не требуется).

		:param user: Данные пользователя.
		:type user: UserData
		:param password: Введённый пользователем пароль.
		:type password: str
		:return: Возвращает `True`, если доступ разрешён.
		:rtype: bool
		"""

		if not user.has_permissions("ap_access") and password:
			if password == self.__Password: user.add_permissions("ap_access")

		return user.has_permissions("ap_access")

	def close(self, user: "UserData"):
		"""
		Закрывает панель управления.

		:param user: Данные пользователя.
		:type user: UserData
		"""

		Options: PanelOptions = self.load_options_for_user(user)

		if Options.current_module:
			Module: BaseModule = self.get_module_object(Options.current_module)
			Module.close(user)

		Options.set_open_state(False)
		if self.__CloseCallback: self.__CloseCallback(user, self.__CallbackArguments)

	def get_current_layer_reply_markup(self, user: "UserData") -> types.ReplyKeyboardMarkup:
		"""
		Возвращает Reply-интерфейс текущего слоя.

		:param user: Данные пользователя.
		:type user: UserData
		:return: Reply-интерфейс текущего слоя.
		:rtype: types.ReplyKeyboardMarkup
		"""

		Options: PanelOptions = self.load_options_for_user(user)

		return self.__BuilReplyMarkupForLayer(Options.path)

	def get_module_object(self, module: str) -> "BaseModule":
		"""
		Получает объект модуля.

		:param module: Имя модуля.
		:type module: str
		:return: Объект модуля.
		:rtype: BaseModule
		"""

		return self.__Modules[module]
	
	def get_module_workdir(self, module: str) -> PathLike:
		"""
		Получает каталог для хранения файлов модуля.

		:param module: Имя модуля.
		:type module: str
		:return: Путь к каталогу.
		:rtype: PathLike
		"""

		Path = f"{self.__WorkDirectory}/{module}"
		if not os.path.exists(Path): os.makedirs(Path)

		return Path

	def load_options_for_user(self, user: "UserData") -> PanelOptions:
		"""
		Загружает параметры панели управления в объекты пользователя под ключом _ap_options_.

		:param user: Данные пользователя.
		:type user: UserData
		:return: Параметры панели управления.
		:rtype: PanelOptions
		"""

		try:
			return user.get_object("ap_options")
		
		except KeyError:
			Options = PanelOptions(user)
			user.attach_object("ap_options", Options)
			return user.get_object("ap_options")

	def open(self, user: "UserData") -> types.ReplyKeyboardMarkup | None:
		"""
		Выполняет авторизацию пользователя и открывает панель управления. При верном пароле .

		:param user: Данные пользователя.
		:type user: UserData
		:return: Reply-интерфейс корня панели управления или `None` при отсутствии доступа.
		:rtype: types.ReplyKeyboardMarkup | None
		"""
		
		if user.has_permissions("ap_access"):
			Options: PanelOptions = self.load_options_for_user(user)
			Options.set_open_state(True)
			Options.set_current_module(None)
			return self.__BuilReplyMarkupForLayer(Options.path)
		
	def set_close_callback(self, callback: Callable | None, args: tuple | None = None):
		"""
		Задаёт Callback-функцию, вызываемую при закрытии панели.

		:param callback: Вызываемая функция, принимающая в качестве первого аргумента структуру `UserData`, а второго – набор дополнительных аргументов.
		:type callback: Callable | None
		:param args: Набор дополнительных аргументов.
		:type args: tuple | None
		"""

		self.__CloseCallback = callback
		self.__CallbackArguments = args or tuple()

	def set_tree(self, tree: dict):
		"""
		Задаёт древо навигации.

		:param tree: Древо навигации.
		:type tree: dict
		"""

		self.__Tree.set(tree)
		self.__InitializeModules()

	def set_workdir(self, directory: PathLike):
		"""
		Задаёт каталог хранения файлов панели управления.

		:param directory: Путь к каталогу.
		:type directory: PathLike
		"""

		self.__WorkDirectory = directory
		if not os.path.exists(self.__WorkDirectory): os.makedirs(self.__WorkDirectory)