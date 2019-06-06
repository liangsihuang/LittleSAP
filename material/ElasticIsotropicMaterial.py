from material.nD.NDMaterial import NDMaterial

class ElasticIsotropicMaterial(NDMaterial):
    
    def __init__(self, tag, e, nu, r):
        super().__init__(tag)
        self.E = e
        self.v = nu
        self.rho = r



    
    