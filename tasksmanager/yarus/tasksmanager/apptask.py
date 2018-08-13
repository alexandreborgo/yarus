
from yarus.common.app import App
from yarus.common.config import Config
from yarus.common.log import LogSystem
from yarus.common.database import Mysql
from yarus.common.exceptions import DatabaseError

class AppTask(App):
    
    def start(self, task):
        super().start('task')
        self.log.settasklogfile(task.ID)
        try:
            self.database = Mysql(self, self.config.db_host, self.config.db_user, self.config.db_password, self.config.db_database)
            # test the connection
            self.database.connect()
            self.database.close()
            self.log.debug("Database connection OK.")
        except DatabaseError as error:
            self.log.error(str(error))
            return False
            
        return True
