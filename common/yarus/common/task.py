
import re
import time
from yarus.common.yarusobject import YarusObject
from yarus.common.exceptions import *
from yarus.common.const import TASK_ACTIONS

class Task(YarusObject):

	def __init__(self):
		self.ID = ""
		self.status = ""
		self.start_time = 0
		self.object_id = ""
		self.action = ""
		self.manager_id = ""
		self.creation_date = 0
		self.end_time = 0

	"""
		Setters
	"""
	def setStatus(self, status):
		if status:
			if status != "":
				self.status = status
			else:
				raise(InvalidValueException("The task's status is invalid."))
		else:
			raise(MissingValueException("The task's status is missing."))

	def setAction(self, action):
		if action:
			if action in TASK_ACTIONS:
				self.action = action
				return True
			else:
				raise(InvalidValueException("The task's action is invalid."))
		else:
			raise(MissingValueException("The task's action is missing."))

	def setObjectID(self, object_id):
		if object_id:
			if re.match("^[a-zA-z0-9-_]*$", object_id):
				self.object_id = object_id
				return 0
			else:
				raise(InvalidValueException("The given object-id value is invalid."))
		else:
			raise(MissingValueException("The object-id value is missing."))

	def setStartTime(self):
		self.start_time = int(time.time())

	def setEndTime(self):
		self.end_time = int(time.time())
