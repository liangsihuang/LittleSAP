from domain.DomainComponent import DomainComponent

import numpy as np

class Node(DomainComponent):

    def __init__(self, tag, ndof, *Crd):
        super().__init__()
        self.numberDOF = ndof          # number of dof at Node
        self.theDOF_Group = None    # pointer to associated DOF_Group

        self.Crd = []
        # Crd是可变参数，接收到的是一个 tuple
        for i in range(0,len(Crd)):
            self.Crd.append(Crd[i])
        
        self.commitDisp = None
        self.trialDisp = None

        self.unbalLoad = None       # unbalanced load
        self.incrDisp = None
        self.incrDeltaDisp = None
        # double arrays holding the disp, vel and accel value
        # 对应 np.narray
        self.disp = None

    # public methods dealing with the DOF at the node
    def getNumberDOF(self):
        return self.numberDOF
    def setDOF_Group(self, theDOF_Grp):
        self.theDOF_Group = theDOF_Grp
    def getDOF_Group(self):
        return self.theDOF_Group

    # public methods for obtaining the nodal coordinates
    def getCrds(self):
        return self.Crd

    # public methods for obtaining committed and trial response quantities of the node
    def getDisp(self):
        if self.commitDisp == None:
            self.createDisp()
        return self.commitDisp
    
    def getTrialDisp(self):
        if self.trialDisp == None:
            self.createDisp()
        return self.trialDisp

    # public methods for updating the trial response quantities
    def incrTrialDisp(self, incrDispl):
        # incrDispl 是 Vector
        # check vector arg is of correct size
        if incrDispl.Size() != self.numberDOF:
            print('WARNING Node::incrTrialDisp() - incompatable sizes.\n')
            return -2
        # create a copy if no trial exists andd add committed
        if self.trialDisp == None:
            if self.createDisp() < 0:
                print('FATAL Node::incrTrialDisp() - ran out of memory.\n')
            for i in range(0, self.numberDOF):
                incrDispI = incrDispl(i)
                self.disp[i] = incrDispI
                self.disp[i+2*self.numberDOF] = incrDispI
                self.disp[i+3*self.numberDOF] = incrDispI
            return 0
        # otherwise set trial = incr + trial
        for i in range(0, self.numberDOF):
            incrDispI = incrDispl(i)
            self.disp[i] += incrDispI
            self.disp[i+2*self.numberDOF] += incrDispI
            self.disp[i+3*self.numberDOF] = incrDispI
        return 0

    # public methods for adding and obtaining load information
    # def zeroUnbalancedLoad(self):
    #     if(self.unbalLoad!=[]):
    #         for i in range(0,len(self.unbalLoad)):
    #             self.unbalLoad[i] = 0.0

    # public methods dealing with the commited state of the node
    def commitState(self):
        # check disp exists, if does set commit = trial, incr = 0.0
        if self.trialDisp != None:
            for i in range(0, self.numberDOF):
                self.disp[i+self.numberDOF] = self.disp[i]
                self.disp[i+2*self.numberDOF] = 0.0
                self.disp[i+3*self.numberDOF] = 0.0
        # check vel exists, if does set commit = trial 
        # check accel exists, if does set commit = trial 
        return 0

    def revertToLastCommit(self):
        # check disp exists, if does set trial = last commit, incr = 0
        if(self.disp!=[]):
            for i in range(0,self.numberDOF):
                self.disp[i] = self.disp[i+self.numberDOF]
                self.disp[i+2*self.numberDOF] = 0.0
                self.disp[i+3*self.numberDOF] = 0.0
        # check vel exists, if does set trial = last commit
        # check accel exists, if does set trial = last commit

    # def revertToStart(self):
    #     # check disp exists, if does set all to zero
    #     if self.disp != None:
    #         for i in range(0, 4*self.numberDOF):
    #             self.disp[i] = 0.0
    #     # check vel exists, if does set all to zero
    #     # check accel exists, if does set all to zero

    #     if self.unbalLoad != None:
    #         for i in self.unbalLoad:
    #             i = 0.0
        
    #     return 0
    
    # public methods for dynamic analysis
    # public methods for eigen vector
    # public methods for output

# AddingSensitivity: BEGIN
# AddingSensitivity: END

    # private methods used to create the Vector objects 
    # for the committed and trial response quantities.
    def createDisp(self):
        # trial , committed, incr = (committed-trial)
        self.disp = np.zeros(4*self.numberDOF)
        # 按照储存顺序
        self.trialDisp = Vector(self.numberDOF, self.disp[0:self.numberDOF])
        self.commitDisp = Vector(self.numberDOF, self.disp[self.numberDOF:2*self.numberDOF])
        self.incrDisp = Vector(self.numberDOF, self.disp[2*self.numberDOF:3*self.numberDOF])
        self.incrDeltaDisp = Vector(self.numberDOF, self.disp[3*self.numberDOF:-1])
        return 0



    
        