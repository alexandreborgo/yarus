
import sys
import time
import threading

from yarus.common.app import App
from yarus.tasksmanager import actions
from yarus.common.task import Task
from yarus.common.exceptions import *
from yarus.common.const import TASK_ACTIONS

WAIT = 10

class YarusTasksManager():

	def __init__(self):

		# start the app context
		self.app = App(debug=True)

		if not self.app.start():
			sys.exit(1)

	def checkForTasks(self):
		try:
			tasks = self.app.database.get_pending_task()
			pending_tasks = []
			if tasks:
				for task_id in tasks:
					try:
						pending_tasks.append(Task().load(self.app.database, task_id["ID"]))
					except Exception as error:
						print("Can't find task ID : " + task_id["ID"])
						print(str(error))
						continue
			return pending_tasks
		except Exception:
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
			print("Erro while init App context.")
			return False
		
		try:
			app.database.connect()

			# set the status of the task to running 
			self.alterTaskStatus(app, task, 'running')

			print("Starting task " + task.ID + " (" + task.action + ") on object " + task.object_id + " in the thread " + str(threading.current_thread()))

			app.log.settasklogfile(task.ID)

			# set the start date
			task.setStartTime()
			task.update(app.database)

			if task.action in TASK_ACTIONS:

				# get the function of the action and execute it
				try:
					action = getattr(actions, task.action)
					result = action(app, task, task.object_id)
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
		
		print("Leaving task " + task.ID + " (" + task.action + ") on thread " + str(threading.current_thread()))

	def run(self):

		pool = []

		while True:

			sync_task = False
			tasks_running = []
			object_running = []

			# check running task
			for item in pool:
				if not item[0].is_alive():
					pool.remove(item)
					continue
				tasks_running.append(item[1].ID)
				object_running.append(item[1].object_id)

			# check for pending task
			self.app.database.connect()
			pending_tasks = self.checkForTasks()			
			self.app.database.close()
			
			if pending_tasks:
				for task in pending_tasks:
					# we check if the task isn't already running
					if not task.ID in tasks_running:
						# and if an other task isn't already running on the object
						if not task.object_id in object_running:
							thread = threading.Thread(target=self.execute, name=task.ID, args=(task,))	
							pool.append([thread, task])
							tasks_running.append(task.ID)
							object_running.append(task.object_id)
							thread.start()
			else:				
				if tasks_running:
					print("Task running: ", end='')
					for task in tasks_running:
						print(task + ", ", end='')
					print("")
				time.sleep(WAIT)
