
from yarus.common.yarusobject import YarusObject

class Upgradable(YarusObject):

	def __init__(self, name="", release="", type="", client_id="", approved=0, ID=""):
		self.name = name
		self.release = release
		self.type = type
		self.client_id = client_id
		self.approved = approved
		self.ID = ID

	def load_upgradable(self, database, client_id, package_id):
		object_tmp = database.get_upgradable(client_id, package_id)
		print(object_tmp)
		if not object_tmp:
			return None
		for key, value in vars(self).items():
			setattr(self, key, object_tmp[key])
		return self
