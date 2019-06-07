from analysis.algorithm.EquiSolnAlgo import EquiSolnAlgo

CURRENT_TANGENT = 0
INITIAL_TANGENT = 1
CURRENT_SECANT = 2
INITIAL_THEN_CURRENT_TANGENT = 3

class NewtonRaphson(EquiSolnAlgo):

    def __init__(self, tangent=CURRENT_TANGENT):
        super().__init__()
        self.tangent = tangent
        self.num_interation = 0

    def solve_current_step(self):
        ana_model = self.get_analysis_model()
        integrator = self.get_incremental_integrator()
        SOE = self.get_linear_SOE()

        if ana_model is None or integrator is None or SOE is None:
            print('WARNING NewtonRaphson::solve_current_step() - setLinks() has')
            print(' not been called - or no ConvergenceTest has been set\n')
            return -5
        if integrator.formUnbalance() < 0:
            print('WARNING NewtonRaphson::solve_current_step() -')
            print('the Integrator failed in formUnbalance()\n')
            return -2
        # set itself as the ConvergenceTest objects EquiSolnAlgo
        self.test.setEquiSolnAlgo(self)
        if self.test.start() < 0:
            print('NewtnRaphson::solve_current_step() - the ConvergenceTest object failed in start()\n')
            return -3

        result = -1
        self.num_interation = 0
        while result==-1:
            if self.tangent==INITIAL_THEN_CURRENT_TANGENT:
                if self.num_interation==0:
                    # SOLUTION_ALGORITHM_tangentFlag = INITIAL_TANGENT ???
                    if self.integrator.formTangent(INITIAL_TANGENT) < 0:
                        print('WARNING NewtonRaphson::solve_current_step() -')
                        print('the Integrator failed in formTangent()\n')
                        return -1
                else:
                    if self.integrator.formTangent(CURRENT_TANGENT) < 0:
                        print('WARNING NewtonRaphson::solve_current_step() -')
                        print('the Integrator failed in formTangent()\n')
                        return -1
            else:
                if integrator.formTangent(CURRENT_TANGENT) < 0:
                    print('WARNING NewtonRaphson::solve_current_step() -')
                    print('the Integrator failed in formTangent()\n')
                    return -1
            if SOE.solve() < 0:
                print('WARNING NewtonRaphson::solve_current_step() -')
                print('the LinearSysOfEqn failed in solve()\n')
                return -3
            if integrator.update(SOE.getX()) < 0:
                print('WARNING NewtonRaphson::solve_current_step() -')
                print('the Integrator failed in update()\n')
                return -4
            if integrator.formUnbalance() < 0:
                print('WARNING NewtonRaphson::solve_current_step() -')
                print('the Integrator failed in formUnbalance()\n')
                return -2

            result = self.test.test()

