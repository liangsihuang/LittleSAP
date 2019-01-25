from material.UniaxialMaterial import UniaxialMaterial

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
        # Sets all history and state variables to initial values
        # History variables
        self.CminStrain = 0.0
        self.CmaxStrain = 0.0
        self.CshiftP = 1.0
        self.CshiftN = 1.0
        self.Cloading = 0

        self.TminStrain = 0.0
        self.TmaxStrain = 0.0
        self.TshiftP = 1.0
        self.TshiftN = 1.0
        self.Tloading = 0

        # State variables
        self.Cstrain = 0.0
        self.Cstress = 0.0
        self.Ctangent = E0

        self.Tstrain = 0.0
        self.Tstress = 0.0
        self.Ttangent = E0