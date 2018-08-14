
from yarus.common.yarusobject import YarusObject
from yarus.common.check_functions import *
from yarus.common.exceptions import *

class Grouped(YarusObject):

	def __init__(self, client_id="", group_id=""):
		self.client_id = client_id
		self.group_id = group_id

	def load_grouped(self, database, client_id, group_id):
		object_tmp = database.get_grouped(client_id, group_id)
		if not object_tmp:
			return None
		for key, value in vars(self).items():
			setattr(self, key, object_tmp[key])
		return self
	def delete_grouped(self, database):
		database.delete_grouped(self.client_id, self.group_id)
		return True