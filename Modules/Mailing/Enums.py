from enum import Enum

class Actions(Enum):
	"""Перечисление режимов взаимодействия."""

	Editing = "editing"

	Mailing = "mailing"
	StopMailing = "mailing_stop"
	CancelMailing = "mailing_cancel"
