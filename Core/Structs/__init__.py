from .OptionsStruct import OptionsStruct

import enum

class UserInput(enum.Enum):
	ButtonLabel = "ap_button_label"
	ButtonLink = "ap_button_link"
	Message = "ap_message"
	Sampling = "ap_sampling"
	Username = "ap_username"
	EditedText = "ap_edited_text"