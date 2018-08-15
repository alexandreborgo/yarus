
import sys
import time
import threading

from yarus.common.app import App
from yarus.tasksmanager import actions
from yarus.common.task import Task
from yarus.common.exceptions import *
from yarus.common.const import TASK_ACTIONS

WAIT = 20

class YarusTasksManager():

	def __init__(self):

		# start the app context
		self.app = App()

		if not self.app.start():
			sys.exit(1)

	def checkForTasks(self):
		info = self.app.database.get_pending_task()
		if info:
			return Task().load(self.app.database, info["ID"])
		else:
			return None

	def alterTaskStatus(self, app, task, new_status):
		try:
			task.setStatus(new_status)
			task.update(app.database)
		except DatabaseError as error:
			app.log.logtask(str(error))
			return False
		return True

	def execute(self, task):

		# start the app context
		app = App()

		if not app.start():
			return False

		app.log.settasklogfile(task.ID)
		
		try:
			app.database.connect()

			# set the start date
			task.setStartTime()
			task.update(app.database)

			# set the status of the task to running 
			self.alterTaskStatus(app, task, 'running')

			if task.action in TASK_ACTIONS:

				# get the function of the action and execute it
				try:
					action = getattr(actions, task.action)
					result = action(app, task.object_id)

				except Exception as error:
					self.alterTaskStatus(app, task, 'failed')
					app.log.logtask("The following error occured during the task :")
					app.log.logtask(error)
					result = False
				
				# check the result
				if result:
					self.alterTaskStatus(app, task, 'completed')
					app.log.logtask("The task " + task.ID + " was succesfully executed.")			
				else:
					self.alterTaskStatus(app, task, 'failed')
					app.log.logtask("The task " + task.ID + " failed during its execution.")
			else:
				self.alterTaskStatus(app, task, 'failed')
				app.log.logtask("The action: '" + task.action + "' isn't recognized as a task action or isn't implemented yet.")

			# set finish date
			task.setEndTime()
			task.update(app.database)
			app.log.logtask("Executed in " + str(task.end_time - task.start_time) + " seconds.")
		
		except DatabaseError as error:
			app.log.log(error)
			sys.exit()

		finally:
			app.database.close()

	def run(self):

		pool = []

		while True:

			sync_task = False
			tasks_running = []

			# check running task
			for thread in pool:
				if not thread.is_alive():
					pool.remove(thread)
					continue
				tasks_running.append(thread.name)

			# check for pending task
			self.app.database.connect()
			task = self.checkForTasks()
			self.app.database.close()
			
			if task:
				# we check if the task isn't already running
				if not task.ID in tasks_running:
					thread = threading.Thread(target=self.execute, name=task.ID, args=(task,))
					pool.append(thread)
					thread.start()			
			else:
				time.sleep(WAIT)
