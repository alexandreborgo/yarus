
import re
import time
from yarus.common.exceptions import *

class YarusObject:

	def show(self):
		print()
		for key, value in vars(self).items():
			print(key + " " + str(value))
	def todata(self):
		data = {}
		for key, value in vars(self).items():
			data[key] = str(value)
		return data
	def insert(self, database):
		values = {}
		for key, value in vars(self).items():
			values[key] = value
		database.insert_object("yarus_"+self.__class__.__name__.lower(), values)
		return True
	def load(self, database, ID):
		self.setID(ID)
		object_tmp = database.get_object("yarus_"+self.__class__.__name__.lower(), ID)
		if not object_tmp:
			return None
		for key, value in vars(self).items():
			setattr(self, key, object_tmp[key])
		return self
	def load_by_name(self, database, name):
		self.setName(name)
		object_tmp = database.get_by_name("yarus_"+self.__class__.__name__.lower(), name)
		if not object_tmp:
			return None
		for key, value in vars(self).items():
			setattr(self, key, object_tmp[key])
		return self
	def update(self, database):
		values = {}
		for key, value in vars(self).items():
			values[key] = value
		database.update_object("yarus_"+self.__class__.__name__.lower(), values)
		return True
	def delete(self, database):
		database.delete_object("yarus_"+self.__class__.__name__.lower(), {'ID':self.ID})
		return True

	"""
		Setters
	"""
	def setID(self, ID):
		if ID:
			if re.match("^[a-zA-z0-9-_]*$", ID):
				self.ID = ID
				return True
			else:
				raise(InvalidValueException("The given ID (" + ID + ") is invalid."))
		else:
			raise(MissingValueException("The ID is missing."))

	def setName(self, name):
		if name:
			if re.match("^[a-zA-z0-9-_ ]*$", name):
				self.name = name
				return True
			else:
				raise(InvalidValueException("The given name (" + name + ") is invalid."))
		else:
			raise(MissingValueException("The name is missing."))

	def setDescription(self, description):
		if description:
			if re.match("^[a-zA-z0-9-_. @!:,?]*$", description):
				self.description = description
				return True
			else:
				raise(InvalidValueException("The given description is invalid."))
		else:
			raise(MissingValueException("The description is missing."))

	def setManagerID(self, mid):
		self.manager_id = mid

	def setCreationDate(self):
		self.creation_date = int(time.time())

	def setLastSyncDate(self):
		self.last_sync = int(time.time())
