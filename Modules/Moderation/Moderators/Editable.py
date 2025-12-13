from ..ModerationOptions import ModerationOptions
from .. import InlineKeyboards

from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from dublib.TelebotUtils.Users import UserData

from .Base import BaseModerator

class Moderator_Editable(BaseModerator):
	
	def run(self, user: "UserData"):
		"""
		Запускает обработку очереди модерации.

		:param user: Пользователь, выполняющий обработку.
		:type user: UserData
		"""

		Text = self._Storage.first_element
		ModuleData = ModerationOptions(user)

		if Text:
			ModuleData.set_value(Text)
			self._Bot.send_message(
				chat_id = user.id,
				text = Text,
				parse_mode = "HTML",
				reply_markup = InlineKeyboards.Editable()
			)

		else:
			self._Bot.send_message(
				chat_id = user.id,
				text = "Контент для модерации отсутствует."
			)
			ModuleData.drop()