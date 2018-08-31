
from yarus.common.yarusobject import YarusObject
from yarus.common.exceptions import *

class Linkrcs(YarusObject):

	def __init__(self):
		self.ID = ""
		self.distribution = ""
		self.release = ""
		self.architecture = ""
		self.channels = ""
		self.creation_date = 0
		self.manager_id = 0
		
	def load_linkrcs_by_info(self, database, distribution, release, architecture):
		object_tmp = database.get_linkrcs_by_info(distribution, release, architecture)
		if not object_tmp:
			return None
		for key, value in vars(self).items():
			setattr(self, key, object_tmp[key])
		return self