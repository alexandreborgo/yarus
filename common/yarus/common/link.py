
from yarus.common.yarusobject import YarusObject
from yarus.common.check_functions import *
from yarus.common.exceptions import *

class Link(YarusObject):

	def __init__(self, repo_id="", channel_id=""):
		self.repo_id = repo_id
		self.channel_id = channel_id

	def load_link(self, database, channel_id, repo_id):
		object_tmp = database.get_link(channel_id, repo_id)
		if not object_tmp:
			return None
		for key, value in vars(self).items():
			setattr(self, key, object_tmp[key])
		return self
	def delete_link(self, database):
		database.delete_link(self.channel_id, self.repo_id)
		return True