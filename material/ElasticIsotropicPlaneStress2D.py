from material.ElasticIsotropicMaterial import ElasticIsotropicMaterial
import numpy as np

class ElasticIsotropicPlaneStress2D(ElasticIsotropicMaterial):
    
    def __init__(self, tag, e, nu, r):

        super().__init__(tag, e, nu, r)
        self.sigma = np.zeros(3)
        self.D = np.zeros((3, 3))
        # trial and commited strain vector
        self.epsilon = np.zeros(3)
        self.c_epsilon = np.zeros(3)






    
    