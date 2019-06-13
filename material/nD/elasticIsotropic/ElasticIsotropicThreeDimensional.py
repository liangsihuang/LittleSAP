from material.nD.elasticIsotropic.ElasticIsotropicMaterial import ElasticIsotropicMaterial
import numpy as np

class ElasticIsotropicThreeDimensional(ElasticIsotropicMaterial):
    
    def __init__(self, tag, e, nu, r=0.0):

        super().__init__(tag, e, nu, r)
        self.sigma = np.zeros(6)
        self.D = np.zeros((6, 6))
        # trial and committed strain vector
        self.epsilon = np.zeros(6)
        self.c_epsilon = np.zeros(6)

    def get_tangent(self):
        # 3维弹性矩阵采用拉梅常数表示
        G2 = self.E/(1.0+self.v)    # 拉梅常数 2G
        lam = self.v/(1.0-2*self.v)*G2 # 拉梅常数 lambda
        G = G2/2 # 拉梅常数 G

        self.D[0, 0] = G2 + lam
        self.D[1, 1] = G2 + lam
        self.D[2, 2] = G2 + lam

        self.D[0, 1] = lam
        self.D[1, 0] = lam
        self.D[0, 2] = lam
        self.D[2, 0] = lam
        self.D[1, 2] = lam
        self.D[2, 1] = lam

        self.D[3, 3] = G
        self.D[4, 4] = G
        self.D[5, 5] = G

        return self.D

    def get_stress(self):
        self.sigma = np.dot(self.D, self.epsilon)
        return self.sigma

    def commit_state(self):
        self.c_epsilon = self.epsilon
        return 0

    def set_trial_strain(self, strain):
        self.epsilon = strain
    
    