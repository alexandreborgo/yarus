import datetime

class LogSystem:

	def __init__(self, app, log_file='/var/log/yarus/yarus.log'):
		self.log_file = log_file
		self.app = app

	def debug(self, message):
		if self.app.debug:
			print("DEBUG: " + message)

	def error(self, errmsg):
		print("ERROR: " + errmsg)
		try:
			file = open(self.log_file, 'a')
			file.write(str(datetime.datetime.now()) + ": " + errmsg + "\n")
			file.close()
		except IOError as error:
			print("Unable to write the error into the log file: " + self.log_file)
			print("ERROR: " + error)
			return False

	def settasklogfile(self, task):
		self.task_log_file = '/var/log/yarus/tasks/' + task.ID + '.log'

	def logtask(self, message):
		print(str(message))
		try:
			file = open(self.task_log_file, 'a')
			file.write(str(message) + "\n")
			file.close()
		except IOError as error:
			print("Unable to write the error into the log task file: " + self.task_log_file)
			print(error)
			return False
