

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
			if re.match("^[a-zA-Z0-9]*$", token):
				self.token = token
				self.token_expire = int(time.time()+10800)
				return True
			else:
				raise(InvalidValueException("The given token (" + token + ") is invalid."))
		else:
			raise(InvalidValueException("The token is missing."))

	def setPassword(self, password):
		if password:
			if re.match("^.{4,}$", password):
				self.password = password
				return True
			else:
				raise(InvalidValueException("The given password (" + password + ") is invalid."))
		else:
			raise(InvalidValueException("The password is missing."))

	def setRoleID(self, role_id):
		if role_id:
			if role_id == '1' or role_id == '2' or role_id == '3':
				self.role_id = role_id
				return True
			else:
				raise(InvalidValueException("The given role-id is invalid.")) # invalid
		else:
			raise(InvalidValueException("The role-id is missing.")) # missing

	def setMail(self, mail):
		if mail:
			if re.match("^[a-zA-z0-9\-\_\.]*@[a-zA-z0-9\-\_\.]*\.[a-zA-z0-9\-\_\.]{2,}$", mail):
				self.mail = mail
				return True
			else:
				raise(InvalidValueException("The given mail (" + mail + ") is invalid."))
		else:
			raise(InvalidValueException("The mail is missing."))
