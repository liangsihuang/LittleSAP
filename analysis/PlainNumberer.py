from analysis.DOF_Numberer import DOF_Numberer


class PlainNumberer(DOF_Numberer):

    def __init__(self):
        super().__init__()

    def number_DOF(self, lastDOF=-1):
        eqnNumber = 0  # start equation number = 0
        # get a pointer to the model & check its not null
        model = self.get_analysis_model()
        domain = None
        if model is not None:
            domain = model.get_domain()
        if model is None or domain is None:
            print('WARNING PlainNumberer::number_DOF(int) - - no AnalysisModel - has setLinks() been invoked?\n')
            return -1
        if lastDOF!=-1:
            print('WARNING PlainNumberer::number_DOF(int lastDOF): does not use the lastDOF as requested\n')
        # iterate throgh  the DOFs first time setting -2 values
        DOFs = model.get_DOFs()
        for tag in DOFs:
            dof = DOFs[tag]
            theID = dof.get_ID()
            for i in range(0, len(theID)):
                if theID[i] == -2:
                    dof.set_ID(i, eqnNumber)
                    eqnNumber += 1

        # iterate through  the DOFs second time setting -3 values
        # iterate through the DOFs one last time setting any -4 values
        eqnNumber -= 1
        numEqn = eqnNumber + 1

        # iterate through the FE_Element getting them to set their IDs
        eles = model.get_FEs()
        for tag in eles:
            ele = eles[tag]
            ele.set_ID()

        # set the numOfEquation in the Model
        model.set_num_eqn(numEqn)
        return numEqn
        