
from yarus.common.yarusobject import YarusObject
from yarus.common.check_functions import *
from yarus.common.exceptions import *

class Repository(YarusObject):

	def __init__(self):
		self.ID = ""
		self.URL = ""
		self.distribution = ""
		self.release = ""
		self.path = ""
		self.components = ""
		self.architectures = ""
		self.type = ""
		self.last_sync = 0
		self.creation_date = 0
		self.name = ""
		self.description = ""
		self.manager_id = 0

	def setURL(self, URL):
		if check_url(URL):
			self.URL = URL
		else:
			raise(InvalidValueException("The URL is missing or invalid."))
	def setRelease(self, release):
		if check_release(release):
			self.release = release
		else:
			raise(InvalidValueException("The release is missing or invalid."))
	def setPath(self, path):
		if check_path(path):
			self.path = path
		else:
			raise(InvalidValueException("The path is missing or invalid."))
	def setComponents(self, components):
		if check_components(components):
			self.components = components
		else:
			raise(InvalidValueException("The components is missing or invalid."))
	def setArchitectures(self, architectures):
		if check_architectures(architectures):
			self.architectures = architectures
		else:
			raise(InvalidValueException("The architectures is missing or invalid."))
