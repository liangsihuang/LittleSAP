
# Responsible for creating the DOF_Group and FE_Element objects, and adding them to the AnalysisModel.
# Also responsible for assigning an initial mapping of dof to equation numbers.

class ConstraintHandler():

    def __init__(self):
        self.domain = None
        self.analysis_model = None
        self.integrator = None

    def set_links(self, domain, theModel, integrator):
        self.domain = domain
        self.analysis_model = theModel
        self.integrator = integrator
    
    def done_numbering_DOF(self):
        # iterate through the FE_Element getting them to set their IDs
        eles = self.analysis_model.get_FEs()
        for tag in eles:
            ele = eles[tag]
            ele.set_ID()
        return 0
    
    def get_domain(self):
        return self.domain

    def get_analysis_model(self):
        return self.analysis_model

    def get_integrator(self):
        return self.integrator
    
    def clear_all(self):
        # for the nodes reset the DOF_Group pointers to 0
        domain = self.get_domain()
        if domain is None:
            return
        nodes = domain.get_nodes()
        for tag in nodes:
            theNod = nodes[tag]
            theNod.set_DOF_group(None)

    # 以下方法：有需要的子类会重写，但并不是所有子类都有，为了程序的通用性
    def apply_load(self):
        return 0

    def update(self):
        return 0