from analysis.Analysis import Analysis

class StaticAnalysis(Analysis):
    def __init__(self, domain, theHandler, theNumberer, theModel, theSolnAlgo, theLinSOE, theStaticIntegrator, theConvergenceTest=None):
        super().__init__(domain)
        self.constraint_handler = theHandler
        self.DOF_numberer = theNumberer
        self.analysis_model = theModel
        self.algorithm = theSolnAlgo
        self.SOE = theLinSOE
        self.eigen_SOE = None
        self.integrator = theStaticIntegrator
        self.test = theConvergenceTest

        self.domain_stamp = 0

        # first we set up the links needed by the elements in the aggregation
        self.analysis_model.set_links(domain, theHandler)
        self.constraint_handler.set_links(domain, theModel, theStaticIntegrator)
        self.DOF_numberer.set_links(theModel)
        self.integrator.set_links(theModel, theLinSOE, theConvergenceTest)
        self.algorithm.set_links(theModel, theStaticIntegrator, theLinSOE, theConvergenceTest)

        if theConvergenceTest is not None:
            self.algorithm.set_convergence_test(theConvergenceTest)
    
    # def clear_all(self):
    #     pass

    def analyze(self, numSteps):
        result = 0
        domain = self.get_domain()
        for i in range(0, numSteps):
            # result = self.analysis_model.analysis_step() # 有什么意义？
            # if result<0 :
            #     print('StaticAnalysis::analyze() - the AnalysisModel failed at iteration: '+str(i))
            #     print(' with domain at load factor '+str(domain.get_current_time())+'.\n')
            #     domain.revert_to_last_commit()
            #     return -2
            
            stamp = domain.has_domain_changed()
            if self.domain_stamp != stamp:
                self.domain_stamp = stamp
                result = self.domain_changed()
                if result < 0:
                    print('StaticAnalysis::analyze() - domain_changed failed at step '+str(i)+' of '+str(numSteps)+'.\n')
                    return -1

            result = self.integrator.new_step()
            if result < 0:
                print('StaticAnalysis::analyze() - the Integrator failed at iteration: '+str(i))
                print(' with domain at load factor '+str(domain.get_current_time())+'.\n')
                domain.revert_to_last_commit()
                self.integrator.revert_to_last_step()
                return -2

            result = self.algorithm.solve_current_step()
            if result < 0:
                print('StaticAnalysis::analyze() - the Algorithm failed at iteration: '+str(i))
                print(' with domain at load factor '+str(domain.get_current_time())+'.\n')
                domain.revert_to_last_commit()
                self.integrator.revert_to_last_step()   # LoadControl 并没有 revert_to_last_step()
                return -3
            
            result = self.integrator.commit()
            if result < 0:
                print('StaticAnalysis::analyze() - the Integrator failed at iteration: '+str(i))
                print(' with domain at load factor '+str(domain.get_current_time())+'.\n')
                domain.revert_to_last_commit()
                self.integrator.revert_to_last_step()
                return -4
            
            return 0






    # def eigen(self):
    #     pass
    # def initialize(self):
    #     pass

    def domain_changed(self):
        # result = 0
        domain = self.get_domain()
        stamp = domain.has_domain_changed()
        self.domain_stamp = stamp

        self.analysis_model.clear_all()
        self.constraint_handler.clear_all()

        # now we invoke handle() on the constraint handler which causes the creation of FE_Element
        # and DOF_Group objects and their addition to the AnalysisModel
        result = self.constraint_handler.handle()
        if result < 0:
            print('StaticAnalysis::domain_changed() - ConstraintHandler::handle() failed')
            return -1
        
        # now we invoke number() on the numberer which causes equation numbers to be assigned to all the
        # DOFs in the AnalysisModel.
        result = self.DOF_numberer.number_DOF()
        if result < 0:
            print('StaticAnalysis::domain_changed() - DOF_Numberer::number_DOF() failed.')
            return -2
        
        result = self.constraint_handler.done_numbering_DOF()
        if result < 0:
            print('StaticAnalysis::domain_changed() - ConstraintHandler::done_numbering_DOF() failed.')
            return -2
        # we invoke set_size() on the LinearSOE which causes that object to determine its size
        theGraph = self.analysis_model.get_DOF_graph()
        result = self.SOE.set_size(theGraph)
        if result < 0:
            print('StaticAnalysis::domain_changed() - LinearSOE::set_size() failed')
            return -3
        # if self.eigen_SOE is not None:
        self.analysis_model.clear_DOF_graph()

        # finally we invoke domain_changed on the Integrator and Algorithm objects .. informing them that the model has changed
        result = self.integrator.domain_changed()
        if result < 0:
            print('StaticAnalysis::domain_changed() - Integrator::domain_changed() failed')
            return -4
        
        result = self.algorithm.domain_changed()
        if result < 0:
            print('StaticAnalysis::domain_changed() - Algorithm::domain_changed() failed')
            return -5
        
        return 0
        

    # def setNumberer(self, theNumberer):
    #     pass
    # def setAlgorithm(self, algorithm):
    #     pass
    # def setIntegrator(self, integrator):
    #     pass
    # def setLinearSOE(self, SOE):
    #     pass
    # def setConvergenceTest(self, test):
    #     pass
    # def setEigenSOE(self, SOE):
    #     pass
    #
    # def getAlgorithm(self):
    #     pass
    # def getIntegrator(self):
    #     pass
    # def getConvergenceTest(self):
    #     pass
    
    


                
        
