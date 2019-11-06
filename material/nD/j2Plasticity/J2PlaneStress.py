from material.nD.j2Plasticity.J2Plasticity import J2Plasticity
from math import fabs
import numpy as np

class J2PlaneStress(J2Plasticity):

    def __init__(self, tag, K, G, yield0, yield_infty, d, H, viscosity=0.0, rho=0.0):
        super().__init__(tag, K, G, yield0, yield_infty, d, H, viscosity, rho)
        self.commit_eps22 = 0.0

    # get the strain and integrate plasticity equations
    def set_trial_strain(self, strain_from_element):
        tolerance = 1e-12
        max_iterations = 25
        iteration_counter = 0
        eps22 = self.strain[2, 2]
        self.strain[:, :] = 0.0

        self.strain[0, 0] = strain_from_element[0]
        self.strain[1, 1] = strain_from_element[1]
        self.strain[0, 1] = 0.5 * strain_from_element[2]
        self.strain[1, 0] = self.strain[0, 1]

        self.strain[2, 2] = eps22

        # enforce the plane stress condition sigma_22 = 0
        # solve for epsilon_22
        # 因为 python 没有do while 循环，只能手动先 do 一次
        self.plastic_integrator()
        self.strain[2, 2] -= self.stress[2, 2] / self.tangent[2, 2, 2, 2]
        iteration_counter += 1

        while fabs(self.stress[2, 2]) > tolerance:
            self.plastic_integrator()
            self.strain[2, 2] -= self.stress[2, 2] / self.tangent[2, 2, 2, 2]
            iteration_counter += 1
            if iteration_counter > max_iterations:
                print('More than '+str(max_iterations)+' iterations in set_trial_strain of J2PlaneStress \n')
                break

        # modify tangent for plane stress
        for ii in range(0, 3):
            for jj in range(0, 3):
                tuple = self.index_map(ii)
                i = tuple[0]
                j = tuple[1]
                tuple = self.index_map(jj)
                k = tuple[0]
                l = tuple[1]
                self.tangent[i, j, k, l] -= self.tangent[i, j, 2, 2] * \
                                            self.tangent[2, 2, k, l] / self.tangent[2, 2, 2, 2]
                # minor symmetries
                self.tangent[j, i, k, l] = self.tangent[i, j, k, l]
                self.tangent[i, j, l, k] = self.tangent[i, j, k, l]
                self.tangent[j, i, l, k] = self.tangent[i, j, k, l]
        return 0

    def get_stress(self):
        stress_vec = np.zeros(3)
        stress_vec[0] = self.stress[0, 0]
        stress_vec[1] = self.stress[1, 1]
        stress_vec[2] = self.stress[0, 1]
        return stress_vec

    def get_tangent(self):
        #     matrix to tensor mapping
        # 	  Matrix      Tensor
        # 	 -------     -------
        # 	   0           0 0
        # 	   1           1 1
        # 	   2           0 1  ( or 1 0 )
        tangent_matrix = np.zeros((3, 3))
        tangent_matrix[0, 0] = self.tangent[0, 0, 0, 0]
        tangent_matrix[1, 1] = self.tangent[1, 1, 1, 1]
        tangent_matrix[2, 2] = self.tangent[0, 1, 0, 1]

        tangent_matrix[0, 1] = self.tangent[0, 0, 1, 1]
        tangent_matrix[1, 0] = self.tangent[1, 1, 0, 0]

        tangent_matrix[0, 2] = self.tangent[0, 0, 0, 1]
        tangent_matrix[2, 0] = self.tangent[0, 1, 0, 0]

        tangent_matrix[1, 2] = self.tangent[1, 1, 0, 1]
        tangent_matrix[2, 1] = self.tangent[0, 1, 1, 1]
        return tangent_matrix

    # 因为多了commit_eps22，所以重写
    def commit_state(self):
        self.epsilon_p_n = self.epsilon_p_nplus1
        self.xi_n = self.xi_nplus1
        self.commit_eps22 = self.strain[2, 2]
        return 0

    # 和三维的不一样哦！
    def index_map(self, matrix_index):
        temp = matrix_index + 1 # add 1 for standard tensor indices
        i = 1
        j = 1
        if temp == 1:
            i = 1
            j = 1
        elif temp == 2:
            i = 2
            j = 2
        elif temp == 3:
            i = 1
            j = 2
        elif temp == 4:
            i = 3
            j = 3
        elif temp == 5:
            i = 2
            j = 3
        elif temp == 6:
            i = 3
            j = 1
        # subtract 1 for C-indexing， 即从0开始
        i -= 1
        j -= 1
        return i, j
