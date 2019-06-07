from analysis.integrator.Integrator import Integrator


class IncrementalIntegrator(Integrator):
    CURRENT_TANGENT = 0
    INITIAL_TANGENT = 1
    CURRENT_SECANT = 2
    INITIAL_THEN_CURRENT_TANGENT = 3
    NO_TANGENT = 4
    SECOND_TANGENT = 5

    def __init__(self):
        super().__init__()
        self.status_flag = self.CURRENT_TANGENT

        self.SOE = None
        self.analysis_model = None
        self.test = None

    def set_links(self, theModel, theLinSOE, theConvergenceTest):
        self.analysis_model = theModel
        self.SOE = theLinSOE
        self.test = theConvergenceTest

    # def setEigenSOE(self):
    #     pass

    # methods to set up the system of equations
    def form_tangent(self, statFlag=CURRENT_TANGENT):
        self.status_flag = statFlag

        if self.analysis_model is None or self.SOE is None:
            print('WARNING IncrementalIntegrator::form_tangent() - no AnalysisModel or LinearSOE have been set. \n')
            return -1

        # zero the A matrix of the linearSOE
        self.SOE.zero_A()

        # the loops to form and add the tangents are broken into two for efficiency when performing parallel computations - CHANGE
        # loop through the FE_Elements adding their contributions to the tangent
        eles = self.analysis_model.get_FEs()
        for tag in eles:
            ele = eles[tag]
            result = self.SOE.add_A(ele.get_tangent(self), ele.get_ID())
            if result < 0:
                print(
                    'WARNING IncrementalIntegrator::form_tangent - failed in add_A for ID ' + str(ele.get_ID()) + ' .\n')
                return -3
        return 0

    def form_unbalance(self):
        if self.analysis_model is None or self.SOE is None:
            print('WARNING IncrementalIntegrator::form_unbalance - no AnalysisModel or LinearSOE has been set.\n')
            return -1
        self.SOE.zero_b()

        if self.form_element_residual() < 0:
            print('WARNING IncrementalIntegrator::form_unbalance - this->form_element_residual failed.\n')
            return -1

        if self.form_nodal_unbalance() < 0:
            print('WARNING IncrementalIntegrator::form_unbalance - this->form_nodal_unbalance failed.\n')
            return -2

        return 0

    # methods to update the domain
    def commit(self):
        if self.analysis_model is None:
            print('WARNING IncrementalIntegrator::commit() - no AnalysisModel object associated with this object.\n')
            return -1
        return self.analysis_model.commit_domain()

    # protected:
    def get_linear_SOE(self):
        return self.SOE

    def get_analysis_model(self):
        return self.analysis_model

    def get_convergence_test(self):
        return self.test

    def form_element_residual(self):
        # loop through the FE_Elements and add the residual
        theEles2 = self.analysis_model.get_FEs()
        for tag in theEles2:
            ele = theEles2[tag]
            result = self.SOE.add_b(ele.get_residual(self), ele.get_ID())
            if result < 0:
                print('WARNING IncrementalIntegrator::form_element_residual - failed in add_b for ID ' + str(
                    ele.get_ID()) + '.\n')
                return -2
        return 0

    def form_nodal_unbalance(self):
        # loop through the DOF_Groups and add the unbalance
        theDOFs = self.analysis_model.get_DOFs()
        for tag in theDOFs:
            dof = theDOFs[tag]
            result = self.SOE.add_b(dof.get_unbalance(self), dof.get_ID())
            if result < 0:
                print('WARNING IncrementalIntegrator::form_nodal_unbalance - failed in add_b for ID ' + str(
                    dof.get_ID()) + '.\n')
                return -2
        return 0
