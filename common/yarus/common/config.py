
import yaml
import sys

from yarus.common.exceptions import MissingValueException
from yarus.common.exceptions import InvalidValueException

class Config:

	# export config value from /etc/yarus/config.yml
	def __init__(self, app):
		self.app = app

	def start(self):
		# open the configuration file
		try:
			config_file = open('/etc/yarus/engine.yml', 'r')
		except IOError as error:
			self.app.log.error("Unable to read configuration file: " + config_file_name)
			self.app.log.error(error)
			return False

		# parse yaml
		try:
			config = yaml.load(config_file)
		except yaml.YAMLError as error:
			self.app.log.error("Configuration file is malformed, it is not good YAML format: " + config_file_name)
			self.app.log.error(error)
			return False

		# extract information
		try:
			# database related information: host, name, username, password
			if 'database' in config:
				if 'host' in config['database']:
					self.db_host = config['database']['host']
				else:
					raise(MissingValueException("Missing database's host information."))
				if 'database' in config['database']:
					self.db_database = config['database']['database']
				else:
					raise(MissingValueException("Missing database's name information."))
				if 'user' in config['database']:
					self.db_user = config['database']['user']
				else:
					raise(MissingValueException("Missing database's username information."))
				if 'password' in config['database']:
					self.db_password = config['database']['password']
				else:
					raise(MissingValueException("Missing database's user password information."))
			else:
				raise(MissingValueException("Missing database information."))

			# local repository information: folder
			self.rp_folder = "/var/www/html/repos"

			# proxy
			if 'proxy' in config:
				if 'host' in config['proxy']:
					self.px_host = config['proxy']['host']
				else:
					raise(MissingValueException("Missing proxy's host information."))
				if 'port' in config['proxy']:
					self.px_port = config['proxy']['port']
				else:
					raise(MissingValueException("Missing proxy's port information."))
				if 'username' in config['proxy']:
					self.px_username = config['proxy']['username']
				else:
					raise(MissingValueException("Missing proxy's username information."))
				if 'password' in config['proxy']:
					self.px_password = config['proxy']['password']
				else:
					raise(MissingValueException("Missing proxy's user password information."))
			else:
				self.px_host = ""
				self.px_port = ""
				self.px_username = ""
				self.px_password = ""

			# engine system related information: address, port
			if 'engine' in config:
				if 'address' in config['engine']:
					self.sv_address = config['engine']['address']
				else:
					raise(MissingValueException("Missing engine's IP address."))
				if 'port' in config['engine']:
					self.sv_port = config['engine']['port']
				else:
					raise(MissingValueException("Missing engine's port."))
			else:
				raise(MissingValueException("Missing engine's information"))

		except MissingValueException as error:
			self.app.log.error(error)
			return False

		return True
