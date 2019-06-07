from material.uniaxial.UniaxialMaterial import UniaxialMaterial

class ElasticMaterial(UniaxialMaterial):

    def __init__(self, tag, e, et = 0.0):
        super().__init__(tag)
        self.E_pos = e
        self.E_neg = e
        self.eta = et
        self.trial_strain = 0.0
        self.trial_strain_rate = 0.0
        self.committed_strain = 0.0
        self.committed_strain_rate = 0.0
    
    # def set_trial_strain(self, strain, strainRate):
    def set_trial_strain(self, strain):
        self.trial_strain = strain
        # self.trial_strain_rate = strainRate
        return 0
    
    def set_trial(self, strain, stress, tangent, strainRate=0.0):
        self.trial_strain = strain
        self.trial_strain_rate = strainRate
        if self.trial_strain >= 0.0:
            stress = self.E_pos * self.trial_strain + self.eta * self.trial_strain_rate
            tangent = self.E_pos
        else:
            stress = self.E_neg * self.trial_strain + self.eta * self.trial_strain_rate
            tangent = self.E_neg
        return 0
        
    def get_strain(self):
        return self.trial_strain

    def get_strain_rate(self):
        return self.trial_strain_rate

    def get_stress(self):
        if self.trial_strain >= 0.0:
            return self.E_pos*self.trial_strain + self.eta*self.trial_strain_rate
        else:
            return self.E_neg*self.trial_strain + self.eta*self.trial_strain_rate

    def get_tangent(self):
        if self.trial_strain > 0.0:
            return self.E_pos
        elif self.trial_strain < 0.0:
            return self.E_neg
        else:
            if self.E_pos > self.E_neg:
                return self.E_pos
            else:
                return self.E_neg

    def get_damp_tangent(self):
        return self.eta

    def get_initial_tangent(self):
        if self.E_pos > self.E_neg:
            return self.E_pos
        else:
            return self.E_neg
    
    def commit_state(self):
        self.committed_strain = self.trial_strain
        self.committed_strain_rate = self.trial_strain_rate
        return 0

    def revert_to_last_commit(self):
        self.trial_strain = self.committed_strain
        self.trial_strain_rate = self.committed_strain_rate
        return 0

    def revert_to_start(self):
        self.trial_strain = 0.0
        self.trial_strain_rate = 0.0
        return 0

    # def getCopy(self):
    #     pass
    

    