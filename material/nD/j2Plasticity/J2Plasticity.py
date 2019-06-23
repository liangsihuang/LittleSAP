from material.nD.NDMaterial import NDMaterial
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
        dt = OPS_Globals.ops_dt # time step
        dev_strain = np.zeros((3, 3))       # deviatoric strain
        dev_stress = np.zeros((3, 3))       # deviatoric stress
        normal = np.zeros((3, 3))           # normal to yield surface

        norm_tau = 0.0      # norm of deviatoric stress
        inv_norm_tau = 0.0
        phi = 0.0           # trial value of yield function
        trace = 0.0         # trace of strain
        gamma = 0.0         # consistency parameter

        resid = 1.0
        tang = 0.0
        theta = 0.0
        theta_inv = 0.0
        c1 = 0.0
        c2 = 0.0
        c3 = 0.0

        max_iterations = 25

        # compute the deviatoric strains
        trace = self.strain[0, 0] + self.strain[1, 1] + self.strain[2, 2]
        dev_strain = self.strain

        for i in range(0, 3):
            dev_strain[i, i] -= 1/3 * trace

        # compute the trial deviatoric stresses
        dev_stress = 2.0 * self.shear * (dev_strain - self.epsilon_p_n)

        # compute norm of deviatoric stress
        for i in range(0, 3):
            for j in range(0, 3):
                norm_tau += dev_stress[i, j] * dev_stress[i, j]
        norm_tau = sqrt(norm_tau)

        if norm_tau > tolerance:
            inv_norm_tau = 1.0 / norm_tau
            normal = inv_norm_tau * dev_stress
        else:
            normal[:, :] = 0.0
            inv_norm_tau = 0.0

        # compute trial value of yield function
        phi = norm_tau - sqrt(2.0/3.0) * self.q(self.xi_n)
        # check if phi > 0
        if phi > 0:
            # plastic
            # solve for gamma
            gamma = 0.0
            resid = 1.0
            iteration_counter = 0
            while fabs(resid) > tolerance:
                r = sqrt(2.0/3.0)
                resid = norm_tau - (2.0*self.shear) * gamma - \
                        r * self.q(self.xi_n + r*gamma) - self.eta / dt * gamma
                tang = -(2.0*self.shear) - 2.0/3.0 * self.qprime(self.xi_n + r * gamma) - self.eta / dt
                gamma -= resid / tang
                iteration_counter += 1
                if iteration_counter > max_iterations:
                    print('More than ' + str(max_iterations) + ' iterations in constituive subroutine J2-plasticity \n')
                    break
            gamma *= 1.0 * 1e-8

            # update plastic internal variables
            self.epsilon_p_nplus1 = self.epsilon_p_n + gamma * normal
            self.xi_nplus1 = self.xi_n + sqrt(2.0/3.0) * gamma

            # recompute deviatoric stresses
            dev_stress = 2.0 * self.shear * (dev_strain - self.epsilon_p_nplus1)

            # compute the terms for plastic part of tangent
            theta = 2.0 * self.shear + 2.0/3.0 * self.qprime(self.xi_nplus1) + self.eta / dt
            theta_inv = 1.0 / theta
        else:
            # elastic
            # update history variables -- they remain unchanged
            self.epsilon_p_nplus1 = self.epsilon_p_n
            self.xi_nplus1 = self.xi_n
            # no extra tangent terms to compute
            gamma = 0.0
            theta = 0.0
            theta_inv = 0.0

        # add on bulk part of stress
        self.stress = dev_stress
        for i in range(0, 3):
            self.stress[i, i] += self.bulk * trace

        # compute the tangent
        c1 = -4.0 * shear * shear
        c2 = c1 * theta_inv
        c3 = c1 * gamma * inv_norm_tau

        for




    def do_initial_tangent(self):
        pass

    # hardening function
    def q(self, xi):
        temp = self.sigma_infty + \
               (self.sigma_0 - self.sigma_infty) * exp(-self.delta * xi) + self.hard * xi
        return temp

    # hardening function derivative
    def qprime(self, xi):
        temp = (self.sigma_0 - self.sigma_infty) * (-self.delta) * exp(-self.delta * xi) + self.hard
        return temp

