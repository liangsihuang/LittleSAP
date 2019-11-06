
from TaggedObject import TaggedObject

# 单条纤维

class Fiber(TaggedObject):

    def __init__(self, tag):
        super().__init__(tag)
        self.sDefault = None # Vector  干嘛的？
        self.fDefault = None # Matrix  干什么？

    def getMaterial(self):
        return 0

    def getNDMaterial(self):
        return 0

