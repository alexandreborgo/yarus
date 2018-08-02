#!/home/env/bin/python

import argparse
import sys

from yarus.tasksmanager.apptasksmanager import AppTasksManager
from yarus.common.functions import *
from yarus.common.task import Task


parser = argparse.ArgumentParser()

parser.add_argument('--scheduled-task-id', action='store')

args = parser.parse_args()

if args.scheduled_task_id:
    # start the app context
    app = AppTasksManager()
    
    if not app.start():
        sys.exit(1)
        
    app.database.connect()
    
    scheduled_task = getscheduled(app, args.scheduled_task_id)
    
    if not scheduled_task:
        print("Scheduled task with ID: " + args.scheduled_task_id + " not found.")
        sys.exit(1)
    
    task = Task()
    task.setID(getnewid())
    task.setStatus('pending')
    task.setCreationDate()
    task.setAction(scheduled_task.task_action)
    task.setObjectID(scheduled_task.object_id)
    task.setManagerID(scheduled_task.manager_id)
    task.insert(app.database)

    print("Task created with ID : " + task.ID)

    app.database.close()
else:
    sys.exit(1)