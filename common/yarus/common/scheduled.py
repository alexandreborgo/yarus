
import re

from yarus.common.yarusobject import YarusObject
from yarus.common.exceptions import *

class Scheduled(YarusObject):
    
    def __init__(self):
        self.ID = ""
        self.name = ""
        self.description = ""
        self.manager_id = 0
        self.last_date = 0
        self.creation_date = 0
        self.action = ""
        self.minute = ""
        self.hour = ""
        self.day_of_month = ""
        self.month = ""
        self.day_of_week = ""
        self.day_place = ""
        self.object_id = ""
        self.object_type = ""
        self.object_name = ""
        
    def setHour(self, info):
        if info:
            if re.match("^([0-9]*)|([*])$", info):
                self.hour = info
                return True
            else:
                raise(InvalidValueException("The given hour (" + info + ") is invalid."))
        else:
            raise(InvalidValueException("The hour is missing."))
            
    def setMinute(self, info):
        if info:
            if re.match("^([0-9]*)|([*])$", info):
                self.minute = info
                return True
            else:
                raise(InvalidValueException("The given minute (" + info + ") is invalid."))
        else:
            raise(InvalidValueException("The minute is missing."))
            
    def setDayofmonth(self, info):
        if info:
            if re.match("^([0-9]*)|([*])$", info):
                self.day_of_month = info
                return True
            else:
                raise(InvalidValueException("The given day of month (" + info + ") is invalid."))
        else:
            raise(InvalidValueException("The day of month is missing."))
            
    def setMonth(self, info):
        if info:
            if re.match("^([0-9]*)|([*])$", info):
                self.month = info
                return True
            else:
                raise(InvalidValueException("The given month (" + info + ") is invalid."))
        else:
            raise(InvalidValueException("The month is missing."))

    def setDayofweek(self, info):
        if info:
            if re.match("^([0-9]*)|([*])$", info):
                self.day_of_week = info
                return True
            else:
                raise(InvalidValueException("The given day of week (" + info + ") is invalid."))
        else:
            raise(InvalidValueException("The day of week is missing."))
            
    def setDayofplace(self, info):
        if info:
            if re.match("^([0-9]*)|([*])$", info):
                self.day_place = info
                return True
            else:
                raise(InvalidValueException("The given day of week in month (" + info + ") is invalid."))
        else:
            raise(InvalidValueException("The day of week in month is missing."))

