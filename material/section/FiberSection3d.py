from material.section.SectionForceDeformation import SectionForceDeformation
import numpy as np
from copy import deepcopy
from material.uniaxial.ElasticMaterial import ElasticMaterial
from material.section.SectionForceDeformation import SECTION_RESPONSE_P,SECTION_RESPONSE_MY,SECTION_RESPONSE_MZ,SECTION_RESPONSE_T


class FiberSection3d(SectionForceDeformation):

    def __init__(self, tag, num, fibers, torsion=None, si=None):
        super().__init__(tag)
        self.section_integration = si # 其实和fibers不能共存？
        self.num_fibers = num
        # Q: 面积的一次矩
        self.Qzbar = 0.0
        self.Qybar = 0.0
        self.Abar = 0.0
        # data for the materials [yloc, zloc and area]
        self.mat_data = np.zeros(3*num)
        self.materials = []

        if self.num_fibers != 0:
            for i in range(0, self.num_fibers):
                fiber = fibers[i]
                loc = fiber.get_fiber_location()
                yloc = loc[0]
                zloc = loc[1]
                area = fiber.get_area()
                self.Qzbar += yloc * area
                self.Qybar += zloc * area
                self.Abar += area
                self.mat_data[i * 3] = yloc
                self.mat_data[i*3+1] = zloc
                self.mat_data[i*3+2] = area
                mat = fiber.get_material()
                self.materials.append(deepcopy((mat)))

            self.ybar = self.Qzbar / self.Abar
            self.zbar = self.Qybar / self.Abar

        if torsion is not None:
            self.torsion = deepcopy(torsion)
        else:
            self.torsion = ElasticMaterial(0, 1.0e10)

        self.s = np.zeros(4) # section resisting forces  (axial force, bending moment)
        self.ks = np.zeros((4,4)) # section stiffness
        self.e = np.zeros(4) # trial section deformations

        self.code = np.zeros(4)
        self.code[0] = SECTION_RESPONSE_P
        self.code[1] = SECTION_RESPONSE_MZ
        self.code[2] = SECTION_RESPONSE_MY
        self.code[3] = SECTION_RESPONSE_T

    def set_trial_section_deformation(self, deforms):
        res = 0
        self.e = deforms
        for i in range(0, 4):
            self.s_data[i] = 0.0
        for i in range(0, 16):
            self.k_data[i] = 0.0

        d0 = deforms[0]
        d1 = deforms[1]
        d2 = deforms[2]
        d3 = deforms[3]

        ylocs = []
        zlocs = []
        fiber_areas = []

        if self.section_integration is not None:
            pass
        else:
            for i in range(0, self.num_fibers):
                ylocs.append(self.mat_data[3*i])
                zlocs.append(self.mat_data[3*i+1])
                fiber_areas.append(self.mat_data[3*i+2])

        for i in self.num_fibers:
            mat = self.materials[i]
            y = ylocs[i] - self.ybar
            z = zlocs[i] - self.zbar
            A = fiber_areas[i]

            # determine material strain and set it
            strain = d0 - y*d1 +z*d2
            res += mat.set_trial(strain, stress, tangent)







