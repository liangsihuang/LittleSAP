from analysis.integrator.StaticIntegrator import StaticIntegrator

class DisplacementControl(StaticIntegrator):

    def __init__(self, node, dof, increment, theDomain, numIncrStep, minIncrement, maxIncrement):
        super().__init__()
        self.theNode = node
        self.theDof = dof
        self.theIncrement = increment
        self.theDomain = theDomain
        self.theDofID = -1

        self.deltaUhat = None
        self.deltaUbar = None
        self.deltaU = None
        self.deltaUstep = None
        self.phat = None
        self.deltaLambdaStep = 0.0
        self.currentLambda = 0.0

        self.specNumIncrStep = numIncrStep
        self.numIncrLastStep = numIncrStep
        self.minIncrement = minIncrement
        self.maxIncrement = maxIncrement

        # to avoid divide-by-zero error on first update() ensure numIncr != 0
        if numIncrStep == 0:
            print('WARNING DisplacementControl::DisplacementControl() -'
                  ' numIncr set to 0, 1 assumed\n')
            self.specNumIncrStep = 1
            self.numIncrLastStep = 1

    def newStep(self):
        if self.theDofID == -1:
            print('DisplacementControl::newStep()-dof is fixed or constrained (or domainChanged has not been called!)\n')
            return -1
        # get pointers to AnalysisModel and LinearSOE
        theModel = self.getAnalysisModel()
        theLinSOE = self.getLinearSOE()
        if theModel is None or theLinSOE is None:
            print('WARNING DisplacementControl::newStep()-No AnalysisModel or LinearSOE has been set\n')
            return -1
        # determine increment for this iteration
        factor = self.specNumIncrStep / self.numIncrLastStep
        self.theIncrement *= factor
        if self.theIncrement < self.minIncrement:
            self.theIncrement = self.minIncrement
        elif self.theIncrement > self.maxIncrement:
            self.theIncrement = self.maxIncrement
        # get the current load factor
        self.currentLambda = theModel.getCurrentDomainTime()
        # determine dUhat
        self.formTangent()
        theLinSOE.setB(self.phat)
        if theLinSOE.solve() < 0:
            print('DisplacementControl::newStep(void) - failed in solver\n')
            return -1

        self.deltaUhat = theLinSOE.getX()
        dUhat = self.deltaUhat # this is the Uft in the nonlinear lecture notes
        dUahat = dUhat[self.theDofID] # this is the component of the Uft in our nonlinear lecture notes

        if dUahat==0.0:
            print('WARNING DisplacementControl::newStep() '
                  'dUahat is zero -- zero reference displacement at control node DOF\n')
            return -1
        # determine delta lambda(1) == dlambda
        dlambda = self.theIncrement/dUahat # this is the dlambda of the 1st step
        self.deltaLambdaStep = dlambda
        self.currentLambda += dlambda

        self.deltaU = dUhat
        self.deltaU *= dlambda # this is eq(4) in the paper {dU}_1=dLAmbda1*Uft.
        self.deltaUstep = self.deltaU

        # update model with delta lambda and delta U
        theModel.incrDisp(self.deltaU)
        theModel.applyLoadDomain(self.currentLambda)
        if theModel.updateDomain() < 0:
            print('DisplacementControl::newStep - model failed to update for new dU\n')
            return -1
        self.numIncrLastStep = 0
        return 0

