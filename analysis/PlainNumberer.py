from analysis.DOF_Numberer import DOF_Numberer


class PlainNumberer(DOF_Numberer):

    def __init__(self):
        super().__init__()

    def numberDOF(self, lastDOF=-1):
        eqnNumber = 0  # start equation number = 0
        # get a pointer to the model & check its not null
        theModel = self.getAnalysisModel()
        theDomain = None
        if theModel is not None:
            theDomain = theModel.getDomain()
        if theModel is None or theDomain is None:
            print('WARNING PlainNumberer::numberDOF(int) - - no AnalysisModel - has setLinks() been invoked?\n')
            return -1
        if lastDOF!=-1:
            print('WARNING PlainNumberer::numberDOF(int lastDOF): does not use the lastDOF as requested\n')
        # iterate throgh  the DOFs first time setting -2 values
        theDOFs = theModel.getDOFs()
        for tag in theDOFs:
            dof = theDOFs[tag]
            theID = dof.getID()
            for i in range(0, len(theID)):
                if theID[i] == -2:
                    dof.setID(i, eqnNumber)
                    eqnNumber += 1

        # iterate through  the DOFs second time setting -3 values
        # iterate through the DOFs one last time setting any -4 values
        eqnNumber -= 1
        numEqn = eqnNumber + 1

        # iterate through the FE_Element getting them to set their IDs
        theEles = theModel.getFEs()
        for tag in theEles:
            ele = theEles[tag]
            ele.setID()

        # set the numOfEquation in the Model
        theModel.setNumEqn(numEqn)
        return numEqn
        