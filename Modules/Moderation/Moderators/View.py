from ..ModerationOptions import ModerationOptions
from .. import InlineKeyboards

from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from dublib.TelebotUtils.Users import UserData

from .Base import BaseModerator

class Moderator_View(BaseModerator):
	
	def run(self, user: "UserData"):
		"""
		Запускает обработку очереди модерации.

		:param user: Пользователь, выполняющий обработку.
		:type user: UserData
		"""

		ModuleData = ModerationOptions(user)

		if not self._Storage.first_element:
			self._Bot.send_message(
				chat_id = user.id,
				text = "Контент для просмотра отсутствует."
			)
			ModuleData.drop()
			return

		if ModuleData.value:
			Text = ModuleData.value

		else:
			Text = self._Storage.first_element
			ModuleData.set_value(Text)

		if Text:
			ID = self._Bot.send_message(
				chat_id = user.id,
				text = Text,
				parse_mode = "HTML",
				reply_markup = InlineKeyboards.View()
			).id
			ModuleData.set_canvas_id(ID)