from yarus.common.yarusobject import YarusObject
from yarus.common.exceptions import *

class Daterepository(YarusObject):
    
    def __init__(self):
        self.ID = ""
        self.repository = ""
        self.date = ""
        
    def load_daterepository(self, database, repository, date):
        object_tmp = database.get_daterepository("yarus_daterepository", repository, date)
        if not object_tmp:
            return None
        for key, value in vars(self).items():
            setattr(self, key, object_tmp[key])
        return self