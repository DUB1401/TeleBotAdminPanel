from dublib.TelebotUtils.Users import UserData

from typing import Any

#==========================================================================================#
# >>>>> ВСПОМОГАТЕЛЬНЫЕ СТРУКТУРЫ ДАННЫХ <<<<< #
#==========================================================================================#

class MailingData:
	"""Данные рассылки."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def button(self) -> "ButtonData":
		"""Данные кнопки."""

		return self.__Button
	
	@property
	def is_mailing(self) -> bool:
		"""Состояние: активна ли рассылка."""

		return self.__Data["is_mailing"]
	
	@property
	def sampling(self) -> int | None:
		"""Количество выбранных для рассылки человек."""

		return self.__Data["sampling"]

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, options: "OptionsStruct", data: dict):
		"""
		Данные рассылки.

		:param options: Параметры панели управления.
		:type options: Options
		:param data: Словарь параметров панели управления.
		:type data: dict
		"""

		self.__Options = options
		self.__Data = data

		self.__Button = ButtonData(self.__Options, self.__Data)

	def add_attachment(self, type: str, file_id: str):
		"""
		Прикрепляет вложение.

		:param type: Строковый идентификатор типа файла: *document*, *photo*, *video* или *audio*.
		:type type: str
		:param file_id: Идентификатор файла.
		:type file_id: str
		:raises ValueError: Выбрасывается при указании неподдерживаемого типа.
		"""

		if type not in ("document", "photo", "video", "audio"): raise ValueError(f"Unsupportable type \"{type}\".")
		self.__Data["mailing_content"].append({"type": type, "file_id": file_id})
		self.__Options.save()

	def drop(self):
		"""Сбрасывает данные сообщения."""

		self.__Data["mailing_caption"] = None
		self.__Data["mailing_content"] = list()
		self.__Options.save()

	def set_caption(self, caption: str | None):
		"""
		Задаёт текст рассылки. Поддерживает HTML-форматирование Telegram.

		:param caption: Текст рассылки.
		:type caption: str | None
		"""

		self.__Data["mailing_caption"] = caption
		self.__Options.save()

	def set_sampling(self, sampling: int | None):
		"""
		Задаёт количество человек для рассылки. Указать `None` для выбора всех.

		:param sampling: Параметры выборки.
		:type sampling: int | None
		"""

		self.__Data["sampling"] = sampling
		self.__Options.save()

	def set_status(self, status: bool):
		"""
		Задаёт статус рассылки.

		:param status: Статус рассылки.
		:type status: bool
		"""

		self.__Data["mailing"] = status
		self.__Options.save()

	def stash(self):
		"""Помещает данные сообщения рассылки во временные ключи."""

		self.__Data["temp_mailing_caption"] = self.__Data["mailing_caption"]
		self.__Data["temp_mailing_content"] = self.__Data["mailing_content"]
		self.__Data["mailing_caption"] = None
		self.__Data["mailing_content"] = list()
		self.__Options.save()

	def unstash(self):
		"""Восстанавливает данные сообщения рассылки из временных ключей."""

		self.__Data["mailing_caption"] = self.__Data["temp_mailing_caption"]
		self.__Data["mailing_content"] = self.__Data["temp_mailing_content"]
		self.__Data["temp_mailing_caption"] = None
		self.__Data["temp_mailing_content"] = list()
		self.__Options.save()

class ButtonData:
	"""Данные кнопки."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def is_enabled(self) -> bool:
		"""Состояние: активна ли кнопка."""

		return all((self.label, self.link))

	@property
	def label(self) -> str | None:
		"""Надпись для отображения на кнопке."""

		return self.__Data["button_label"]

	@property
	def link(self) -> str | None:
		"""Ссылка для перехода по кнопке."""

		return self.__Data["button_link"]
	
	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, options: "Options", data: dict):
		"""
		Данные кнопки.

		:param options: Параметры панели управления.
		:type options: Options
		:param data: Словарь параметров панели управления.
		:type data: dict
		"""

		self.__Options = options
		self.__Data = data

	def disable(self):
		"""Отключает кнопку через удаление её данных."""

		self.__Data["button_label"] = None
		self.__Data["button_link"] = None
		self.__Options.save()

	def set_label(self, label: str | None):
		"""
		Задаёт надпись для кнопки.

		:param label: Текст надписи.
		:type label: str | None
		"""

		self.__Data["button_label"] = label
		self.__Options.save()

	def set_link(self, link: str | None):
		"""
		Задаёт ссылку для кнопки.

		:param link: Ссылка.
		:type link: str | None
		"""

		self.__Data["button_link"] = link
		self.__Options.save()

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class OptionsStruct:
	"""Параметры панели управления."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def is_open(self) -> bool:
		"""Состояние: открыта ли панель управления."""

		return self.__Data["is_open"]
	
	@property
	def mailing(self) -> MailingData:
		"""Данные рассылки."""

		return self.__Mailing
	
	@property
	def moderated_value(self) -> str | None:

		return self.__Data["moderated_value"]

	@property
	def moderator_index(self) -> int | None:
		"""Данные рассылки."""

		return self.__Data["moderator_index"]

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#
	
	def __ParseData(self):
		"""Парсит параметры."""

		if self.__User.has_property("ap"):
			Data: dict[str, Any] = self.__User.get_property("ap")

			for Key in self.__Data:
				if Key not in Data: Data[Key] = self.__Data[Key]

			self.__Data = Data
			
		else: self.save()

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, user: UserData):
		"""
		Параметры обмена энергией пользователя.

		:param user: Данные пользователя.
		:type user: UserData
		"""

		self.__User = user

		self.__Data = {
			"is_open": True,

			"sampling": None,
			"mailing": False,
			"mailing_caption": None,
			"mailing_content": [],
			"button_label": None,
			"button_link": None,
			"temp_mailing_caption": None,
			"temp_mailing_content": [],

			"moderated_value": None,
			"moderator_index": None,
			"edited_text": None,
		}

		self.__ParseData()
		
		self.__Mailing = MailingData(self, self.__Data)

	def __getitem__(self, key: str) -> Any:
		"""
		Возвращает значение параметра.

		:param key: Ключ параметра.
		:type key: str
		:return: Значение параметра.
		:rtype: Any
		"""

		return self.__Data[key]

	def save(self):
		"""Сохраняет параметры."""

		self.__User.set_property("ap", self.__Data)

	def set_open_state(self, status: bool):
		"""
		Задаёт состояние: открыта ли панель управления.

		:param status: Состояние.
		:type status: bool
		"""

		self.__Data["is_open"] = status
		self.save()

	#==========================================================================================#
	# >>>>> МЕТОДЫ ВЗАИМОДЕЙСТВИЯ С МОДЕРАТОРАМИ <<<<< #
	#==========================================================================================#

	def drop_moderator_index(self):
		"""Сбрасывает индекс модератора."""

		if "moderator_index" in self.__Data.keys(): del self.__Data["moderator_index"]
		self.save()

	def remember_moderator_index(self, index: int):
		"""
		Запоминает индекс текущего модератора.

		:param index: Индекс модератора.
		:type index: int
		"""

		self.__Data["moderator_index"] = index
		self.save()

	def set_moderated_value(self, value: str | None):
		self.__Data["moderated_value"] = value
		self.save()

	def set_edited_text(self, text: str):
		"""
		Сохраняет отредактированный текст.

		:param text: Отредактированный текст.
		:type text: str
		"""

		self.__Data["edited_text"] = text
		self.save()

	def get_edited_text(self, autoremove: bool = True) -> str | None:
		"""
		Возвращает отредактированный текст.

		:param autoremove: Указывает, нужно ли удалить текст из свойств пользователя после вызова метода.
		:type autoremove: bool
		:return: Отредактированный текст или `None` в случае отсутствия оного.
		:rtype: str
		"""

		Text = self.__Data["edited_text"]

		if autoremove and Text: 
			self.__Data["edited_text"] = None
			self.save()

		return Text