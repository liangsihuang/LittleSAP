import numpy as np

class CTestNormUnbalance:

    def __init__(self, tol, max_num_iter, print_flag, normType=2, maxincr=-1, max_tol=1.7e307):
        self.SOE = None
        self.tol = tol
        self.max_tol = max_tol
        self.max_num_iter = max_num_iter
        self.current_iter = 0
        self.print_flag = print_flag
        self.n_type = normType
        self.norms = np.zeros(max_num_iter)
        self.maxIncr = maxincr
        self.numIncr = 0
        if self.maxIncr < 0:
            self.maxIncr = max_num_iter

    def setEquiSolnAlgo(self, theAlgo):
        self.SOE = theAlgo.getLinearSOE()

    def start(self):
        if self.SOE is None:
            print('WARNING: CTestNormUnbalance::test() - no SOE returning true\n')
            return -1
        # set iteration count = 1
        self.norms[:] = 0.0
        self.current_iter = 1
        self.numIncr = 0
        return 0

    def test(self):
        # check to ensure the SOE has been set - this should not happen if the
        # return from start() is checked
        if self.SOE is None:
            print('WARNING: CTestNormUnbalance::test() - no SOE set.\n')
            return -2
        # check to ensure the algo does invoke start() - this is needed otherwise
        # may never get convergence later on in analysis!
        if self.current_iter == 0:
            print('WARNING: CTestNormUnbalance::test() - start() was never invoked.\n')
            return -2
        # get the B vector & determine it's norm & save the value in norms vector
        x = self.SOE.getB()
        n_type