from material.section.Fiber.Fiber import Fiber
from copy import deepcopy
import numpy as np
# 3d 是点纤维，只有y方向（竖直）和z方向（水平）的位置参数
from material.section.SectionForceDeformation import SECTION_RESPONSE_P, SECTION_RESPONSE_MZ, SECTION_RESPONSE_MY


class UniaxialFiber3d(Fiber):

    # 类共有
    ks = np.zeros((3, 3))
    fs = np.zeros(3)
    code = np.zeros(3)

    def __init__(self, tag, theMat, area, position):
        super().__init__(tag)
        self.area = area # double
        self.yz = [-position[0], position[1]]
        self.material = deepcopy(theMat) # UniaxialMaterial
        if UniaxialFiber3d.code[0] != SECTION_RESPONSE_P:
            UniaxialFiber3d.code[0] = SECTION_RESPONSE_P
            UniaxialFiber3d.code[1] = SECTION_RESPONSE_MZ
            UniaxialFiber3d.code[2] = SECTION_RESPONSE_MY

    def set_trial_fiber_strain(self, vs):
        # vs 是什么？
        strain = vs[0] + self.yz[0] * vs[1] + self.yz[1] * vs[2]
        if self.material is not None:
            return self.material.set_trial_strain(strain)
        else:
            print('UniaxialFiber3d::setTrialFiberStrain() - no material!')
            return -1

    def get_fiber_stress_resultants(self):
        df = self.material.get_stress() * self.area
        UniaxialFiber3d.fs[0] = df
        UniaxialFiber3d.fs[1] = df * self.yz[0]
        UniaxialFiber3d.fs[2] = df * self.yz[1]
        return UniaxialFiber3d.fs

    # get contribution of fiber to section tangent stiffness
    def get_fiber_tangent_stiff_contr(self):
        # ks = (as^as) * area * Et;
        value = self.material.get_tangent() * self.area
        UniaxialFiber3d.ks[0, 0] = value
        UniaxialFiber3d.ks[0, 1] = value * self.yz[0]
        UniaxialFiber3d.ks[0, 2] = value * self.yz[1]

        UniaxialFiber3d.ks[1, 0] = value * self.yz[0]
        UniaxialFiber3d.ks[1, 1] = value * self.yz[0] * self.yz[0]
        UniaxialFiber3d.ks[1, 2] = value * self.yz[0] * self.yz[1]

        UniaxialFiber3d.ks[2, 0] = value * self.yz[1]
        UniaxialFiber3d.ks[2, 1] = value * self.yz[0] * self.yz[1]
        UniaxialFiber3d.ks[2, 2] = value * self.yz[1] * self.yz[1]

    def get_order(self):
        return 3

    def get_type(self):
        return UniaxialFiber3d.code

    def commit_state(self):
        return self.material.commit_state()

    def revert_to_last_state(self):
        return self.material.revert_to_last_state()

    def revert_to_start(self):
        return self.material.revert_to_start()

    def get_fiber_location(self):
        loc = [-self.yz[0], self.yz[1]]
        return loc