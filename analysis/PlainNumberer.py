from analysis.DOF_Numberer import DOF_Numberer


class PlainNumberer(DOF_Numberer):

    def __init__(self):
        super().__init__()

    def numberDOF(self, lastDOF):
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
        