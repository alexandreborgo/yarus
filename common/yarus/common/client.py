
from yarus.common.yarusobject import YarusObject
from yarus.common.exceptions import *

class Client(YarusObject):

	def __init__(self):
		self.ID = ""

		self.IP = ""

		self.name = ""
		self.description = ""

		self.distribution = ""
		self.version = ""
		self.type = ""

		self.manager_id = 0

		self.last_check = 0
		self.creation_date = 0

	def load_by_ip(self, database, client_ip):
		# check if the IP is valid by setting it
		self.setIP(client_ip)
		object_tmp = database.get_client_by_ip(client_ip)
		if not object_tmp:
			return None
		for key, value in vars(self).items():
			setattr(self, key, object_tmp[key])
		return self

	def setIP(self, IP):
		if check_ip(IP):
			self.IP = IP
		else:
			raise(InvalidValueException("The client IP is missing or invalid."))
	def setVersion(self, version):
		if check_version(version):
			self.version = version
		else:
			raise(InvalidValueException("The client version is missing or invalid."))