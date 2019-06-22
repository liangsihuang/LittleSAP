from material.nD.NDMaterial import NDMaterial
import numpy as np

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

class J2Plasticity(NDMaterial):

    def __init__(self, tag, K, G, yield0, yield_infty, d, H, viscosity=0, rho=0.0):
        super().__init__(tag)

        # material parameters
        self.bulk = K       # bulk modulus
        self.shear = G      # shear modulus
        self.sigma_0 = yield0           # initial yield stress
        self.sigma_infty = yield_infty  # final saturation yield stress
        self.delta = d          # exponential hardening parameter
        self.hard = H           # linear hardening parameter
        self.eta = viscosity    # viscosity
        self.rho = rho

        # internal variables
        self.epsilon_p_n = np.zeros((3, 3))         # plastic strain time n
        self.epsilon_p_nplus1 = np.zeros((3, 3))    # plastic strain time n+1
        self.xi_n = 0.0         # xi time n
        self.xi_nplus1 = 0.0    # xi time n+1

        # material input
        self.strain = np.zeros((3, 3))  # strain tensor
        # material response
        self.stress = np.zeros((3, 3))                  # stress tensor
        self.tangent = np.zeros((3, 3, 3, 3))           # material tangent
        self.initial_tangent = np.zeros((3, 3, 3, 3))   # material tangent
        self.IIdev = np.zeros((3, 3, 3, 3))     # rank 4 deviatoric（偏）
        self.IbunI = np.zeros((3, 3, 3, 3))     # rank 4 I bun I

        # form rank4 IbunI
        self.IbunI[0, 0, 0, 0] = 1.0
        self.IbunI[0, 0, 1, 1] = 1.0
        self.IbunI[0, 0, 2, 2] = 1.0
        self.IbunI[1, 1, 0, 0] = 1.0
        self.IbunI[1, 1, 1, 1] = 1.0
        self.IbunI[1, 1, 2, 2] = 1.0
        self.IbunI[2, 2, 0, 0] = 1.0
        self.IbunI[2, 2, 1, 1] = 1.0
        self.IbunI[2, 2, 2, 2] = 1.0

        # form rank4 IIdev
        self.IIdev[0, 0, 0, 0] = 2.0 / 3.0
        self.IIdev[0, 0, 1, 1] = -1.0 / 3.0
        self.IIdev[0, 0, 2, 2] = -1.0 / 3.0
        self.IIdev[0, 1, 0, 1] = 0.5
        self.IIdev[0, 1, 1, 0] = 0.5
        self.IIdev[0, 2, 0, 2] = 0.5
        self.IIdev[0, 2, 2, 0] = 0.5
        self.IIdev[1, 0, 0, 1] = 0.5
        self.IIdev[1, 0, 1, 0] = 0.5
        self.IIdev[1, 1, 0, 0] = -1.0 / 3.0
        self.IIdev[1, 1, 1, 1] = 2.0 / 3.0
        self.IIdev[1, 1, 2, 2] = -1.0 / 3.0
        self.IIdev[1, 2, 1, 2] = 0.5
        self.IIdev[1, 2, 2, 1] = 0.5
        self.IIdev[2, 0, 0, 2] = 0.5
        self.IIdev[2, 0, 2, 0] = 0.5
        self.IIdev[2, 1, 1, 2] = 0.5
        self.IIdev[2, 1, 2, 1] = 0.5
        self.IIdev[2, 2, 0, 0] = -1.0 / 3.0
        self.IIdev[2, 2, 1, 1] = -1.0 / 3.0
        self.IIdev[2, 2, 2, 2] = 2.0 / 3.0

        self.plastic_integrator()

    # plastic_integration routine
    def plastic_integrator(self):
        tolerance = 1.0e-8 * self.sigma_0
        dt = ops_dt



    def do_initial_tangent(self):
        pass