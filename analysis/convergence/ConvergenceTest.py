import numpy as np

class CTestNormUnbalance:

    def __init__(self, tol, maxNumIter, printFlag, normType=2, maxincr=-1, maxTol=1.7e307):
        self.theSOE = None
        self.tol = tol
        self.maxTol = maxTol
        self.maxNumIter = maxNumIter
        self.currentIter = 0
        self.printFlag = printFlag
        self.nType = normType
        self.norms = np.zeros(maxNumIter)
        self.maxIncr = maxincr
        self.numIncr = 0
        if self.maxIncr < 0:
            self.maxIncr = maxNumIter

    def setEquiSolnAlgo(self, theAlgo):
        self.theSOE = theAlgo.getLinearSOE()

    def start(self):
        if self.theSOE is None:
            print('WARNING: CTestNormUnbalance::test() - no SOE returning true\n')
            return -1
        # set iteration count = 1
        self.norms[:] = 0.0
        self.currentIter = 1
        self.numIncr = 0
        return 0

    def test(self):
        # check to ensure the SOE has been set - this should not happen if the
        # return from start() is checked
        if self.theSOE is None:
            print('WARNING: CTestNormUnbalance::test() - no SOE set.\n')
            return -2
        # check to ensure the algo does invoke start() - this is needed otherwise
        # may never get convergence later on in analysis!
        if self.currentIter == 0:
            print('WARNING: CTestNormUnbalance::test() - start() was never invoked.\n')
            return -2
        # get the B vector & determine it's norm & save the value in norms vector
        x = self.theSOE.getB()
        nType