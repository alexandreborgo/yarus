

import re
import time
from yarus.common.yarusobject import YarusObject
from yarus.common.exceptions import *

class User(YarusObject):

	def __init__(self):
		self.ID = ""
		self.name = ""
		self.password = ""
		self.role_id = ""
		self.mail = ""
		self.creation_date = 0
		self.token = ""
		self.token_expire = 0

	def setToken(self, token):
		if token:
			if re.match("^[a-z0-9]*$", token):
				self.token = token
				self.token_expire = int(time.time()+10800)
				return True
			else:
				raise(InvalidValueException("The given token (" + token + ") is invalid."))
		else:
			raise(MissingValueException("The token is missing."))

	def setPassword(self, password):
		if password:
			if re.match("^.{4,}$", password):
				self.password = password
				return True
			else:
				raise(InvalidValueException("The given password (" + password + ") is invalid."))
		else:
			raise(MissingValueException("The password is missing."))

	def setRoleID(self, role_id):
		if role_id:
			if role_id == 'admin' or role_id == 'manager' or role_id == 'client':
				self.role_id = 1
				return 0
			if role_id == 'manager' or role_id == 'client':
				self.role_id = 2
				return 0
			if role_id == 'client':
				self.role_id = 3
				return 0
			else:
				raise(InvalidValueException("The given role-id is invalid.")) # invalid
		else:
			raise(MissingValueException("The role-id is missing.")) # missing

	def setMail(self, mail):
		if mail:
			if re.match("^[a-zA-z0-9\-\_\.]*@[a-zA-z0-9\-\_\.]*\.[a-zA-z0-9\-\_\.]{2,}$", mail):
				self.mail = mail
				return True
			else:
				raise(InvalidValueException("The given mail (" + mail + ") is invalid."))
		else:
			raise(MissingValueException("The mail is missing."))
