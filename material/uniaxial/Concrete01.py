from material.uniaxial.UniaxialMaterial import UniaxialMaterial
from math import fabs
# Description: This file contains the class definition for
# Concrete01
#    - Modified Kent-Park envelope
#    - No tension
#    - Linear unloading/reloading

class Concrete01(UniaxialMaterial):

    def __init__(self, tag, fpc, ec0, fpcu, ecu):
        super().__init__(tag)
        self.fpc = fpc      # Compressive strength
        self.epsc0 = ec0    # Strain at compressive strength
        self.fpcu = fpcu    # Crushing strength
        self.epscu = ecu    # Strain at crushing strength

        # CONVERGED History Variables / C:commmited
        self.c_min_strain = 0.0   # Smallest previous concrete strain (compression)
        self.c_end_strain = 0.0   # Strain at the end of unloading from CminStrain
        # CONVERGED State Variables / C:commmited
        self.c_strain = 0.0
        self.c_stress = 0.0

        # Make all concrete parameters negative
        if self.fpc > 0.0:
            self.fpc = -self.fpc
        if self.epsc0 > 0.0:
            self.epsc0 = -self.epsc0
        if self.fpcu > 0.0:
            self.fpcu = -self.fpcu
        if self.epscu > 0.0:
            self.epscu = -self.epscu

        # Initial tangent
        Ec0 = 2 * self.fpc / self.epsc0
        self.c_tangent = Ec0
        self.c_unload_slope = Ec0
        self.t_tangent = Ec0 # T:trial

        # set trial values
        self.revert_to_last_commit()

    def revert_to_last_commit(self):
        # Reset trial history variables to last committed state
        self.t_min_strain = self.c_min_strain
        self.t_end_strain = self.c_end_strain
        self.t_unload_slope = self.c_unload_slope
        # Recompute trial stress and tangent
        self.t_strain = self.c_strain
        self.t_stress = self.c_stress
        self.t_tangent = self.c_tangent

    # def getCopy(self):
    #     theCopy = Concrete01(self.getTag(), self.fpc, self.epsc0, self.fpcu, self.epscu)
    #     theCopy.CminStrain = self.CminStrain
    #     theCopy.CunloadSlope = self.CunloadSlope
    #     theCopy.CendStrain = self.CendStrain
    #     theCopy.Cstrain = self.Cstrain
    #     theCopy.Cstress = self.Cstress
    #     theCopy.Ctangent = self.Ctangent
    #     return theCopy

    def set_trial(self, strain, strain_rate=0.0):
        # Reset trial history variables to last committed state
        self.t_min_strain = self.c_min_strain
        self.t_end_strain = self.c_end_strain
        self.t_unload_slope = self.c_unload_slope

        self.t_strain = self.c_strain
        self.t_stress = self.c_stress
        self.t_tangent = self.c_tangent
        # Determine change in strain from last converged state
        dstrain = strain - self.c_strain
        if fabs(dstrain) < 1e-16:
            stress = self.t_stress
            tangent = self.t_tangent
            return stress, tangent
        self.t_strain = strain
        # check for a quick return
        if self.t_strain > 0.0:
            self.t_stress = 0
            self.t_tangent = 0
            stress = 0
            tangent = 0
            return stress, tangent
        # Calculate the trial state given the change in strain
        self.t_unload_slope = self.c_unload_slope
        tempstress = self.c_stress + self.t_unload_slope*(self.t_strain-self.c_strain)
        # Material goes further into compression
        if strain <= self.c_strain:
            self.t_min_strain = self.c_min_strain
            self.t_end_strain = self.c_end_strain
            self.reload()
            if tempstress > self.t_stress:
                self.t_stress = tempstress
                self.t_tangent = self.t_unload_slope
        # Material goes TOWARD tension
        elif tempstress <= 0.0:
            self.t_stress = tempstress
            self.t_tangent = self.t_unload_slope
        # Made it into tension
        else:
            self.t_stress = 0.0
            self.t_tangent = 0.0

        stress = self.t_stress
        tangent = self.t_tangent

        return stress, tangent

    def reload(self):
        if self.t_strain <= self.t_min_strain:
            self.t_min_strain = self.t_strain
            # Determine point on envelope
            self.envelope()
            self.unload()
        elif self.t_strain <= self.t_end_strain:
            self.t_tangent = self.t_unload_slope
            self.t_stress = self.t_tangent * (self.t_strain-self.t_end_strain)
        else:
            self.t_stress = 0.0
            self.t_tangent = 0.0

    def envelope(self):
        if self.t_strain > self.epsc0:
            eta = self.t_strain / self.epsc0
            self.t_stress = self.fpc * (2*eta-eta*eta)
            Ec0 = 2.0 * self.fpc / self.epsc0
            self.t_tangent = Ec0 * (1-eta)
        elif self.t_strain > self.epscu:
            self.t_tangent = (self.fpc-self.fpcu) / (self.epsc0-self.epscu)
            self.t_stress = self.fpc + self.t_tangent * (self.t_strain-self.epsc0)
        else:
            self.t_stress = self.fpcu
            self.t_tangent = 0.0

    def unload(self):
        tempstrain = self.t_min_strain
        if tempstrain < self.epscu:
            tempstrain = self.epscu
        eta = tempstrain / self.epsc0
        ratio = 0.707*(eta-2.0) + 0.834
        if eta < 2.0:
            ratio = 0.145*eta*eta + 0.13*eta
        self.t_end_strain = ratio * self.epsc0
        temp1 = self.t_min_strain - self.t_end_strain
        Ec0 = 2.0 * self.fpc / self.epsc0
        temp2 = self.t_stress / Ec0
        if temp1 > 0.0: # temp1 should always be negative
            self.t_unload_slope = Ec0
        elif temp1 < temp2:
            self.t_end_strain = self.t_min_strain - temp1
            self.t_unload_slope = self.t_stress / temp1
        else:
            self.t_end_strain = self.t_min_strain - temp2
            self.t_unload_slope = Ec0



