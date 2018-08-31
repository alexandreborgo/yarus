
from yarus.common.yarusobject import YarusObject
from yarus.common.check_functions import *
from yarus.common.exceptions import *

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
		self.object_type = ""
		self.object_name = ""
		
	"""
		Setters
	"""
	def setStatus(self, status):
		if check_status(status):
			self.status = status
		else:
			raise(InvalidValueException("The status is missing or invalid."))
