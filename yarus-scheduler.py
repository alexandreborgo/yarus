#!/opt/yarus/env/bin/python

import argparse
import sys

from yarus.common.app import App
from yarus.common.functions import *
from yarus.common.task import Task


parser = argparse.ArgumentParser()

parser.add_argument('--scheduled-task-id', action='store')

args = parser.parse_args()

 # start the app context
app = App()

if not app.start():
    app.log.error("Can't start AppTaskManager.")
    sys.exit(0)

if args.scheduled_task_id:
           
    app.database.connect()

    # check if the object exists
    scheduled_task = getobject(app, 'scheduled', args.scheduled_task_id)
    if not scheduled_task:
        app.log.error("Scheduled task with ID: " + args.scheduled_task_id + " not found.")
        sys.exit(0)
    
    # generate task object
    task = Task()
    task.setID(getnewid())
    task.setStatus('pending')
    task.setCreationDate()
    task.setAction(scheduled_task.action)
    task.setObjectID(scheduled_task.object_id)
    task.setManagerID(scheduled_task.manager_id)

    # push into the database
    task.insert(app.database)

    app.log.log("Task created with ID : " + task.ID)

    app.database.close()
else:
    app.log.error("No scheduled task ID given.")
    sys.exit(0)