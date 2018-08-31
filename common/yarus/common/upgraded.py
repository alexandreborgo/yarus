from yarus.common.yarusobject import YarusObject
class Upgraded(YarusObject):
    def __init__(self, package_id, update_id):
        self.package_id = package_id
        self.update_id = update_id
        