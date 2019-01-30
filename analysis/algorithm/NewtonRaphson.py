from analysis.algorithm.EquiSolnAlgo import EquiSolnAlgo

CURRENT_TANGENT = 0
INITIAL_TANGENT = 1
CURRENT_SECANT = 2
INITIAL_THEN_CURRENT_TANGENT = 3

class NewtonRaphson(EquiSolnAlgo):

    def __init__(self, tangent=CURRENT_TANGENT):
        super().__init__()
        self.tangent = tangent
        self.numInteration = 0

    def solveCurrentStep(self):
        theAnaModel = self.getAnalysisModel()
        theIntegrator = self.getIncrementalIntegrator()
        theSOE = self.getLinearSOE()

        if theAnaModel is None or theIntegrator is None or theSOE is None:
            print('WARNING NewtonRaphson::solveCurrentStep() - setLinks() has')
            print(' not been called - or no ConvergenceTest has been set\n')
            return -5
        if theIntegrator.formUnbalance() < 0:
            print('WARNING NewtonRaphson::solveCurrentStep() -')
            print('the Integrator failed in formUnbalance()\n')
            return -2
        # set itself as the ConvergenceTest objects EquiSolnAlgo
        self.theTest.setEquiSolnAlgo(self)
        if self.theTest.start() < 0:
            print('NewtnRaphson::solveCurrentStep() - the ConvergenceTest object failed in start()\n')
            return -3

        result = -1
        self.numInteration = 0
        while result==-1:
            if self.tangent==INITIAL_THEN_CURRENT_TANGENT:
                if self.numInteration==0:
                    # SOLUTION_ALGORITHM_tangentFlag = INITIAL_TANGENT ???
                    if self.theIntegrator.formTangent(INITIAL_TANGENT) < 0:
                        print('WARNING NewtonRaphson::solveCurrentStep() -')
                        print('the Integrator failed in formTangent()\n')
                        return -1
                else:
                    if self.theIntegrator.formTangent(CURRENT_TANGENT) < 0:
                        print('WARNING NewtonRaphson::solveCurrentStep() -')
                        print('the Integrator failed in formTangent()\n')
                        return -1
            else:
                if theIntegrator.formTangent(CURRENT_TANGENT) < 0:
                    print('WARNING NewtonRaphson::solveCurrentStep() -')
                    print('the Integrator failed in formTangent()\n')
                    return -1
            if theSOE.solve() < 0:
                print('WARNING NewtonRaphson::solveCurrentStep() -')
                print('the LinearSysOfEqn failed in solve()\n')
                return -3
            if theIntegrator.update(theSOE.getX()) < 0:
                print('WARNING NewtonRaphson::solveCurrentStep() -')
                print('the Integrator failed in update()\n')
                return -4
            if theIntegrator.formUnbalance() < 0:
                print('WARNING NewtonRaphson::solveCurrentStep() -')
                print('the Integrator failed in formUnbalance()\n')
                return -2

            result = self.theTest.test()

