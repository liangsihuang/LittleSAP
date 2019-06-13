from material.nD.NDMaterial import NDMaterial
import numpy as np

class J2Plasticity(NDMaterial):

    def __init__(self, tag, K, G, yield0, yield_infty, d, H, viscosity=0, rho=0.0):
        super().__init__(tag)

        # material parameters
        self.bulk = K
        self.shear = G
        self.sigma_0 = yield0
        self.sigma_infty = yield_infty
        self.delta = d
        self.hard = H
        self.eta = viscosity
        self.rho = rho

        # internal variables
        self.epsilon_p_n = np.zeros((3, 3))  # plastic strain time n
        self.epsilon_p_nplus1 = np.zeros((3, 3))  # plastic strain time n+1
        self.xi_n = 0.0         # xi time n
        self.xi_nplus1 = 0.0    # xi time n+1

        # material input
        self.strain = np.zeros((3, 3))  # strain tensor
        # material response
        self.stress = np.zeros((3, 3))          # stress tensor
        self.tangent = np.zeros((3, 3, 3, 3))
        self.initial_tangent = np.zeros((3, 3, 3, 3))
        self.IIdev = np.zeros((3, 3, 3, 3))     # rank 4 deviatoric（偏）
        self.IbunI = np.zeros((3, 3, 3, 3))     # rank 4 I bun I

