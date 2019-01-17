from analysis.ConstraintHandler import  ConstraintHandler
from analysis.DOF_Group import  DOF_Group
from analysis.FE_Element import  FE_Element
# Responsible for creating the DOF_Group and FE_Element objects, and adding them to the AnalysisModel.
# Also responsible for assigning an initial mapping of dof to equation numbers.

class PlainHandler(ConstraintHandler):

    def __init__(self):
        super().__init__()

    def handle(self, nodesNumberedLast=None):
        # nodesNumberedLast is ID/narray
        # first check links exist to a Domain and an AnalysisModel object
        theDomain = self.getDomain()
        theModel = self.getAnalysisModel()
        theIntegrator = self.getIntegrator()
        if theDomain is None or theModel is None or theIntegrator is None:
            print('WARNING PlainHandler::handle() - setLinks() has not been called.\n')
            return -1

        allSPs = {}
        theSPs = theDomain.getDomainAndLoadPatternSPs()
        for sp in theSPs:
            if sp.isHomogeneous() == False:
                print('ARNING PlainHandler::handle() - non-homogeneos constraint')
                print(' for node' + str(sp.getNodeTag()) + '.\n')
            allSPs[sp.getNodeTag()] = sp

        # initialise the DOF_Groups and add them to the AnalysisModel.
        # must of course set the initial IDs
        theNod = theDomain.getNodes()
        numDOF = 0
        count3 = 0
        countDOF = 0
        for node in theNod:
            numDOF += 1
            dof = DOF_Group(numDOF, node)
            # initially set all the ID value to -2
            id1 = dof.getID()
            for j in range(0, len(id1)):
                dof.setID(j, -2)
                countDOF += 1
            # loop through the SP_Constraints to see if any of the
            # DOFs are constrained, if so set initial ID value to -1
            nodeID = node.getTag()
            for sp in allSPs:
                id1 = dof.getID()
                dofnumber = sp.getDOF_Number()
                if id1[dofnumber] == -2:
                    dof.setID(dofnumber, -1)
                    countDOF -= 1
                else:
                    print('WARNING PlainHandler::handle() - multiple single pointconstraints at DOF ')
                    print(str(dofnumber) + 'for node' + str(sp.getNodeTag()))

            # MP 略 -4
            node.setDOF_Group(dof)
            theModel.addDOF_Group(dof)

        # set the number of eqn in the model
        theModel.setNumEqn(countDOF)

        # now see if we have to set any of the dof's to -3
        # what is -3 ?
        if nodesNumberedLast is not None:
            pass

        # initialise the FE_Elements and add to the AnalysisModel.
        theEles = theDomain.getElements()
        numFe = 0
        for ele in theEles:
            # just a regular element .. create an FE_Element for it & add to AnalysisModel
            numFe += 1
            fe = FE_Element(numFe, ele)
            theModel.addFE_Element(fe)

        return count3


