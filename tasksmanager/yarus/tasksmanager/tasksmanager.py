
import sys
import time

from yarus.tasksmanager.apptasksmanager import AppTasksManager
from yarus.tasksmanager import actions
from yarus.common.task import Task
from yarus.common.exceptions import *
from yarus.common.const import TASK_ACTIONS

WAIT = 20

class YarusTasksManager():

	def __init__(self):

		# start the app context
		self.app = AppTasksManager()

		if not self.app.start():
			sys.exit(1)

	def checkForTasks(self):
		info = self.app.database.get_pending_task()
		if info:
			return Task().load(self.app.database, info["ID"])
		else:
			return None

	def alterTaskStatus(self, task, new_status):
		try:
			task.setStatus(new_status)
			task.update(self.app.database)
		except DatabaseError as error:
			self.app.log.logtask(str(error))
			return False
		return True

	def execute(self, task):
		task.setStartTime()
		task.update(self.app.database)
		self.app.log.settasklogfile(task)
		self.alterTaskStatus(task, 'running')

		if task.action in TASK_ACTIONS:
			try:
				action = getattr(actions, task.action)
				result = action(self.app, task.object_id)
			except Exception as error:
				self.alterTaskStatus(task, 'failed')
				self.app.log.logtask("The following error occured during the task :")
				self.app.log.logtask(error)
				task.setEndTime()
				task.update(self.app.database)
				self.app.log.logtask("Executed in " + str(task.end_time - task.start_time) + " seconds.")
				return False

			if result:
				self.alterTaskStatus(task, 'completed')
				self.app.log.logtask("The task " + task.ID + " was succesfully executed.")
				task.setEndTime()
				task.update(self.app.database)
				self.app.log.logtask("Executed in " + str(task.end_time - task.start_time) + " seconds.")
				return True
			else:
				self.alterTaskStatus(task, 'failed')
				self.app.log.logtask("The task " + task.ID + " failed during its execution.")
				task.setEndTime()
				task.update(self.app.database)
				return False
		else:
			self.alterTaskStatus(task, 'failed')
			self.app.log.logtask("The action: '" + task.action + "' isn't recognized as a task action.")
			task.setEndTime()
			task.update(self.app.database)
			return False

	def run(self):
		while True:
			# check for pending task
			self.app.database.connect()
			task = self.checkForTasks()
			self.app.database.close()
			if task:
				print("The task (ID: " + str(task.ID) + ") will be executed. Action: " + task.action + ". On: " + str(task.object_id))
				self.app.database.connect()
				self.execute(task)
				self.app.database.close()
			else:
				print("No task to execute.")
				print("Waiting for " + str(WAIT) + " seconds before next check.")
				time.sleep(WAIT)
