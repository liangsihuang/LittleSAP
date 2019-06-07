# LinearSOE:
# storing linear system of equations of form Ax = b
# abstract base class, subclasses are:
# BandSPDLinearSOE
# SparseSPDLinearSOE
# BandGeneralLinearSOE
# EleByEleLinearSOE
# subclass do not actually store the components of the system, for example the A matrix


class LinearSOE:

    def __init__(self, linear_SOE_solver=None):
        self.analysis_model = None
        self.solver = linear_SOE_solver

    def solve(self):
        if self.solver is not None:
            return self.solver.solve()
        else:
            return -1
    
    def set_links(self, model):
        self.analysis_model = model

    def get_solver(self):
        return self.solver
    

    
    

    


