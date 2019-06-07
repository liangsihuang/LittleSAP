from domain.DomainComponent import DomainComponent

class Element(DomainComponent):

    def __init__(self, tag):
        super().__init__(tag)
        self.alpha_M = 0.0
        self.beta_K = 0.0
        self.beta_K0 = 0.0
        self.beta_Kc = 0.0
        self.Kc = None         # pointer to hold last committed matrix if needed for rayleigh damping
        self.previous_K = None
        self.num_previous_K = 0

        self.index = -1
        self.node_index = -1

    
    # methods dealing with nodes and number of external dof

    # def getCharacteristicLength(self):
    #     pass
        
    # methods dealing with commited state and update
    # def commitState(self):
    #     if self.Kc != None:
    #         Kc = self.getTangentStiff() # Python 没有虚函数，只能把这段写在每个子类中
    #     return 0

    # def revertToStart(self):
    #     pass
    # def update(self):
    #     pass

    # methods to return the current linearized stiffness, damping and mass matrices
    # def getDamp(self):
    #     pass
    # def getMass(self):
    #     pass
    # def getGeometricTangentStiff(self):
    #     pass

    # methods for applying loads
    # def zeroLoad(self):
    #     pass # 空函数？有鬼用？（注意：虚函数）
    # def addLoad(self, theLoad, loadFactor):
    #     pass
    # def addLoad(self, theLoad, loadFactors):
    # def addInertiaLoadToUnbalance(self, accel):
    #     pass
    # def setRayleighDampingFactors(self, alpha_M, beta_K, beta_K0, beta_Kc):
    #     pass

    # methods for obtaining resisting force (force includes elemental loads)
    # def getResistingForceIncInertia(self):
    #     pass

    # methods for obtaining information specific to an element
