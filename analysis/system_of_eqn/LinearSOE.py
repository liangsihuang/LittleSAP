# LinearSOE:
# storing linear system of equations of form Ax = b
# abstract base class, subclasses are:
# BandSPDLinearSOE
# SparseSPDLinearSOE
# BandGeneralLinearSOE
# EleByEleLinearSOE
# subclass do not actually store the components of the system, for example the A matrix


class LinearSOE:

    def __init__(self, theLinearSOESolver=None):
        self.theAnalysisModel = None
        self.theSolver = theLinearSOESolver

    def solve(self):
        if self.theSolver is not None:
            return self.theSolver.solve()
        else:
            return -1
    
    def setLinks(self, theModel):
        self.theAnalysisModel = theModel

    def getSolver(self):
        return self.theSolver
    

    
    

    


