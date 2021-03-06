from analysis.ConstraintHandler import  ConstraintHandler
from analysis.model.DOF_Group import  DOF_Group
from analysis.model.FE_Element import  FE_Element
# Responsible for creating the DOF_Group and FE_Element objects, and adding them to the AnalysisModel.
# Also responsible for assigning an initial mapping of dof to equation numbers.

class PlainHandler(ConstraintHandler):

    def __init__(self):
        super().__init__()

    def handle(self, nodesNumberedLast=None):
        # nodesNumberedLast is ID/narray
        # first check links exist to a Domain and an AnalysisModel object
        domain = self.get_domain()
        model = self.get_analysis_model()
        integrator = self.get_integrator()

        if domain is None or model is None or integrator is None:
            print('WARNING PlainHandler::handle() - setLinks() has not been called.\n')
            return -1

        SPs = domain.get_domain_and_loadpattern_SPs()

        # initialise the DOF_Groups and add them to the AnalysisModel.
        # must of course set the initial IDs
        nodes = domain.get_nodes()
        numDOFgroup = 0
        count3 = 0
        countDOF = 0
        for tag in nodes:
            node = nodes[tag]
            numDOFgroup += 1
            dof_group = DOF_Group(numDOFgroup, node)
            # initially set all the ID value to -2
            id1 = dof_group.get_ID()
            for j in range(0, len(id1)):
                dof_group.set_ID(j, -2)
                countDOF += 1
            # loop through the SP_Constraints to see if any of the
            # DOFs are constrained, if so set initial ID value to -1
            nodeTag = node.get_tag()
            for sp in SPs:
                if sp.get_node_tag() == nodeTag:
                    dofnumber = sp.get_DOF_number()
                    if id1[dofnumber-1] == -2:
                        dof_group.set_ID(dofnumber-1, -1)
                        countDOF -= 1
                    else:
                        print('WARNING PlainHandler::handle() - multiple single point constraints at DOF')
                        print(str(dofnumber) + ' for node' + str(sp.get_node_tag()))

            # MP 略 -4
            node.set_DOF_group(dof_group)
            model.add_DOF_group(dof_group)

        # set the number of eqn in the model
        model.set_num_eqn(countDOF)

        # now see if we have to set any of the dof's to -3
        # what is -3 ?
        # if nodesNumberedLast is not None:
        #     pass

        # initialise the FE_Elements and add to the AnalysisModel.
        theEles = domain.get_elements()
        numFe = 0
        for tag in theEles:
            ele = theEles[tag]
            # just a regular element .. create an FE_Element for it & add to AnalysisModel
            numFe += 1
            fe = FE_Element(numFe, ele)
            model.add_FE_element(fe)

        return count3


