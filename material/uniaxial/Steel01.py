from material.uniaxial.UniaxialMaterial import UniaxialMaterial
from math import fabs, pow

STEEL_01_DEFAULT_A1 = 0.0
STEEL_01_DEFAULT_A2 = 55.0
STEEL_01_DEFAULT_A3 = 0.0
STEEL_01_DEFAULT_A4 = 55.0

class Steel01(UniaxialMaterial):

    def __init__(self, tag, fy, E0, b,
                 a1=STEEL_01_DEFAULT_A1, a2=STEEL_01_DEFAULT_A2,
                 a3=STEEL_01_DEFAULT_A3, a4=STEEL_01_DEFAULT_A4):
        super().__init__(tag)
        self.fy = fy
        self.E0 = E0
        self.b  = b
        self.a1 =a1
        self.a2 = a2
        self.a3 = a3
        self.a4 = a4
        # Sets all history and state variables to initial values
        # History variables
        self.c_min_strain = 0.0
        self.c_max_strain = 0.0
        self.c_shift_P = 1.0
        self.c_shift_N = 1.0
        self.c_loading = 0

        self.t_min_strain = 0.0
        self.t_max_strain = 0.0
        self.t_shift_P = 1.0
        self.t_shift_N = 1.0
        self.t_loading = 0

        # State variables
        self.c_strain = 0.0
        self.c_stress = 0.0
        self.c_tangent = E0

        self.t_strain = 0.0
        self.t_stress = 0.0
        self.t_tangent = E0

    # def getCopy(self):
    #     theCopy = Steel01(self.getTag(), self.fy, self.E0, self.b, self.a1, self.a2, self.a3, self.a4)
    #     theCopy.CminStrain = self.CminStrain
    #     theCopy.CmaxStrain = self.CmaxStrain
    #     theCopy.CshiftP = self.CshiftP
    #     theCopy.CshiftN = self.CshiftN
    #     theCopy.Cloading = self.Cloading
    #
    #     theCopy.TminStrain = self.TminStrain
    #     theCopy.TmaxStrain = self.TmaxStrain
    #     theCopy.TshiftP = self.TshiftP
    #     theCopy.TshiftN = self.TshiftN
    #     theCopy.Tloading =self.Tloading
    #
    #     theCopy.Cstrain = self.Cstrain
    #     theCopy.Cstress = self.Cstress
    #     theCopy.Ctangent = self.Ctangent
    #
    #     theCopy.Tstrain = self.Tstrain
    #     theCopy.Tstress = self.Tstress
    #     theCopy.Ttangent = self.Ttangent
    #
    #     return theCopy

    def set_trial(self, strain, strain_rate=0.0):
        # Reset history variables to last converged state
        self.t_min_strain = self.c_min_strain
        self.t_max_strain = self.c_max_strain
        self.t_shift_P = self.c_shift_P
        self.t_shift_N = self.c_shift_N
        self.t_loading = self.c_loading
        self.t_strain = self.c_strain
        self.t_stress = self.c_stress
        self.t_tangent = self.c_tangent
        # Determine change in strain from last converged state
        dstrain = strain - self.c_strain
        if fabs(dstrain) > 1e-16:
            # Set trial strain
            self.t_strain = strain
            # Calculate the trial state given the trial strain
            self.determine_trial_state(dstrain)
        stress = self.t_stress
        tangent = self.t_tangent
        return stress, tangent


    def determine_trial_state(self, dstrain):
        fyoneminusb = self.fy * (1.0-self.b)
        Esh = self.b * self.E0
        epsy = self.fy / self.E0
        c1 = Esh * self.t_strain
        c2 = self.t_shift_N * fyoneminusb
        c3 = self.t_shift_P * fyoneminusb
        c = self.c_stress + self.E0 * dstrain

        c1c3 = c1 + c3
        if c1c3<c:
            self.t_stress = c1c3
        else:
            self.t_stress = c
        c1c2 = c1 - c2
        if c1c2 > self.t_stress:
            self.t_stress = c1c2

        if fabs(self.t_stress-c) < 1e-16:
            self.t_tangent = self.E0
        else:
            self.t_tangent = Esh

        # Determine if a load reversal has occurred due to the trial strain
        # Determine initial loading condition
        if self.t_loading == 0 and dstrain != 0.0:
            if dstrain > 0.0:
                self.t_loading = 1
            else:
                self.t_loading = -1

        # Transition from loading to unloading, i.e. positive strain increment
        # to negative strain increment
        if self.t_loading == 1 and dstrain < 0.0:
            self.t_loading = -1
            if self.c_strain > self.t_max_strain:
                self.t_max_strain = self.c_strain
            temp = (self.t_max_strain-self.t_min_strain) / (2.0*self.a2*epsy)
            self.t_shift_N = 1 + self.a1 * pow(temp, 0.8)
        # Transition from unloading to loading, i.e. negative strain increment
        # to positive strain increment
        if self.t_loading == -1 and dstrain > 0.0:
            self.t_loading = 1
            if self.c_strain < self.t_min_strain:
                self.t_min_strain = self.c_strain
            temp = (self.t_max_strain-self.t_min_strain) / (2.0*self.a4*epsy)
            self.t_shift_P = 1 + self.a3 * pow(temp, 0.8)

    def get_strain(self):
        return self.t_strain
    def get_stress(self):
        return self.t_stress
    def get_tangent(self):
        return self.t_tangent

    def commit_state(self):
        # history variables
        self.c_min_strain = self.t_min_strain
        self.c_max_strain = self.t_max_strain
        self.c_shift_P = self.t_shift_P
        self.c_shift_N = self.t_shift_N
        self.c_loading = self.t_loading
        # state variables
        self.c_strain = self.t_strain
        self.c_stress = self.t_stress
        self.c_tangent = self.t_tangent

    def revert_to_last_commit(self):
        pass
    def revert_to_start(self):
        pass

