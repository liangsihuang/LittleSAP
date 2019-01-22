from element.Element import Element
from math import sqrt
import numpy as np

class Truss(Element):

    trussM2 = np.zeros((2, 2))
    trussM4 = np.zeros((4, 4))
    trussM6 = np.zeros((6, 6))
    trussM12 = np.zeros((12, 12))
    trussV2 = np.zeros(2)
    trussV4 = np.zeros(4)
    trussV6 = np.zeros(6)
    trussV12 = np.zeros(12)

    def __init__(self, tag, dim, nd1, nd2, theMaterial, A, r=0.0, damp=0, cm=0):
        super().__init__(tag)
        self.theMaterial = theMaterial
        
        self.connectedExternalNodes = []  # 存储节点号
        self.connectedExternalNodes.append(nd1)
        self.connectedExternalNodes.append(nd2)

        self.dimension = dim   # truss in 2 or 3d domain
        self.numDOF = 0        # number of dof for truss ??

        self.theLoad = None    # pointer to the load vector P
        self.theMatrix = None  # pointer to objects matrix (a class wide Matrix)
        self.theVector = None  # pointer to objects vector (a class wide Vector)

        self.L = 0.0       # length of truss based on undeformed configuration
        self.A = A         # area of truss
        self.rho = r       # rho: mass density per unit length

        self.doRayleighDamping = damp  # flag to include Rayleigh damping
        self.cMass = cm                # consistent mass flag

        self.cosX = [0, 0, 0]      # direction cosines
        self.theNodes = [None, None] # 存储节点本身
        self.initialDisp = None     # narray
    
    # public methods to obtain information about dof and connectivity
    def getNumExternalNodes(self):
        return 2
    def getExternalNodes(self):
        return self.connectedExternalNodes
    def getNode(self):
        return self.theNodes
    def getNumDOF(self):
        return self.numDOF
        
    def setDomain(self, theDomain):
        # check Domain is not null - invoked when object removed from the a domain
        if theDomain is None:
            self.theNodes = [None, None]
            self.L = 0
            return
        # first set the node pointers
        nd1 = self.connectedExternalNodes[0]
        nd2 = self.connectedExternalNodes[1]
        self.theNodes[0] = theDomain.getNode(nd1)
        self.theNodes[1] = theDomain.getNode(nd2)
        # if can't find both - send a warning message
        if self.theNodes[0] is None or self.theNodes[1] is None:
            if self.theNodes[0] is None:
                print('Truss::setDomain() - truss '+ str(self.getTag())+' node '+str(nd1)+' does not exist in the model.\n')
            else:
                print('Truss::setDomain() - truss '+ str(self.getTag())+' node '+str(nd2)+' does not exist in the model.\n')
                # fill this in so don't segment fault later
                self.numDOF = 2
                self.theMatrix = Truss.trussM2 # ????
                self.theVector = Truss.trussV2
                return
        # now determine the number of dof and the dimension
        dofNd1 = self.theNodes[0].getNumberDOF()
        dofNd2 = self.theNodes[1].getNumberDOF()
        # if differing dof at the ends - print a warning message
        if dofNd1 != dofNd2:
            print('WARNING Truss::setDomain(): nodes '+str(nd1)+' and '+str(nd2)+'have differing dof at ends for truss '+str(self.getTag())+'.\n')
            # fill this in so don't segment fault later
            self.numDOF = 2
            self.theMatrix = Truss.trussM2
            self.theVector = Truss.trussV2
            return
        # call the base class method
        super().setDomain(theDomain)
        # now set the number of dof for element and set matrix and vector pointer
        if self.dimension == 1 and dofNd1 == 1:
            self.numDOF = 2
            self.theMatrix = Truss.trussM2 # ????
            self.theVector = Truss.trussV2
        elif self.dimension == 2 and dofNd1 == 2:
            self.numDOF = 4
            self.theMatrix = Truss.trussM4 # ????
            self.theVector = Truss.trussV4
        elif self.dimension == 2 and dofNd1 == 3:
            self.numDOF = 6
            self.theMatrix = Truss.trussM6 # ????
            self.theVector = Truss.trussV6
        elif self.dimension == 3 and dofNd1 == 3:
            self.numDOF = 6
            self.theMatrix = Truss.trussM6 # ????
            self.theVector = Truss.trussV6
        elif self.dimension == 3 and dofNd1 == 6:
            self.numDOF = 12
            self.theMatrix = Truss.trussM12 # ????
            self.theVector = Truss.trussV12
        else:
            print('WARNING Truss::setDomain cannot handle '+str(self.dimension)+' dofs at nodes in '+str(dofNd1)+' problem.\n')
            self.numDOF = 2
            self.theMatrix = Truss.trussM2 # ????
            self.theVector = Truss.trussV2
            return
        # create the load vector
        if self.theLoad is None:
            self.theLoad = np.zeros(self.numDOF)
        elif len(self.theLoad) != self.numDOF:
            self.theLoad = np.zeros(self.numDOF)
        # now determine the length, cosines and fill in the transformation
        # Note: t = -t(every one else uses for residual calc)
        end1Crd = self.theNodes[0].getCrds() # 都是Vector
        end2Crd = self.theNodes[1].getCrds()
        end1Disp = self.theNodes[0].getDisp()
        end2Disp = self.theNodes[1].getDisp()

        if self.dimension == 1:
            dx = end2Crd[0] - end1Crd[0]
            if self.initialDisp is None:
                iDisp = end2Disp[0] - end1Disp[0]
                if iDisp != 0:
                    self.initialDisp = np.zeros(1)
                    self.initialDisp[0] = iDisp
                    dx += iDisp
            self.L = sqrt(dx*dx)
            if self.L == 0.0:
                print('WARNING Truss::setDomain() - truss '+str(self.getTag())+' has zero length.\n')
                return
            self.cosX[0] = 1.0
        elif self.dimension == 2:
            dx = end2Crd[0] - end1Crd[0]
            dy = end2Crd[1] - end1Crd[1]
            if self.initialDisp is None:
                iDispX = end2Disp[0] - end1Disp[0]
                iDispY = end2Disp[1] - end1Disp[1]
                if iDispX!=0 or iDispY!=0:
                    self.initialDisp = np.zeros(2)
                    self.initialDisp[0] = iDispX
                    self.initialDisp[1] = iDispY
                    dx += iDispX
                    dy += iDispY
            self.L = sqrt(dx*dx+dy*dy)
            if self.L == 0.0:
                print('WARNING Truss::setDomain() - truss '+str(self.getTag())+' has zero length.\n')
                return
            self.cosX[0] = dx/self.L
            self.cosX[1] = dy/self.L
        else:
            dx = end2Crd[0] - end1Crd[0]
            dy = end2Crd[1] - end1Crd[1]
            dz = end2Crd[2] - end1Crd[2]
            if self.initialDisp is None:
                iDispX = end2Disp[0] - end1Disp[0]
                iDispY = end2Disp[1] - end1Disp[1]
                iDispZ = end2Disp[2] - end1Disp[2]
                if iDispX!=0 or iDispY!=0 or iDispZ!=0:
                    self.initialDisp = np.zeros(3)
                    self.initialDisp[0] = iDispX
                    self.initialDisp[1] = iDispY
                    self.initialDisp[2] = iDispZ
                    dx += iDispX
                    dy += iDispY
                    dz += iDispZ
            self.L = sqrt(dx*dx+dy*dy+dz*dz)
            if self.L == 0.0:
                print('WARNING Truss::setDomain() - truss '+str(self.getTag())+' has zero length.\n')
                return
            self.cosX[0] = dx/self.L
            self.cosX[1] = dy/self.L
            self.cosX[2] = dz/self.L

        
    
    # public methods to set the state of the element
    def commitState(self):
        if self. Kc is not None:
            self.Kc = self.getTangentStiff()
        retVal = self.theMaterial.commitState()
        return retVal
    
    # def revertToLastCommit(self):
    #     return self.theMaterial.revertToLastCommit()
    # def revertToStart(self):
    #     pass
    def update(self):
        # determine the current strain given trial displacements at nodes
        strain = self.computeCurrentStrain()
        # rate = self.computeCurrentStrainRate()
        # return self.theMaterial.setTrialStrain(strain, rate)
        return self.theMaterial.setTrialStrain(strain)

    # public methods to obtain stiffness, mass, damping and residual information
    # def getKi(self):
    #     pass

    def getTangentStiff(self):
        if self.L == 0.0: # - problem in setDomain() no further warnings
            self.theMatrix.Zero()
            return self.theMatrix
        E = self.theMaterial.getTangent()
        # come back later and redo this if too slow
        stiff = self.theMatrix
        numDOF2 = int(self.numDOF / 2)
        EAoverL = E * self.A / self.L
        for i in range(0, self.dimension):
            for j in range(0, self.dimension):
                temp = self.cosX[i] * self.cosX[j] * EAoverL
                stiff[i, j] = temp
                stiff[i+numDOF2, j] = -temp
                stiff[i, j+numDOF2] = -temp
                stiff[i+numDOF2, j+numDOF2] = temp
        return stiff

    def getInitialStiff(self):
        if self.L == 0.0: # - problem in setDomain() no further warnings
            self.theMatrix.Zero()
            return self.theMatrix
        E = self.theMaterial.getInitialTangent()  
        # come back later and redo this if too slow
        stiff = self.theMatrix
        numDOF2 = self.numDOF / 2
        EAoverL = E * self.A / self.L
        for i in range(0, self.dimension):
            for j in range(0, self.dimension):
                temp = self.cosX[i] * self.cosX[j] * EAoverL
                stiff[i, j] = temp
                stiff[i+numDOF2, j] = -temp
                stiff[i, j+numDOF2] = -temp
                stiff[i+numDOF2, j+numDOF2] = temp
        return stiff

    # def getDamp(self):
    #     pass
    # def getMass(self):
    #     pass
    
    def zeroLoad(self):
        self.theLoad[:] = 0.0

    def addLoad(self, theLoad, loadFactor): # Truss 单元没有分布力
        print('Truss::addLoad - load type unknown for truss with tag: '+str(self.getTag())+'.\n')
        return -1

    # def addInertiaLoadToUnbalance(self, accel):
    #     pass

    def getResistingForce(self):
        if self.L == 0.0: # - problem in setDomain() no further warnings
            self.theVector = None
            return self.theVector
        
        # R = Ku - Pext
        # Ku = F * transformation
        force = self.A * self.theMaterial.getStress()
        numDOF2 = int(self.numDOF / 2)
        for i in range(0, self.dimension):
            temp = self.cosX[i] * force
            self.theVector[i] = -temp
            self.theVector[i+numDOF2] = temp
        return self.theVector 
        

    # def getResistingForceIncInertia(self):
    #         return super().getResistingForceIncInertia()
    

    # public methods for element output
    # private
    def computeCurrentStrain(self):
        # Note: method will not be called if L == 0
        # determine the strain
        disp1 = self.theNodes[0].getTrialDisp() # Vector
        disp2 = self.theNodes[1].getTrialDisp()
        dLength = 0.0
        if self.initialDisp is None:
            for i in range(0, self.dimension):
                dLength += (disp2[i] - disp1[i]) * self.cosX[i]
        else:
            for i in range(0, self.dimension):
                dLength += (disp2[i] - disp1[i] - self.initialDisp[i]) * self.cosX[i]

        # this method should never be called with L == 0
        return dLength/self.L

    
    # def computeCurrentStrainRate(self):
    #     # Note: method will not be called if L == 0
    #     # determine the strain
    #     vel1 = self.theNodes[0].getTrialVel()
    #     vel2 = self.theNodes[1].getTrialVel()
    #     dLength = 0.0
    #     for i in range(0, self.dimension):
    #         dLength += (vel2[i] - vel1[i]) * self.cosX[i]
    #     # this method should never be called with L == 0
    #     return dLength/self.L
