from material.nD.j2Plasticity.J2Plasticity import J2Plasticity
import numpy as np
from opensees import OPS_Globals
from math import sqrt, exp, fabs
# J2 isotropic hardening material class

# Elastic Model
# sigma = K*trace(epsilion_elastic) + (2*G)*dev(epsilon_elastic)

# Yield Function
# phi(sigma,q) = || dev(sigma) ||  - sqrt(2/3)*q(xi)

# Saturation Isotropic Hardening with linear term
# q(xi) = simga_0 + (sigma_infty - sigma_0)*exp(-delta*xi) + H*xi

# Flow Rules
# \dot{epsilon_p} =  gamma * d_phi/d_sigma
# \dot{xi}        = -gamma * d_phi/d_q

# Linear Viscosity
# gamma = phi / eta  ( if phi > 0 )

# Backward Euler Integration Routine
# Yield condition enforced at time n+1

# set eta := 0 for rate independent case

# Send strains in following format :
#
#    strain_vec = {   eps_00
#                     eps_11
#                     eps_22
#                   2 eps_01
#                   2 eps_12
#                   2 eps_20    }   <--- note the 2
#


class J2ThreeDimensional(J2Plasticity):

    def __init__(self, tag, K, G, yield0, yield_infty, d, H, viscosity=0, rho=0.0):
        super().__init__(tag, K, G, yield0, yield_infty, d, H, viscosity, rho)




    def set_trial_strain(self, strain_from_element):
        self.strain[:, :] = 0.0
        self.strain[0, 0] = strain_from_element[0]
        self.strain[1, 1] = strain_from_element[1]
        self.strain[2, 2] = strain_from_element[2]

        self.strain[0, 1] = 0.5 * strain_from_element[3]
        self.strain[1, 0] = self.strain[0, 1]

        self.strain[1, 2] = 0.5 * strain_from_element[4]
        self.strain[2, 1] = self.strain[1, 2]

        self.strain[2, 0] = 0.5 * strain_from_element[5]
        self.strain[0, 2] = self.strain[2, 0]

        self.plastic_integrator()
        return 0

    def getStress(self):
        stress_vec = np.zeros(6)
        stress_vec[0] = self.stress[0, 0]
        stress_vec[1] = self.stress[1, 1]
        stress_vec[2] = self.stress[2, 2]
        stress_vec[3] = self.stress[0, 1]
        stress_vec[4] = self.stress[1, 2]
        stress_vec[5] = self.stress[0, 2]
        return stress_vec

    def get_tangent(self):
#       matrix to tensor mapping
#       Matrix      Tensor
#      -------     -------
#        0           0 0
#        1           1 1
#        2           2 2
#        3           0 1  ( or 1 0 )
#        4           1 2  ( or 2 1 )
#        5           2 0  ( or 0 2 )
        tangent_matrix = np.zeros((6, 6))
        for ii in range(0, 6):
            for jj in range(0, 6):
                tuple = self.index_map(ii)
                i = tuple[0]
                j = tuple[1]
                tuple = self.index_map(jj)
                k = tuple[0]
                l = tuple[1]
                tangent_matrix[ii, jj] = self.tangent[i, j, k, l]
        return tangent_matrix