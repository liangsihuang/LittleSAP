from analysis.ConstraintHandler import  ConstraintHandler
# Responsible for creating the DOF_Group and FE_Element objects, and adding them to the AnalysisModel.
# Also responsible for assigning an initial mapping of dof to equation numbers.

class PlainHandler(ConstraintHandler):

    def __init__(self):
        super().__init__()

    def handle(self):
        # first check links exist to a Domain and an AnalysisModel object
        theDomain = self.getDomain()
        theModel = self.getAnalysisModel()
        theIntegrator = self.getIntegrator()
        if theDomain is None or theModel is None or theIntegrator is None:
            print('WARNING PlainHandler::handle() - setLinks() has not been called.\n')
            return -1
        



