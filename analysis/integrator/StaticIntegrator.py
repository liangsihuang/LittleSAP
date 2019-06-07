from analysis.integrator.IncrementalIntegrator import IncrementalIntegrator


class StaticIntegrator(IncrementalIntegrator):

    def __init__(self):
        super().__init__()

    # methods which define what the FE_Element and DOF_Groups add to the system of equation object
    def form_ele_tangent(self, theEle):
        # theEle is FE_Element
        if self.status_flag == IncrementalIntegrator.CURRENT_TANGENT:
            theEle.zero_tangent()
            theEle.add_Kt_to_tang()
        elif self.status_flag == IncrementalIntegrator.INITIAL_TANGENT:
            theEle.zero_tangent()
            theEle.add_Ki_to_tang()
        return 0

    def form_ele_residual(self, theEle):
        # theEle is FE_Element
        # only elements residual needed
        theEle.zero_residual()
        theEle.add_R_to_residual()
        return 0

    # def formNodTangent(self, theDof):
    #     # should never be called
    #     print('StaticIntegrator::formNodTangent() - this method should never have been called!\n')
    #     return -1

    def form_nod_unbalance(self, theDof):
        # theDof is DOF_Group
        # only nodes unbalance need be added
        theDof.zero_unbalance()
        theDof.add_P_to_unbalance()
        return 0
