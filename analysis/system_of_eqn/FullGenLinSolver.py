from scipy.linalg import solve

class FullGenLinSolver:

    def __init__(self):
        self.SOE = None
    
    def set_linear_SOE(self, theFullGenSOE):
        self.SOE = theFullGenSOE

    def solve(self):
        if self.SOE is None:
            print('WARNING FullGenLinSolver::solve() - No LinearSOE object has been set.\n')
            return -1
        A = self.SOE.A
        b = self.SOE.b
        self.SOE.x = solve(A, b)
        return 0


        