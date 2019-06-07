from analysis.algorithm.SolutionAlgorithm import SolutionAlgorithm

class EquiSolnAlgo(SolutionAlgorithm):

    def __init__(self):
        super().__init__()
        self.model = None
        self.integrator = None
        self.sys_of_eqn = None
        self.test = None
    
    def set_links(self, theNewModel, theNewIntegrator, theSOE, theConvergenceTest):
        self.model = theNewModel
        self.integrator = theNewIntegrator
        self.sys_of_eqn = theSOE
        self.test = theConvergenceTest

    # def solveCurrentStep(self):
    #     pass # 纯虚函数

    def set_convergence_test(self, theConvergenceTest):
        self.test = theConvergenceTest
    
    def get_convergence_test(self):
        return self.test
    
    # def Print(self):
    #     pass # 纯虚函数

    def get_analysis_model(self):
        return self.model

    def get_incremental_integrator(self):
        return self.integrator

    def get_linear_SOE(self):
        return self.sys_of_eqn
    


