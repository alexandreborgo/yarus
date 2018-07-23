
import re
from yarus.common.yarusobject import YarusObject
from yarus.common.exceptions import *

class Grouped(YarusObject):

	def __init__(self):
		self.client_id = ""
		self.group_id = ""

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

	def setClientID(self, ID):
		if ID:
			if re.match("^[a-zA-z0-9-_]*$", ID):
				self.client_id = ID
				return True
			else:
				raise(InvalidValueException("The given client ID (" + ID + ") is invalid."))
		else:
			raise(MissingValueException("The client ID is missing."))

	def setGroupID(self, ID):
		if ID:
			if re.match("^[a-zA-z0-9-_]*$", ID):
				self.group_id = ID
				return True
			else:
				raise(InvalidValueException("The group ID (" + ID + ") is invalid."))
		else:
			raise(MissingValueException("The group ID is missing."))
