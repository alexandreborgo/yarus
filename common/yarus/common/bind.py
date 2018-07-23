
import re
from yarus.common.yarusobject import YarusObject
from yarus.common.exceptions import *

class Bind(YarusObject):

	def __init__(self, client_id="", repo_id="", channel_id=""):
		self.client_id = client_id
		self.repo_id = repo_id
		self.channel_id = channel_id

	def load_bind(self, database, client_id, repo_id, channel_id):
		object_tmp = database.get_bind(client_id, repo_id, channel_id)
		if not object_tmp:
			return None
		for key, value in vars(self).items():
			setattr(self, key, object_tmp[key])
		return self

	def delete_bind(self, database):
		database.delete_bind(self.client_id, self.repo_id, self.channel_id)
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

	def setRepoID(self, ID):
		if ID:
			if re.match("^[a-zA-z0-9-_]*$", ID):
				self.repo_id = ID
				return True
			else:
				raise(InvalidValueException("The given repository ID (" + ID + ") is invalid."))
		else:
			raise(MissingValueException("The repository ID is missing."))

	def setChannelID(self, ID):
		if ID:
			if re.match("^[a-zA-z0-9-_]*$", ID):
				self.channel_id = ID
				return True
			else:
				raise(InvalidValueException("The channel ID (" + ID + ") is invalid."))
		else:
			raise(MissingValueException("The channel ID is missing."))
