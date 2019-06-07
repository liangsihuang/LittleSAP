from TaggedObject import TaggedObject
import numpy as np

class DOF_Group(TaggedObject):
    # static variables - single copy for all objects of the class
    num_DOFs = 0
    errVect = np.zeros(1)
    errMatrix = np.zeros((1,1))
    theMatrices = []
    theVectors = []

    def __init__(self, tag, node):
        super().__init__(tag) # tag 从0开始
        
        # protected variables - a copy for each object of the class  
        self.unbalance = None
        self.tangent = None
        self.node = node

        # private variables - a copy for each object of the class  
        self.myID = np.zeros(node.get_number_DOF(), dtype=int)
        self.num_DOF = node.get_number_DOF()

        # get number of DOF & verify valid
        num_DOF = node.get_number_DOF()
        if num_DOF <= 0:
            print('DOF_Group::DOF_Group() - node must have at least 1 dof. \n')
        
        # initially set all the IDs to be -2
        for i in range(0, num_DOF):
            self.myID[i] = -2
        # set the pointers for the tangent and residual
        self.unbalance = np.zeros(self.num_DOF)
        self.tangent = np.zeros((self.num_DOF, self.num_DOF))

        DOF_Group.num_DOFs += 1
        
        
    def set_ID(self, index, value): # 有重载，复制函数
        if index >= 0 and index < self.num_DOF:
            self.myID[index] = value
        else:
            print('WARNING DOF_Group::set_ID - invalid location '+str(index)+' in ID of size '+str(self.num_DOF)+'.\n')

    def get_ID(self):
        return self.myID

    # def doneID(self):
    #     return 0 # 有鬼用
    
    def get_node_tag(self):
        if self.node is not None:
            return self.node.get_tag()
        else:
            return -1

    def get_num_DOF(self):
        return self.num_DOF

    def get_num_free_DOF(self):
        numFreeDOF = self.num_DOF
        for i in range(0, self.num_DOF):
            if self.myID[i] == -1 or self.myID[i] == -4:
                numFreeDOF -= 1
        return numFreeDOF

    def get_num_constrained_DOF(self):
        numConstr = 0
        for i in range(0, self.num_DOF):
            if self.myID[i] < 0:
                numConstr += 1
        return numConstr
    
    # methods to form the tangent
    def get_tangent(self, theIntegrator): # 不call还写出来干嘛？
        if theIntegrator != None:
            theIntegrator.formNodTangent(self) # StaticIntegrator::formNodTangent() - this method should never have been called!
        return self.tangent # is Matrix

    def zero_tangent(self):
        self.tangent[:,:] = 0

    # def addMtoTang(self, fact = 1.0):
    #     pass
    # def addCtoTang(self, fact = 1.0):
    #     pass
    
    # methods to form the unbalance
    def get_unbalance(self, theIntegrator):
        if theIntegrator is not None:
            theIntegrator.form_nod_unbalance(self)
        return self.unbalance # is Vector

    def zero_unbalance(self):
        self.unbalance[:] = 0

    def add_P_to_unbalance(self, fact = 1.0):
        if self.node is not None:
            self.unbalance += self.node.get_unbalanced_load() * fact
        else:
            print('DOF_Group::add_P_to_unbalance() - no Node associated. Subclass should provide the method.\n')

    # def addPIncInertiaToUnbalance(self, fact = 1.0):
    #     pass
    # def addM_Force(self, udotdot, fact = 1.0):
    #     pass
    
    # def getTangForce(self, x, fact=1.0):
    #     pass
    # def getC_Force(self, x, fact=1.0):
    #     pass
    # def getM_Force(self, x, fact=1.0):
    #     pass

    # methods to obtain committed responses from the nodes
    def get_committed_disp(self):
        if self.node is None:
            print('DOF_Group::get_committed_disp: no associated Node, returning the error Vector.\n')
            return DOF_Group.errVect
        return self.node.get_disp()

    # def getCommittedVel(self):
    #     if self.node == None:
    #         print('DOF_Group::getCommittedVel: no associated Node, returning the error Vector.\n')
    #         return DOF_Group.errVect
    #     return self.node.getVel()
    #
    # def getCommittedAccel(self):
    #     if self.node == None:
    #         print('DOF_Group::getCommittedAccel: no associated Node, returning the error Vector.\n')
    #         return DOF_Group.errVect
    #     return self.node.getAccel()
    
    # methods to update the trial response at the nodes
    def set_node_disp(self, u):
        # u is Vector
        if self.node is None:
            print('DOF_Group::setNodeDisp: no associated Node.\n')
            return
        disp = self.unbalance       # ????
        disp = self.node.get_trial_disp() # ????
        # get disp for my dof out of vector u
        for i in range(0, self.num_DOF):
            loc = self.myID[i]
            if loc >= 0:
                disp[i] = u[loc]
        self.node.set_trial_disp(disp)

    # def setNodeVel(self, udot):
    #     if self.node == None:
    #         print('DOF_Group::setNodeVel: no associated Node.\n')
    #         return
    #     vel = self.unbalance       # ????
    #     vel = self.node.getTrialVel() # ????
    #     # get vel for my dof out of vector u
    #     for i in range(0, self.num_DOF):
    #         loc = self.myID[i]
    #         if loc >= 0:
    #             vel[i] = udot[loc]
    #     self.node.setTrialVel(vel)

    # def setNodeAccel(self, udotdot):
    #     if self.node == None:
    #         print('DOF_Group::setNodeAccel: no associated Node.\n')
    #         return
    #     accel = self.unbalance       # ????
    #     accel = self.node.getTrialAccel() # ????
    #     # get accel for my dof out of vector u
    #     for i in range(0, self.num_DOF):
    #         loc = self.myID[i]
    #         if loc >= 0:
    #             accel[i] = udotdot[loc]
    #     self.node.setTrialAccel(accel)
    
    def incr_node_disp(self, u):
        # u 是 Vector
        if self.node is None:
            print('DOF_Group::incrNodeDisp: 0 Node Pointer.\n')
        
        disp = self.unbalance
        # get disp for my dof out of vector u
        for i in range(0, self.num_DOF):
            loc = self.myID[i]
            if loc >= 0:
                disp[i] = u[loc]
            else:
                disp[i] = 0.0
        
        self.node.incr_trial_disp(disp)
    
    # def incrNodeVel(self, udot):
    #     pass
    # def incrNodeAccel(self, udotdot):
    #     pass

    # methods to set the eigen vectors
    # methods added for TransformationDOF_Groups
    # def getT(self):
    #     pass

    # protected:
    # def addLocalM_Force(self, udotdot, fact=1.0):
    #     pass
    
        
        
        
        


        
    