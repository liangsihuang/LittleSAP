from scipy.linalg import solve

class FullGenLinSolver:

    def __init__(self):
        self.theSOE = None
    
    def setLinearSOE(self, theFullGenSOE):
        self.theSOE = theFullGenSOE

    def solve(self):
        if self.theSOE is None:
            print('WARNING FullGenLinSolver::solve() - No LinearSOE object has been set.\n')
            return -1
        A = self.theSOE.A
        B = self.theSOE.B
        self.theSOE.X = solve(A, B)
        return 0


        