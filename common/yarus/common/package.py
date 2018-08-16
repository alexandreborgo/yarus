from yarus.common.yarusobject import YarusObject
from yarus.common.exceptions import *

class Package(YarusObject):
    
    def __init__(self):
        self.ID = ""
        self.repository = ""
        self.component = ""
        self.name = ""
        self.architecture = ""
        self.version = ""
        self.release = ""
        self.location = ""
        self.checksum_type = ""
        self.checksum = ""
        self.summary = ""
        self.type = ""
        
    def load_package(self, database, repository, comp, name, version, arch, rel):
        object_tmp = database.get_package(repository, comp, name, version, arch, rel)
        if not object_tmp:
            return None
        for key, value in vars(self).items():
            setattr(self, key, object_tmp[key])
        return self
        
    def load_package_by_info(self, database, name, arch, version, release):
        object_tmp = database.get_package_by_info(name, arch, version, release)
        if not object_tmp:
            return None
        for key, value in vars(self).items():
            setattr(self, key, object_tmp[key])
        return self
