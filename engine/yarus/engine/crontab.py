

import os
import subprocess

class Crontab():

    tmp_cron_file = "/tmp/crontab"
    scheduler_script = "/var/lib/yarus/yarus-scheduler.py"

    def __init__(self):
        if os.path.isfile(self.tmp_cron_file):
            os.remove(self.tmp_cron_file)
        open(self.tmp_cron_file, 'w').close()

    def generate_cron_file(self, database):
        cronfile = open(self.tmp_cron_file, 'w')
        crons = database.get_scheduled_tasks()
            
        for cron in crons:
            cronline = ""
            
            # time related information
            cronline += cron['minute'] + " "
            cronline += cron['hour'] + " "
            cronline += cron['day_of_month'] + " "
            cronline += cron['month'] + " "
            cronline += cron['day_of_week'] + " "

            # deal with day_place
            if cron['day_place'] == 'first':
                cronline += "[ `date +\%d` -le 7 ] && "
            elif cron['day_place'] == 'second':
                cronline += "[ `date +\%d` -gt 7 ] && [ `date +\%d` -le 14 ] && "
            elif cron['day_place'] == 'third':
                cronline += "[ `date +\%d` -gt 15 ] && [ `date +\%d` -le 21 ] && "
            elif cron['day_place'] == 'fourth':
                cronline += "[ `date +\%d` -gt 22 ] && [ `date +\%d` -le 28 ] && "
            elif cron['day_place'] == 'fifth':
                cronline += "[ `date +\%d` -gt 29 ] && "

            # command
            cronline += self.scheduler_script + " --scheduled-task-id " + cron['ID'] + " >> /var/log/yarus/scheduler.log"
            
            # comment on the task
            cronfile.write("# Scheduled task " + cron['name'] + ", " + cron['description'] + "\n")
            
            # the task
            cronfile.write(cronline + "\n")

        cronfile.close()
        return True
        
    def set_cron_file(self):
        # change the crontab file with the new one
        cron_cmd = "crontab " + self.tmp_cron_file
        result = subprocess.call(cron_cmd, shell=True)
        
        if result != 0:
            return False
        else:
            return True
