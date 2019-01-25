from material.UniaxialMaterial import UniaxialMaterial

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
        self.CminStrain = 0.0   # Smallest previous concrete strain (compression)
        self.CendStrain = 0.0   # Strain at the end of unloading from CminStrain
        # CONVERGED State Variables / C:commmited
        self.Cstrain = 0.0
        self.Cstress = 0.0

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
        self.Ctangent = Ec0
        self.CunloadSlope = Ec0
        self.Ttangent = Ec0 # T:trial

        # set trial values
        self.revertToLastCommit()

    def revertToLastCommit(self):
        # Reset trial history variables to last committed state
        self.TminStrain = self.CminStrain
        self.TendStrain = self.CendStrain
        self.TunloadSlope = self.CunloadSlope
        # Recompute trial stress and tangent
        self.Tstrain = self.Cstrain
        self.Tstress = self.Cstress
        self.Ttangent = self.Ctangent
