from material.section.Fiber.Fiber import Fiber
from copy import deepcopy

# 2d 是层纤维，只有一个y方向的位置参数

class UniaxialFiber2d(Fiber):

    def __init__(self, tag, theMat, area, position):
        super().__init__(tag)
        self.area = area # double
        self.y = -position # double
        self.theMaterial = deepcopy(theMat) # UniaxialMaterial


    def getMaterial(self):
        return 0

    def getNDMaterial(self):
        return 0

    