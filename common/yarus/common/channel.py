
from yarus.common.yarusobject import YarusObject

class Channel(YarusObject):

	def __init__(self):
		self.ID = ""
		
		self.name = ""
		self.description = ""
		self.distribution = ""
		self.release = ""

		self.manager_id = 0

		self.creation_date = 0
		self.last_sync = 0

	def load_channel_by_info(self, database, distribution, version):
		object_tmp = database.get_channel_by_info(distribution, version)
		if not object_tmp:
			return None
		for key, value in vars(self).items():
			setattr(self, key, object_tmp[key])
		return self
