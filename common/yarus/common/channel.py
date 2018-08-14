
from yarus.common.yarusobject import YarusObject

class Channel(YarusObject):

	def __init__(self):
		self.ID = ""
		
		self.name = ""
		self.description = ""

		self.manager_id = 0

		self.creation_date = 0
		self.last_sync = 0
