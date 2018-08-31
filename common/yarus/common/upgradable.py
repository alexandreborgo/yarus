
from yarus.common.yarusobject import YarusObject

class Upgradable(YarusObject):

	def __init__(self, object_id="", object_type="", approved=0, ID="", package_id=""):
		self.object_id = object_id
		self.package_id = package_id
		self.object_type = object_type
		self.approved = approved
		self.ID = ID

	def load_upgradable_by_info(self, database, object_type, object_id, package_id):
		object_tmp = database.get_upgradable_by_info(object_type, object_id, package_id)
		if not object_tmp:
			return None
		for key, value in vars(self).items():
			setattr(self, key, object_tmp[key])
		return self
