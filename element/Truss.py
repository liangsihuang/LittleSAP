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

    def __init__(self, tag, dim, nd1, nd2, material, A, r=0.0, damp=0, cm=0):
        super().__init__(tag)
        self.material = material
        
        self.connected_external_nodes = []  # 存储节点号
        self.connected_external_nodes.append(nd1)
        self.connected_external_nodes.append(nd2)

        self.dimension = dim   # truss in 2 or 3d domain
        self.num_DOF = 0        # number of dof for truss ??

        self.load = None    # pointer to the load vector P
        self.matrix = None  # pointer to objects matrix (a class wide Matrix)
        self.vector = None  # pointer to objects vector (a class wide Vector)

        self.L = 0.0       # length of truss based on undeformed configuration
        self.A = A         # area of truss
        self.rho = r       # rho: mass density per unit length

        self.do_rayleigh_damping = damp  # flag to include Rayleigh damping
        self.cMass = cm                # consistent mass flag

        self.cosX = [0, 0, 0]      # direction cosines
        self.nodes = [None, None] # 存储节点本身
        self.initial_disp = None     # narray
    
    # public methods to obtain information about dof and connectivity
    def get_num_external_nodes(self):
        return 2

    def get_external_nodes(self):
        return self.connected_external_nodes

    def get_nodes(self):
        return self.nodes

    def get_num_DOF(self):
        return self.num_DOF
        
    def set_domain(self, theDomain):
        # check Domain is not null - invoked when object removed from the a domain
        if theDomain is None:
            self.nodes = [None, None]
            self.L = 0
            return
        # first set the node pointers
        nd1 = self.connected_external_nodes[0]
        nd2 = self.connected_external_nodes[1]
        self.nodes[0] = theDomain.get_node(nd1)
        self.nodes[1] = theDomain.get_node(nd2)
        # if can't find both - send a warning message
        if self.nodes[0] is None or self.nodes[1] is None:
            if self.nodes[0] is None:
                print('Truss::setDomain() - truss '+ str(self.get_tag())+' node '+str(nd1)+' does not exist in the model.\n')
            else:
                print('Truss::setDomain() - truss '+ str(self.get_tag())+' node '+str(nd2)+' does not exist in the model.\n')
                # fill this in so don't segment fault later
                self.num_DOF = 2
                self.matrix = Truss.trussM2 # ????
                self.vector = Truss.trussV2
                return
        # now determine the number of dof and the dimension
        dofNd1 = self.nodes[0].get_number_DOF()
        dofNd2 = self.nodes[1].get_number_DOF()
        # if differing dof at the ends - print a warning message
        if dofNd1 != dofNd2:
            print('WARNING Truss::setDomain(): nodes '+str(nd1)+' and '+str(nd2)+'have differing dof at ends for truss '+str(self.get_tag())+'.\n')
            # fill this in so don't segment fault later
            self.num_DOF = 2
            self.matrix = Truss.trussM2
            self.vector = Truss.trussV2
            return
        # call the base class method
        super().set_domain(theDomain)
        # now set the number of dof for element and set matrix and vector pointer
        if self.dimension == 1 and dofNd1 == 1:
            self.num_DOF = 2
            self.matrix = Truss.trussM2 # ????
            self.vector = Truss.trussV2
        elif self.dimension == 2 and dofNd1 == 2:
            self.num_DOF = 4
            self.matrix = Truss.trussM4 # ????
            self.vector = Truss.trussV4
        elif self.dimension == 2 and dofNd1 == 3:
            self.num_DOF = 6
            self.matrix = Truss.trussM6 # ????
            self.vector = Truss.trussV6
        elif self.dimension == 3 and dofNd1 == 3:
            self.num_DOF = 6
            self.matrix = Truss.trussM6 # ????
            self.vector = Truss.trussV6
        elif self.dimension == 3 and dofNd1 == 6:
            self.num_DOF = 12
            self.matrix = Truss.trussM12 # ????
            self.vector = Truss.trussV12
        else:
            print('WARNING Truss::setDomain cannot handle '+str(self.dimension)+' dofs at nodes in '+str(dofNd1)+' problem.\n')
            self.num_DOF = 2
            self.matrix = Truss.trussM2 # ????
            self.vector = Truss.trussV2
            return
        # create the load vector
        if self.load is None:
            self.load = np.zeros(self.num_DOF)
        elif len(self.load) != self.num_DOF:
            self.load = np.zeros(self.num_DOF)
        # now determine the length, cosines and fill in the transformation
        # Note: t = -t(every one else uses for residual calc)
        end1Crd = self.nodes[0].get_crds() # 都是Vector
        end2Crd = self.nodes[1].get_crds()
        end1Disp = self.nodes[0].get_disp()
        end2Disp = self.nodes[1].get_disp()

        if self.dimension == 1:
            dx = end2Crd[0] - end1Crd[0]
            if self.initial_disp is None:
                iDisp = end2Disp[0] - end1Disp[0]
                if iDisp != 0:
                    self.initial_disp = np.zeros(1)
                    self.initial_disp[0] = iDisp
                    dx += iDisp
            self.L = sqrt(dx*dx)
            if self.L == 0.0:
                print('WARNING Truss::setDomain() - truss '+str(self.get_tag())+' has zero length.\n')
                return
            self.cosX[0] = 1.0
        elif self.dimension == 2:
            dx = end2Crd[0] - end1Crd[0]
            dy = end2Crd[1] - end1Crd[1]
            if self.initial_disp is None:
                iDispX = end2Disp[0] - end1Disp[0]
                iDispY = end2Disp[1] - end1Disp[1]
                if iDispX!=0 or iDispY!=0:
                    self.initial_disp = np.zeros(2)
                    self.initial_disp[0] = iDispX
                    self.initial_disp[1] = iDispY
                    dx += iDispX
                    dy += iDispY
            self.L = sqrt(dx*dx+dy*dy)
            if self.L == 0.0:
                print('WARNING Truss::setDomain() - truss '+str(self.get_tag())+' has zero length.\n')
                return
            self.cosX[0] = dx/self.L
            self.cosX[1] = dy/self.L
        else:
            dx = end2Crd[0] - end1Crd[0]
            dy = end2Crd[1] - end1Crd[1]
            dz = end2Crd[2] - end1Crd[2]
            if self.initial_disp is None:
                iDispX = end2Disp[0] - end1Disp[0]
                iDispY = end2Disp[1] - end1Disp[1]
                iDispZ = end2Disp[2] - end1Disp[2]
                if iDispX!=0 or iDispY!=0 or iDispZ!=0:
                    self.initial_disp = np.zeros(3)
                    self.initial_disp[0] = iDispX
                    self.initial_disp[1] = iDispY
                    self.initial_disp[2] = iDispZ
                    dx += iDispX
                    dy += iDispY
                    dz += iDispZ
            self.L = sqrt(dx*dx+dy*dy+dz*dz)
            if self.L == 0.0:
                print('WARNING Truss::setDomain() - truss '+str(self.get_tag())+' has zero length.\n')
                return
            self.cosX[0] = dx/self.L
            self.cosX[1] = dy/self.L
            self.cosX[2] = dz/self.L

        
    
    # public methods to set the state of the element
    def commit_state(self):
        if self. Kc is not None:
            self.Kc = self.get_tangent_stiff()
        retVal = self.material.commit_state()
        return retVal
    
    # def revertToLastCommit(self):
    #     return self.material.revertToLastCommit()
    # def revertToStart(self):
    #     pass
    def update(self):
        # determine the current strain given trial displacements at nodes
        strain = self.compute_current_strain()
        # rate = self.computeCurrentStrainRate()
        # return self.material.setTrialStrain(strain, rate)
        return self.material.set_trial_strain(strain)

    # public methods to obtain stiffness, mass, damping and residual information
    # def getKi(self):
    #     pass

    def get_tangent_stiff(self):
        if self.L == 0.0: # - problem in setDomain() no further warnings
            for i in self.matrix:
                i = 0.0
            return self.matrix
        E = self.material.get_tangent()
        # come back later and redo this if too slow
        stiff = self.matrix
        numDOF2 = int(self.num_DOF / 2)
        EAoverL = E * self.A / self.L
        for i in range(0, self.dimension):
            for j in range(0, self.dimension):
                temp = self.cosX[i] * self.cosX[j] * EAoverL
                stiff[i, j] = temp
                stiff[i+numDOF2, j] = -temp
                stiff[i, j+numDOF2] = -temp
                stiff[i+numDOF2, j+numDOF2] = temp
        return stiff

    def get_initial_stiff(self):
        if self.L == 0.0: # - problem in setDomain() no further warnings
            for i in self.matrix:
                i = 0.0
            return self.matrix
        E = self.material.get_initial_tangent()
        # come back later and redo this if too slow
        stiff = self.matrix
        numDOF2 = self.num_DOF / 2
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
    
    def zero_load(self):
        self.load[:] = 0.0

    def add_load(self, load, loadFactor): # Truss 单元没有分布力
        print('Truss::add_load - load type unknown for truss with tag: '+str(self.get_tag())+'.\n')
        return -1

    # def addInertiaLoadToUnbalance(self, accel):
    #     pass

    def get_resisting_force(self):
        if self.L == 0.0: # - problem in setDomain() no further warnings
            self.vector = None
            return self.vector
        
        # R = Ku - Pext
        # Ku = F * transformation
        force = self.A * self.material.get_stress()
        numDOF2 = int(self.num_DOF / 2)
        for i in range(0, self.dimension):
            temp = self.cosX[i] * force
            self.vector[i] = -temp
            self.vector[i+numDOF2] = temp
        return self.vector
        

    # def getResistingForceIncInertia(self):
    #         return super().getResistingForceIncInertia()
    

    # public methods for element output
    # private
    def compute_current_strain(self):
        # Note: method will not be called if L == 0
        # determine the strain
        disp1 = self.nodes[0].get_trial_disp() # Vector
        disp2 = self.nodes[1].get_trial_disp()
        dLength = 0.0
        if self.initial_disp is None:
            for i in range(0, self.dimension):
                dLength += (disp2[i] - disp1[i]) * self.cosX[i]
        else:
            for i in range(0, self.dimension):
                dLength += (disp2[i] - disp1[i] - self.initial_disp[i]) * self.cosX[i]

        # this method should never be called with L == 0
        return dLength/self.L

    
    # def computeCurrentStrainRate(self):
    #     # Note: method will not be called if L == 0
    #     # determine the strain
    #     vel1 = self.nodes[0].getTrialVel()
    #     vel2 = self.nodes[1].getTrialVel()
    #     dLength = 0.0
    #     for i in range(0, self.dimension):
    #         dLength += (vel2[i] - vel1[i]) * self.cosX[i]
    #     # this method should never be called with L == 0
    #     return dLength/self.L
