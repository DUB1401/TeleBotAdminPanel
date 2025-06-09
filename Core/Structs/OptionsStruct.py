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

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#
	
	def __ParseData(self):
		"""Парсит параметры."""

		if self.__User.has_property("ap"):
			Data: dict[str, Any] = self.__User.get_property("ap")

			for Key in self.__Data.keys():
				if Key not in Data.keys(): Data[Key] = self.__Data[Key]

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
			"temp_mailing_content": []
		}

		self.__ParseData()
		
		self.__Mailing = MailingData(self, self.__Data)

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