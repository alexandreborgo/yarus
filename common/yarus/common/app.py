
from yarus.common.log import LogSystem
from yarus.common.config import Config

class App:

	def __init__(self, debug=False):
		self.debug = debug

	def start(self, component):
		# load log system
		self.log = LogSystem(self)
		self.log.debug("Log system loaded.")

		# load configuration settings
		self.config = Config(self, component)
		if not self.config.start():
			return False
		self.log.debug("Config loaded.")

		return True
