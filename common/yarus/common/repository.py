
import re
from yarus.common.yarusobject import YarusObject
from yarus.common.exceptions import *

class Repository(YarusObject):

	def __init__(self):
		self.ID = ""
		self.URL = ""
		self.repository = ""
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

	"""
		Setters
	"""
	def setURL(self, URL):
		if URL:
			if re.match("^https?:\/\/([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$", URL):
				self.URL = URL
				return True
			else:
				raise(InvalidValueException("The given URL (" + URL + ") is invalid."))
		else:
			raise(MissingValueException("The URL is missing."))
	def setRepository(self, repository):
		if repository:
			if re.match("^[a-zA-z0-9\-\_\.]*$", repository):
				self.repository = repository
				return True
			else:
				raise(InvalidValueException("The given repository (" + repository + ") is invalid."))
		else:
			raise(MissingValueException("The repository is missing."))
	def setRelease(self, release):
		if release:
			if re.match("^[a-zA-z0-9\-\_\.]*$", release):
				self.release = release
				return True
			else:
				raise(InvalidValueException("The given release (" + release + ") is invalid."))
		else:
			raise(MissingValueException("The release is missing."))
	def setPath(self, path):
		if path:
			if re.match("^[a-zA-z0-9\-\_\.]*$", path):
				self.path = path
				return True
			else:
				raise(InvalidValueException("The given path (" + path + ") is invalid."))
		else:
			raise(MissingValueException("The path is missing."))
	def setComponents(self, components):
		if components:
			if re.match("^[a-zA-z0-9\-\_\.,]*$", components):
				self.components = components
				return True
			else:
				raise(InvalidValueException("The given components (" + components + ") is invalid."))
		else:
			raise(MissingValueException("The components is missing."))
	def setArchitectures(self, architectures):
		if architectures:
			if re.match("^[a-zA-z0-9\-\_\.,]*$", architectures):
				self.architectures = architectures
				return True
			else:
				raise(InvalidValueException("The given architectures (" + architectures + ") is invalid."))
		else:
			raise(MissingValueException("The architectures is missing."))
	def setType(self, rtype):
		if rtype:
			if rtype == 'YUM' or rtype =='APT':
				self.type = rtype
				return True
			else:
				raise(InvalidValueException("The given repository type (" + rtype + ") is invalid."))
		else:
			raise(MissingValueException("The repository type is missing."))
