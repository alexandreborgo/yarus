import datetime

class LogSystem:

	def __init__(self, app, log_file='/opt/yarus/log/yarus.log'):
		self.log_file = log_file
		self.app = app

	def debug(self, message):
		if self.app.debug:
			print("DEBUG: " + str(message))
			try:
				file = open("/opt/yarus/log/debug.log", 'a')
				file.write("ERROR " + str(datetime.datetime.now()) + ": " + str(message) + "\n")
				file.close()
			except IOError as error:
				print("ERROR: " + str(message))
				print("Unable to write the error into the log file: " + self.log_file)
				print("ERROR: " + str(error))
				return False

	def error(self, message):
		try:
			file = open(self.log_file, 'a')
			file.write("ERROR " + str(datetime.datetime.now()) + ": " + str(message) + "\n")
			file.close()
		except IOError as error:
			print("ERROR: " + str(message))
			print("Unable to write the error into the log file: " + self.log_file)
			print("ERROR: " + str(error))
			return False

	def log(self, message):
		try:
			file = open(self.log_file, 'a')
			file.write(str(datetime.datetime.now()) + ": " + str(message) + "\n")
			file.close()
		except IOError as error:
			print("ERROR: " + str(message))
			print("Unable to write the error into the log file: " + self.log_file)
			print("ERROR: " + str(error))
			return False

	def settasklogfile(self, ID):
		self.task_log_file = '/opt/yarus/log/tasks/' + ID + '.log'

	def logtask(self, message):
		try:
			file = open(self.task_log_file, 'a')
			file.write(str(message) + "\n")
			file.close()
		except IOError as error:
			print("ERROR: " + str(message))
			print("Unable to write the error into the log task file: " + self.task_log_file)
			print("ERROR: " + str(error))
			return False
