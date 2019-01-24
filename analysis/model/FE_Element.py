from TaggedObject import TaggedObject
import numpy as np

MAX_NUM_DOF = 64

class FE_Element(TaggedObject):
    # static variables - single copy for all objects of the class	
    errMatrix = None # matrix
    errVector = None # vector
    theMatrices = None # array of pointers to 'class wide matrices'/ rank-2 narray
    theVectors = None # array of pointers to 'class wide vectors'/ narray
    numFEs = 0  # number of objects

    def __init__(self, tag, ele):
        super().__init__(tag)
        self.myDOF_Groups = np.zeros(len(ele.getExternalNodes()), dtype=int)
        self.myID = np.zeros(ele.getNumDOF(), dtype=int)
        self.numDOF = ele.getNumDOF()
        self.theModel = None
        self.myEle = ele
        self.theResidual = None # vector
        self.theTangent = None # matrix
        self.theIntegrator = None # needed for subdomain???

        if self.numDOF <= 0:
            print('FE_Element::FE_Element() - element must have 1 dof')
        
        # get element domain and check if it is valid
        theDomain = ele.getDomain()
        if theDomain is None:
            print('FE_Element::FE_Element() - element has no domain')
        # keep a pointer to all DOF_Groups
        numGroup = ele.getNumExternalNodes() # int
        nodes = ele.getExternalNodes()  # int's list
        for i in range(0, numGroup):
            node = theDomain.getNode(nodes[i])
            if node is None:
                print('FATAL FE_Element::FE_Element() - Node: '+str(nodes[i]))
                print('does not exist in the Domain\n')
            dofGrp = node.getDOF_Group()
            if dofGrp is not None:
                self.myDOF_Groups[i] = dofGrp.getTag()
            else:
                print('FATAL FE_Element::FE_Element() - Node: ')
                print('has no DOF_Group associated with it\n')

        # if this is the first FE_Element we now
        # create the arrays used to store pointers to class wide
        # matrix and vector objects used to return tangent and residual
        if FE_Element.numFEs == 0:
            FE_Element.theMatrices = []
            FE_Element.theVectors = []
        for i in range(0, MAX_NUM_DOF+1):
            FE_Element.theMatrices.append(None)
            FE_Element.theVectors.append(None)
        # if Elements are not subdomains, set up pointers to
        # objects to return tangent Matrix and residual Vector.
        if self.numDOF <= MAX_NUM_DOF:
            # use class wide objects
            if FE_Element.theVectors[self.numDOF] is None:
                FE_Element.theVectors[self.numDOF] = np.zeros(self.numDOF)
                FE_Element.theMatrices[self.numDOF] = np.zeros((self.numDOF,self.numDOF))
                self.theResidual = FE_Element.theVectors[self.numDOF]
                self.theTangent = FE_Element.theMatrices[self.numDOF]
            else:
                self.theResidual = FE_Element.theVectors[self.numDOF]
                self.theTangent = FE_Element.theMatrices[self.numDOF]
        else:
            # create matrices and vectors for each object instance
            self.theResidual = np.zeros(self.numDOF)
            self.theTangent = np.zeros((self.numDOF, self.numDOF))

        FE_Element.numFEs += 1

    # public methods for setting/obtaining mapping information
    def getDOFtags(self):
        return self.myDOF_Groups

    def getID(self):
        return self.myID

    def setAnalysisModel(self, theAnalysisModel):
        self.theModel = theAnalysisModel

    def setID(self):
        current = 0
        if self.theModel is None:
            print('WARNING FE_Element::setID() - no AnalysisModel set.\n')
            return -1
        numGrps = len(self.myDOF_Groups)
        for i in range(0, numGrps):
            tag = self.myDOF_Groups[i]
            dof = self.theModel.getDOF_Group(tag)
            if dof is None:
                print('WARNING FE_Element::setID: 0 DOF_Group Pointer.\n')
                return -2
            theDOFid = dof.getID()
            for j in range(0, len(theDOFid)):
                if current < self.numDOF:
                    self.myID[current] = theDOFid[j]
                    current += 1
                else:
                    print('WARNING FE_Element::setID() - numDOF and number of dof at the DOF_Groups.\n')
                    return -3
        return 0
    
    # methods to form and obtain the tangent and residual
    def getTangent(self, theNewIntegrator):
        self.theIntegrator = theNewIntegrator
        if self.myEle is None:
            print('FATAL FE_Element::getTangent() - no Element *given.\n')

        if theNewIntegrator is not None:
            theNewIntegrator.formEleTangent(self)
            return self.theTangent


    def getResidual(self, theNewIntegrator):
        self.theIntegrator = theNewIntegrator
        if self.theIntegrator is None:
            return self.theResidual
        if self.myEle is None:
            print('FATAL FE_Element::getTangent() - no Element *given.\n')
        theNewIntegrator.formEleResidual(self)
        return self.theResidual

    
    # methods to allow integrator to build tangent
    def zeroTangent(self):
        if self.myEle is not None:
            self.theTangent[:, :] = 0.0

    def addKtToTang(self, fact=1.0):
        if self.myEle is not None:
            # check for a quick return	
            if fact == 0.0:
                return 
            else:
                self.theTangent += self.myEle.getTangentStiff() * fact

    def addKiToTang(self, fact=1.0):
        if self.myEle is not None:
            # check for a quick return 
            if fact == 0.0:
                return 
            else:
                self.theTangent += self.myEle.getInitialStiff() * fact

    def addKgToTang(self, fact=1.0):
        if self.myEle is not None:
            # check for a quick return 
            if fact == 0.0:
                return 
            else:
                self.theTangent += self.myEle.getGeometricTangentStiff() * fact

    # def addCtoTang(self, fact=1.0):
    #     pass
    # def addMtoTang(self, fact=1.0):
    #     pass

    def addKpToTang(self, fact=1.0, numP=0):
        if self.myEle is not None:
            # check for a quick return 
            if fact == 0.0:
                return 
            else:
                thePrevMat = self.myEle.getPreviousK(numP)
                if thePrevMat is not None:
                    self.theTangent += thePrevMat * fact

    def storePreviousK(self, numP):
        res = None
        if self.myEle is not None:
            res = self.myEle.storePreviousK(numP)
        return res
    
    # methods to allow integrator to build residual
    def zeroResidual(self):
        if self.myEle is not None:
                self.theResidual[:] = 0.0
        else:
            print('FATAL FE_Element::zeroResidual() - no Element *given.\n')

    def addRtoResidual(self, fact=1.0):
        if self.myEle is not None:
            # check for a quick return 
            if fact == 0.0:
                return 
            eleResisting = self.myEle.getResistingForce()
            self.theResidual += (eleResisting * -1.0)
        else:
            print('FATAL FE_Element::addRtoResidual() - no Element *given.\n')


    # def addRIncInertiaToResidual(self, fact=1.0):
    #     pass
    
    # methods for ele-by-ele strategies
    def getTangForce(self, disp, fact=1.0):
        if self.myEle is not None:
            # zero out the force vector
            self.theResidual[:] = 0.0
            # check for a quick return
            if fact == 0.0:
                return self.theResidual
            # get the component we need out of the vector and place in a temporary vector
            tmp = np.zeros(self.numDOF)
            for i in range(0, self.numDOF):
                dof = self.myID[i]
                if dof >= 0:
                    tmp[i] = disp[dof]
                else:
                    tmp[i] = 0.0
            # form the tangent again and then add the force
            self.theIntegrator.formEleTangent(self)
            self.theResidual += self.theTangent @ tmp * fact
            return self.theResidual
        else:
            print('WARNING FE_Element::addTangForce() - no Element *given.\n')
            return FE_Element.errVector

    def getK_Force(self, disp, fact=1.0):
        if self.myEle is not None:
            self.theResidual[:] = 0.0
            if fact == 0.0:
                return self.theResidual
            tmp = np.zeros(self.numDOF)
            for i in range(0, self.numDOF):
                dof = self.myID[i]
                if dof >= 0:
                    tmp[i] = disp[dof]
                else:
                    tmp[i] = 0.0
            self.theResidual += self.myEle.getTangentStiff() @ tmp * fact
            return self.theResidual
        else:
            print('WARNING FE_Element::getKForce() - no Element *given.\n')
            return FE_Element.errVector

    def getKi_Force(self, disp, fact=1.0):
        if self.myEle is not None:
            self.theResidual[:] = 0.0
            if fact == 0.0:
                return self.theResidual
            tmp = np.zeros(self.numDOF)
            for i in range(0, self.numDOF):
                dof = self.myID[i]
                if dof >= 0:
                    tmp[i] = disp[dof]
                else:
                    tmp[i] = 0.0
            self.theResidual += self.myEle.getInitialStiff() @ tmp * fact
            return self.theResidual
        else:
            print('WARNING FE_Element::getKForce() - no Element *given.\n')
            return FE_Element.errVector



    # def getC_Force(self, x, fact=1.0):
    #     pass
    # def getM_Force(self, x, fact=1.0):
    #     pass
    #
    # def addM_Force(self, accel, fact=1.0):
    #     pass
    # def addD_Force(self, vel, fact=1.0):
    #     pass

    def addK_Force(self, disp, fact=1.0):
        if self.myEle is not None:
            if fact == 0.0:
                return
            tmp = np.zeros(self.numDOF)
            for i in range(0, self.numDOF):
                loc = self.myID[i]
                if loc >= 0:
                    tmp[i] = disp[loc]
                else:
                    tmp[i] = 0.0
            self.theResidual += self.myEle.getTangentStiff() @ tmp * fact
        else:
            print('WARNING FE_Element::addK_Force() - no Element *given.\n')

    def addKg_Force(self, disp, fact=1.0):
        if self.myEle is not None:
            if fact == 0.0:
                return
            tmp = np.zeros(self.numDOF)
            for i in range(0, self.numDOF):
                loc = self.myID[i]
                if loc >= 0:
                    tmp[i] = disp[loc]
                else:
                    tmp[i] = 0.0
            self.theResidual += self.myEle.getGeometricTangentStiff() @ tmp * fact
        else:
            print('WARNING FE_Element::addKg_Force() - no Element *given.\n')
    
    def updateElement(self):
        if self.myEle is not None:
            return self.myEle.update()
        # else: =None 不用 print 吗？
        return 0

    def getLastIntegrator(self):
        return self.theIntegrator

    def getLastResponse(self):
        if self.myEle is not None:
            if self.theIntegrator is not None:
                if self.theIntegrator.getLastResponse(self.theResidual, self.myID) < 0:
                    print('WARNING FE_Element::getLastResponse(void) - the Integrator had problems with getLastResponse().\n')
            else:
                self.theResidual[:] = 0.0
                print('WARNING  FE_Element::getLastResponse() - No Integrator yet passed.\n')
            return self.theResidual
        else:
            print('WARNING  FE_Element::getLastResponse() - No Element passed in constructor.\n')
            return FE_Element.errVector

    def getElement(self):
        return self.myEle
    
    # protected:
    # def addLocalM_Force(self, accel, fact=1.0):
    #     pass
    # def addLocalD_Force(self, vel, fact=1.0):
    #     pass
        

    