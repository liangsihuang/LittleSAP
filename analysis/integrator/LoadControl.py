from analysis.integrator.StaticIntegrator import StaticIntegrator


class LoadControl(StaticIntegrator):

    def __init__(self, dLambda, numIncr, minLambda, maxLambda):
        super().__init__()
        self.delta_lambda = dLambda
        self.spec_num_incr_step = numIncr # Jd
        self.num_incr_last_step = numIncr # J(i-1)
        self.d_lambda_min = minLambda # min values for dlambda at step(i)
        self.d_lambda_max = maxLambda # max ...

        # to avoid divide-by-zero error on first update() ensure numIncr != 0
        if numIncr == 0 :
            print('WARNING LoadControl::LoadControl() - numIncr set to 0, 1 assumed.\n')
            self.spec_num_incr_step = 1.0
            self.num_incr_last_step = 1.0


    def new_step(self):
        theModel = self.analysis_model
        if theModel is None:
            print('LoadControl::newStep() - no associated AnalysisModel.\n')
            return -1
        # determine delta lambda for this step based on dLambda and #iter of last step
        factor = self.spec_num_incr_step / self.num_incr_last_step
        self.delta_lambda *= factor

        if self.delta_lambda < self.d_lambda_min:
            self.delta_lambda = self.d_lambda_min
        elif self.delta_lambda > self.d_lambda_max:
            self.delta_lambda = self.d_lambda_max

        currentLambda = theModel.get_current_domain_time()
        currentLambda += self.delta_lambda
        theModel.apply_load_domain(currentLambda)

        self.num_incr_last_step = 0
        return 0
    
    def update(self, deltaU):
        # deltaU 是 Vector
        myModel = self.get_analysis_model()
        theSOE = self.get_linear_SOE()
        if myModel is None or theSOE is None:
            print('WARNING LoadControl::update() - No AnalysisModel or LinearSOE has been set.\n')
            return -1
        
        myModel.incr_disp(deltaU)
        if myModel.update_domain() < 0:
            print('LoadControl::update - model failed to update for new dU.\n')
            return -1
        
        # set deltaU for the convergence test
        theSOE.set_x(deltaU)
        self.num_incr_last_step += 1
        return 0
    
    def set_delta_lambda(self, newValue):
        # we set the #incr at last step = #incr so get newValue incr
        self.num_incr_last_step = self.spec_num_incr_step
        self.delta_lambda = newValue
        return 0
    
    
    
    

