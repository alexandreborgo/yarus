
class MissingValueException(Exception):
	pass

class InvalidValueException(Exception):
	pass

class FailStartException(Exception):
	pass

class DoesNotExist(Exception):
	pass

class DatabaseError(Exception):
	pass

class PermissionError(Exception):
	pass