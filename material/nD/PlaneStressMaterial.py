from material.nD.NDMaterial import NDMaterial
import numpy as np
from scipy.linalg import solve

class PlaneStressMaterial(NDMaterial):

    def __init__(self, tag, threed_material):
        super.__init__(tag)

        self.material = threed_material

        # out of plane strains .. trial and committed
        self.t_strain22 = 0.0
        self.t_gamma02 = 0.0
        self.t_gamma12 = 0.0
        self.c_strain22 = 0.0
        self.c_gamma02 = 0.0
        self.c_gamma12 = 0.0

        self.strain = np.zeros(3)

    def get_copy(self):
        clone = PlaneStressMaterial(self.getTag())
        clone.t_strain22 = self.t_strain22
        clone.t_gamma02 = self.t_gamma02
        clone.t_gamma12 = self.t_gamma12
        clone.c_strain22 = self.c_strain22
        clone.c_gamma02 = self.c_gamma02
        clone.c_gamma12 = self.c_gamma12

        return clone

    def set_trial_strain(self,strain_from_element):
        tolerance = 1.0e-8
        self.strain[0] = strain_from_element[0]
        self.strain[1] = strain_from_element[1]
        self.strain[2] = strain_from_element[2]

        norm = 1.0 # 随便给一个数，只要大于tolerance就行
        condensed_stress = np.zeros(3)
        strain_increment = np.zeros(3)
        threed_strain = np.zeros(6)
        dd22 = np.zeros((3,3))
        count = 0
        max_count = 20
        norm0 = 0.0

        # newton loop to solve for out-of-plane strains
        while count < max_count and norm > tolerance:

            threed_strain[0] = self.strain[0]
            threed_strain[1] = self.strain[1]
            threed_strain[2] = self.t_strain22
            threed_strain[3] = self.strain[2]
            threed_strain[4] = self.t_gamma12
            threed_strain[5] = self.t_gamma02

            # three dimensional stress
            threed_stress = self.get_stress()

            # three dimensional tangent
            threed_tangent = self.get_tangent()

            # NDmaterial strain order          = 11, 22, 33, 12, 23, 31
            # PlaneStressMaterial strain order = 11, 22, 12, 33, 23, 31
            condensed_stress[0] = threed_stress[2]
            condensed_stress[1] = threed_stress[4]
            condensed_stress[2] = threed_stress[5]

            dd22[0, 0] = threed_tangent[2, 2]
            dd22[1, 0] = threed_tangent[4, 2]
            dd22[2, 0] = threed_tangent[5, 2]

            dd22[0, 1] = threed_tangent[2, 4]
            dd22[1, 1] = threed_tangent[4, 4]
            dd22[2, 1] = threed_tangent[5, 4]

            dd22[0, 2] = threed_tangent[2, 5]
            dd22[1, 2] = threed_tangent[4, 5]
            dd22[2, 2] = threed_tangent[5, 5]

            # norm0用来记录一下第一次的norm?有什么用？
            norm = np.linalg.norm(condensed_stress)
            if count == 0:
                norm0= norm

            # condensation
            strain_increment = solve(dd22, condensed_stress)

            # update out of plane strains
            self.t_strain22 -= strain_increment[0]
            self.t_gamma12 -= strain_increment[1]
            self.t_gamma02 -= strain_increment[2]

            count += 1

    def get_stress(self):
        threed_stress = self.material.get_stress()
        stress = np.zeros(3)
        stress[0] = threed_stress[0]
        stress[1] = threed_stress[1]
        stress[2] = threed_stress[3]
        return stress

    def get_tangent(self):
        threed_tangent = self.material.get_tangent()

        dd11 = np.zeros((3,3))
        dd11[0, 0] = threed_tangent[0, 0]
        dd11[1, 0] = threed_tangent[1, 0]
        dd11[2, 0] = threed_tangent[3, 0]

        dd11[0, 1] = threed_tangent[0, 1]
        dd11[1, 1] = threed_tangent[1, 1]
        dd11[2, 1] = threed_tangent[3, 1]

        dd11[0, 2] = threed_tangent[0, 3]
        dd11[1, 2] = threed_tangent[1, 3]
        dd11[2, 2] = threed_tangent[3, 3]

        dd12 = np.zeros((3, 3))
        dd12[0, 0] = threed_tangent[0, 2]
        dd12[1, 0] = threed_tangent[1, 2]
        dd12[2, 0] = threed_tangent[3, 2]

        dd12[0, 1] = threed_tangent[0, 4]
        dd12[1, 1] = threed_tangent[1, 4]
        dd12[2, 1] = threed_tangent[3, 4]

        dd12[0, 2] = threed_tangent[0, 5]
        dd12[1, 2] = threed_tangent[1, 5]
        dd12[2, 2] = threed_tangent[3, 5]

        dd21 = np.zeros((3, 3))
        dd21[0, 0] = threed_tangent[2, 0]
        dd21[1, 0] = threed_tangent[4, 0]
        dd21[2, 0] = threed_tangent[5, 0]

        dd21[0, 1] = threed_tangent[2, 1]
        dd21[1, 1] = threed_tangent[4, 1]
        dd21[2, 1] = threed_tangent[5, 1]

        dd21[0, 2] = threed_tangent[2, 3]
        dd21[1, 2] = threed_tangent[4, 3]
        dd21[2, 2] = threed_tangent[5, 3]

        dd22 = np.zeros((3, 3))
        dd22[0, 0] = threed_tangent[2, 2]
        dd22[1, 0] = threed_tangent[4, 2]
        dd22[2, 0] = threed_tangent[5, 2]

        dd22[0, 1] = threed_tangent[2, 4]
        dd22[1, 1] = threed_tangent[4, 4]
        dd22[2, 1] = threed_tangent[5, 4]

        dd22[0, 2] = threed_tangent[2, 5]
        dd22[1, 2] = threed_tangent[4, 5]
        dd22[2, 2] = threed_tangent[5, 5]

        # condesation?
        dd22inv_dd21 = solve(dd22, dd21)

        dd11 -= dd12 * dd22inv_dd21

        return dd11

