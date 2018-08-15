
"""
	YARUS App is used as context to get log system, configuration and database access
"""

from yarus.common.log import LogSystem
from yarus.common.config import Config
from yarus.common.database import Mysql
from yarus.common.exceptions import DatabaseError

class App:
	""" yarus app """
	def __init__(self, debug=False):
		""" init """
		self.debug = debug
		self.log = None
		self.config = None
		self.database = None

	def start(self):
		""" setup the context """
		# load log system
		self.log = LogSystem(self)
		self.log.debug("Log system loaded.")

		# load configuration settings
		self.config = Config(self)
		if not self.config.start():
			return False
		self.log.debug("Config loaded.")

		# database connection
		try:
			self.database = Mysql(self, self.config.db_host, self.config.db_user, self.config.db_password, self.config.db_database)
			self.database.connect()
			self.database.close()
			self.log.debug("Database connection OK.")
		except DatabaseError as error:
			self.log.error(error)
			return False
		return True