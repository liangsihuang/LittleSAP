
from material.section.Fiber import Fiber

class UniaxialFiber2d(Fiber):

    def __init__(self, tag, theMat, area, position):
        super().__init__(tag)
        self.area = area # double
        self.y = -position # double
        self.theMaterial = theMat.getCopy() # UniaxialMaterial


    def getMaterial(self):
        return 0

    def getNDMaterial(self):
        return 0

    