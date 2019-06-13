from material.nD.elasticIsotropic.ElasticIsotropicMaterial import ElasticIsotropicMaterial
import numpy as np


class ElasticIsotropicPlaneStress2D(ElasticIsotropicMaterial):
    
    def __init__(self, tag, e, nu, r=0.0):

        super().__init__(tag, e, nu, r)
        self.sigma = np.zeros(3)
        self.D = np.zeros((3, 3))
        # trial and committed strain vector
        self.epsilon = np.zeros(3)
        self.c_epsilon = np.zeros(3)

    def get_tangent(self):
        a = self.E/(1.0-self.v*self.v)
        self.D[0, 0] = 1 * a
        self.D[1, 1] = 1 * a
        self.D[0, 1] = self.v * a
        self.D[1, 0] = self.v * a
        self.D[2, 2] = (1 - self.v)/2 * a
        return self.D

    def get_stress(self):
        self.sigma = np.dot(self.D, self.epsilon)
        return self.sigma

    def commit_state(self):
        self.c_epsilon = self.epsilon
        return 0

    def set_trial_strain(self, strain):
        self.epsilon = strain
    
    