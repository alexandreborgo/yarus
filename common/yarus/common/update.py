from yarus.common.yarusobject import YarusObject
class Update(YarusObject):
    def __init__(self, object_id="", obj="", date=0, ID=""):
        self.object_id = object_id
        self.object_type = obj
        self.date = date
        self.ID = ID
