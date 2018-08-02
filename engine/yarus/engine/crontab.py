

import os
import subprocess

class Crontab():

    crontab_dir = "/var/spool/cron/crontabs/"
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
            cronline += cron['minute'] + " "
            cronline += cron['hour'] + " "
            cronline += cron['day_of_month'] + " "
            cronline += cron['month'] + " "
            cronline += cron['day_of_week'] + " "
            # deal with day_place
            cronline += self.scheduler_script + " --scheduled-task-id " + cron['ID'] + " >> /var/log/yarus/scheduler.log"
            cronfile.write("# Scheduled task " + cron['name'] + ", " + cron['description'] + "\n")
            cronfile.write(cronline + "\n")
            print(cronline)
        cronfile.close()
        return True
        
    def set_cron_file(self):
        cron_cmd = "crontab " + self.tmp_cron_file
        result = subprocess.call(cron_cmd, shell=True)
        
        if result != 0:
            return False
        else:
            return True
