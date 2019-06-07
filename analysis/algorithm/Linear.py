from analysis.algorithm.EquiSolnAlgo import EquiSolnAlgo

CURRENT_TANGENT = 0
class Linear(EquiSolnAlgo):

    def __init__(self, theTangent = CURRENT_TANGENT, fact = 0):
        super().__init__()
        self.incr_tangent = theTangent
        self.factor_once = fact

    def solve_current_step(self):
        analysis_model = self.get_analysis_model()
        SOE = self.get_linear_SOE()
        inc_integrator = self.get_incremental_integrator()
        if analysis_model is None or inc_integrator is None or SOE is None:
            print('WARNING Linear::solve_current_step() - setLinks() has not been called.\n')
            return -5
        
        if self.factor_once != 2:
            if inc_integrator.form_tangent(self.incr_tangent) < 0 :
                print('WARNING Linear::solve_current_step() - the Integrator failed in formTangent().\n')
                return -1
            if self.factor_once == 1:
                self.factor_once = 2
        
        if inc_integrator.form_unbalance() < 0:
            print('WARNING Linear::solve_current_step() - the Integrator failed in formUnbalance().\n')
            return -2
        
        if SOE.solve() < 0:
            print('WARNING Linear::solve_current_step() - theLinearSOE failed in solve().\n')
            return -3
        
        deltaU = SOE.get_x()

        if inc_integrator.update(deltaU) < 0:
            print('WARNING Linear::solve_current_step() - the Integrator failed in update().\n')
            return -4
        
        return 0
        
    # def setConvergenceTest(self, theNewTest):
    #     pass


