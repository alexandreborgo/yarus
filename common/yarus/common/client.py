
import re
from yarus.common.yarusobject import YarusObject
from yarus.common.exceptions import *

class Client(YarusObject):

	def __init__(self):
		self.ID = ""
		self.IP = ""
		self.type = ""
		self.version = ""
		self.name = ""
		self.description = ""
		self.distribution = ""
		self.manager_id = 0
		self.last_check = 0
		self.creation_date = 0

	def load_by_ip(self, database, client_ip):
		self.setIP(client_ip)
		object_tmp = database.get_client_by_ip(client_ip)
		if not object_tmp:
			return None
		for key, value in vars(self).items():
			setattr(self, key, object_tmp[key])
		return self

	"""
		Setters
	"""
	def setIP(self, IP):
		if IP:
			if re.match("^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$", IP):
				self.IP = IP
				return True
			else:
				raise(InvalidValueException("The given IP (" + IP + ") is invalid."))
		else:
			raise(MissingValueException("The IP is missing."))

	def setVersion(self, version):
		if version:
			if re.match("^[a-zA-z0-9\-\_\.]*$", version):
				self.version = version
				return True
			else:
				raise(InvalidValueException("The given version (" + version + ") is invalid."))
		else:
			raise(MissingValueException("The version is missing."))

	def setType(self, rtype):
		if rtype:
			if rtype == 'YUM' or rtype =='APT':
				self.type = rtype
				return True
			else:
				raise(InvalidValueException("The given repository type (" + rtype + ") is invalid."))
		else:
			raise(MissingValueException("The repository type is missing."))

	def setDistribution(self, distribution):
		if distribution:
			if re.match("^[a-zA-z0-9\-\_\.]*$", distribution):
				self.distribution = distribution
				return True
			else:
				raise(InvalidValueException("The given distribution (" + distribution + ") is invalid."))
		else:
			raise(MissingValueException("The distribution is missing."))
