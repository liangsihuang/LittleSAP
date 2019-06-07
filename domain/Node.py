from domain.DomainComponent import DomainComponent

import numpy as np

class Node(DomainComponent):

    def __init__(self, tag, ndof, *crd):
        super().__init__(tag)
        self.number_DOF = ndof          # number of dof at Node
        self.DOF_group = None    # pointer to associated DOF_Group

        self.crd = []
        # Crd是可变参数，接收到的是一个 tuple
        for i in range(0,len(crd)):
            self.crd.append(crd[i])
        
        self.commit_disp = None
        self.trial_disp = None

        self.unbal_load = None       # unbalanced load
        self.incr_disp = None
        self.incr_delta_disp = None
        # double arrays holding the disp, vel and accel value
        # 对应 np.narray
        self.disp = None

    # public methods dealing with the DOF at the node
    def get_number_DOF(self):
        return self.number_DOF

    def set_DOF_group(self, dof_grp):
        self.DOF_group = dof_grp

    def get_DOF_group(self):
        return self.DOF_group

    # public methods for obtaining the nodal coordinates
    def get_crds(self):
        return self.crd

    # public methods for obtaining committed and trial response quantities of the node
    def get_disp(self):
        if self.commit_disp is None:
            self.create_disp()
        return self.commit_disp
    
    def get_trial_disp(self):
        if self.trial_disp is None:
            self.create_disp()
        return self.trial_disp

    # public methods for updating the trial response quantities
    def incr_trial_disp(self, incrDispl):
        # incrDispl 是 Vector
        # check vector arg is of correct size
        if len(incrDispl) != self.number_DOF:
            print('WARNING Node::incr_trial_disp() - incompatable sizes.\n')
            return -2
        # create a copy if no trial exists andd add committed
        if self.trial_disp is None:
            self.create_disp()
            for i in range(0, self.number_DOF):
                incrDispI = incrDispl[i]
                self.disp[i] = incrDispI
                self.disp[i+2*self.number_DOF] = incrDispI
                self.disp[i+3*self.number_DOF] = incrDispI
            return 0
        # otherwise set trial = incr + trial
        for i in range(0, self.number_DOF):
            incrDispI = incrDispl[i]
            self.disp[i] += incrDispI
            self.disp[i+2*self.number_DOF] += incrDispI
            self.disp[i+3*self.number_DOF] = incrDispI
        return 0

    # public methods for adding and obtaining load information
    def add_unbalanced_load(self, add, fact=1.0):
        # add: narray
        # check vector arg is of correct size
        if len(add) != self.number_DOF:
            print('Node::add_unbal_Load - load to add of incorrect size')
            return -1
        # if no load yet create it and assign
        if self.unbal_load is None:
            self.unbal_load = add
            if fact != 1.0:
                self.unbal_load = self.unbal_load * fact
            return 0
        # add fact*add to the unbalanced load
        self.unbal_load = add * fact
        return 0

    def get_unbalanced_load(self):
        # make sure it was created before we return it
        if self.unbal_load is None:
            self.unbal_load = np.zeros(self.number_DOF)
        return self.unbal_load

    def zero_unbalanced_load(self):
        if self.unbal_load is not None:
            self.unbal_load[:] = 0.0

    # public methods dealing with the commited state of the node
    def commit_state(self):
        # check disp exists, if does set commit = trial, incr = 0.0
        if self.trial_disp is not None:
            for i in range(0, self.number_DOF):
                self.disp[i+self.number_DOF] = self.disp[i]
                self.disp[i+2*self.number_DOF] = 0.0
                self.disp[i+3*self.number_DOF] = 0.0
        # check vel exists, if does set commit = trial 
        # check accel exists, if does set commit = trial 
        return 0

    # def revertToLastCommit(self):
    #     # check disp exists, if does set trial = last commit, incr = 0
    #     if self.disp!=[]:
    #         for i in range(0,self.number_DOF):
    #             self.disp[i] = self.disp[i+self.number_DOF]
    #             self.disp[i+2*self.number_DOF] = 0.0
    #             self.disp[i+3*self.number_DOF] = 0.0
        # check vel exists, if does set trial = last commit
        # check accel exists, if does set trial = last commit

    # def revertToStart(self):
    #     # check disp exists, if does set all to zero
    #     if self.disp != None:
    #         for i in range(0, 4*self.number_DOF):
    #             self.disp[i] = 0.0
    #     # check vel exists, if does set all to zero
    #     # check accel exists, if does set all to zero

    #     if self.unbal_load != None:
    #         for i in self.unbal_load:
    #             i = 0.0
        
    #     return 0
    
    # public methods for dynamic analysis
    # public methods for eigen vector
    # public methods for output

# AddingSensitivity: BEGIN
# AddingSensitivity: END

    # private methods used to create the Vector objects 
    # for the committed and trial response quantities.
    def create_disp(self):
        # trial , committed, incr = (committed-trial)
        self.disp = np.zeros(4*self.number_DOF)
        # 按照储存顺序
        self.trial_disp = self.disp[0:self.number_DOF]
        self.commit_disp = self.disp[self.number_DOF:2*self.number_DOF]
        self.incr_disp = self.disp[2*self.number_DOF:3*self.number_DOF]
        self.incr_delta_disp = self.disp[3*self.number_DOF:-1]



    
        