
from yarus.common.yarusobject import YarusObject

class Channel(YarusObject):

	def __init__(self):
		self.ID = ""
		self.last_sync = None
		self.creation_date = None
		self.name = ""
		self.description = ""
		self.manager_id = 0
