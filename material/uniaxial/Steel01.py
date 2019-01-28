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
        self.a1 =a1
        self.a2 = a2
        self.a3 = a3
        self.a4 = a4
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

    def getCopy(self):
        theCopy = Steel01(self.getTag(), self.fy, self.E0, self.b, self.a1, self.a2, self.a3, self.a4)
        theCopy.CminStrain = self.CminStrain
        theCopy.CmaxStrain = self.CmaxStrain
        theCopy.CshiftP = self.CshiftP
        theCopy.CshiftN = self.CshiftN
        theCopy.Cloading = self.Cloading

        theCopy.TminStrain = self.TminStrain
        theCopy.TmaxStrain = self.TmaxStrain
        theCopy.TshiftP = self.TshiftP
        theCopy.TshiftN = self.TshiftN
        theCopy.Tloading =self.Tloading

        theCopy.Cstrain = self.Cstrain
        theCopy.Cstress = self.Cstress
        theCopy.Ctangent = self.Ctangent

        theCopy.Tstrain = self.Tstrain
        theCopy.Tstress = self.Tstress
        theCopy.Ttangent = self.Ttangent

        return theCopy