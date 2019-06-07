from domain.DomainComponent import DomainComponent

class SP_Constraint(DomainComponent):
    # 为什么要统计数量和记录tag？
    num_SPs = 0
    next_tag = 0

    def __init__(self, node, ndof, value, ISconstant):
        SP_Constraint.next_tag = SP_Constraint.next_tag + 1
        super().__init__(SP_Constraint.next_tag)
        self.node_tag = node
        self.DOF_number = ndof
        self.valueR = value
        self.valueC = value
        self.is_constant = ISconstant
        self.loadpattern_tag = -1

        SP_Constraint.num_SPs = SP_Constraint.num_SPs + 1

    
    def __del__(self):
        SP_Constraint.num_SPs = SP_Constraint.num_SPs - 1
        if SP_Constraint.num_SPs == 0 :
            SP_Constraint.next_tag = 0

    def get_node_tag(self):
        return self.node_tag
    
    def get_DOF_number(self):
        return self.DOF_number
    
    def apply_constraint(self, loadFactor):
        # as SP_Constraint objects are time invariant nothing is done
        if self.is_constant == False:
            self.valueC = loadFactor * self.valueR
        return 0
    # 还有：
    # The constraint may be time-varying .. time varying constarints however 
    # must be implemented using subclasses.
    
    # def getValue(self):
    #     pass
    
    def is_homogeneous(self):
        if self.valueR == 0.0:
            return  True
        else:
            return False
    
    # def setLoadPatternTag(self, loadpattern_tag):
    #     pass
    #
    # def getLoadPatternTag(self):
    #     pass
    
    # def sendSelf(self):
    #     pass
    # def recvSelf(self):
    #     pass
    # def Print(self):
    #     pass
