
import time

from yarus.common.check_functions import *
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

	def setID(self, ID):
		if check_id(ID):
			self.ID = ID
		else:
			raise(InvalidValueException("The ID is missing or invalid."))
	def setName(self, name):
		if check_name(name):
			self.name = name
		else:
			raise(InvalidValueException("The name is missing or invalid."))
	def setDescription(self, description):
		if check_description(description):
			self.description = description
		else:
			raise(InvalidValueException("The description is missing or invalid."))		
	def setCreationDate(self):
		self.creation_date = int(time.time())
	def setLastSyncDate(self):
		self.last_sync = int(time.time())
	def setStartTime(self):
		self.start_time = int(time.time())
	def setEndTime(self):
		self.end_time = int(time.time())
	def setType(self, rtype):
		if check_type(rtype):
			self.type = rtype
		else:
			raise(InvalidValueException("The type is missing or invalid."))		
	def setDistribution(self, distribution):
		if check_distribution(distribution):
			self.distribution = distribution
		else:
			raise(InvalidValueException("The distribution is missing or invalid."))
	def setClientID(self, ID):
		if check_id(ID):
			self.client_id = ID
		else:
			raise(InvalidValueException("The client ID is missing or invalid."))
	def setRepoID(self, ID):
		if check_id(ID):
			self.repo_id = ID
		else:
			raise(InvalidValueException("The repository ID is missing or invalid."))
	def setChannelID(self, ID):
		if check_id(ID):
			self.channel_id = ID
		else:
			raise(InvalidValueException("The channel ID is missing or invalid."))
	def setGroupID(self, group_id):
		if check_id(group_id):
			self.group_id = group_id
		else:
			raise(InvalidValueException("The group ID is missing or invalid."))
	def setManagerID(self, manager_id):
		self.manager_id = manager_id
		return True
	def setObjectID(self, object_id):
		if check_id(object_id):
			self.object_id = object_id
		else:
			raise(InvalidValueException("The object ID is missing or invalid."))
	def setAction(self, action):
		if check_action(action):
			self.action = action
		else:
			raise(InvalidValueException("The action is missing or invalid."))
	