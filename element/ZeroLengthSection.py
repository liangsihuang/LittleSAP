from element.Element import Element
import numpy as np
from copy import deepcopy
from material.section.SectionForceDeformation import SECTION_RESPONSE_MZ,\
SECTION_RESPONSE_P,SECTION_RESPONSE_VY,SECTION_RESPONSE_MY,SECTION_RESPONSE_VZ,SECTION_RESPONSE_T
# A ZeroLengthSection element is defined by two nodes with the same coordinate.
# A SectionForceDeformation object is associated with the nodes to
# provide the basic force-deformation relationship for the element.

class ZeroLengthSection(Element):
    # Class wide matrices for return
    K6 = np.zeros((6,6))
    K12 = np.zeros((12,12))
    # Class wide vectors for return
    P6 = np.zeros(6)
    P12 = np.zeros(12)

    def __init__(self, tag, dimension, Nd1, Nd2, section, x=None, yprime=None, doRayleighDamping=0):
        super().__init__(tag)
        # 默认局部坐标和整体坐标相同
        if x is None:
            x = [1.0, 0.0, 0.0]
        if yprime is None:
            yprime = [0.0, 1.0, 0.0]

        self.connected_external_nodes = np.zeros(2, dtype=int)
        self.nodes = []
        self.dimension = dimension
        self.num_DOF = 0
        self.transformation = np.zeros((3,3))
        self.use_rayleigh_damping = doRayleighDamping # int， 0：not including rayleigh damping

        self.A = None # Transformation matrix ... e = A*(u2-u1)
        self.v = None # Section deformation vector, the element basic deformations
        self.K = None # Pointer to element stiffness matrix
        self.P = None # Pointer to element force vector

        self.section = deepcopy(section) # SectionForceDeformation object
        self.order = section.get_order() # Order of the section model

        # Set up the transformation matrix of direction cosines
        self.set_up(Nd1, Nd2, x, yprime)


    def get_num_external_nodes(self):
        return 2

    def get_external_nodes(self):
        return self.connected_external_nodes

    def get_nodes(self):
        return self.nodes

    def get_num_DOF(self):
        return self.num_DOF

    def set_domain(self, theDomain):
        if theDomain is None:
            self.nodes[0] = None
            self.nodes[1] = None
            return
        Nd1 = self.connected_external_nodes[0]
        Nd2 = self.connected_external_nodes[1]
        self.nodes[0] = theDomain.getNode(Nd1)
        self.nodes[1] = theDomain.getNode(Nd2)
        # check
        if self.nodes[0] is None or self.nodes[1] is None:
            if self.nodes[0] is None:
                print('ZeroLengthSection::set_domain() -- Nd1:' +str(Nd1)+
                      ' does not exist in ')
            else:
                print('ZeroLengthSection::set_domain() -- Nd2:' +str(Nd2)+
                      ' does not exist in ')
            print('model for ZeroLengthSection with id '+str(self.getTag()))
            return
        # now determine the number of dof and the dimension
        dofNd1 = self.nodes[0].get_number_DOF()
        dofNd2 = self.nodes[1].get_number_DOF()
        if dofNd1!=dofNd2:
            print('ZeroLengthSection::set_domain() -- nodes '+str(Nd1)+' and '+str(Nd2)+
                  'have differing dof at ends for ZeroLengthSection '+str(self.getTag()))
            return
        self.num_DOF = 2 * dofNd1
        if self.num_DOF!=6 and self.num_DOF!=12:
            print('ZeroLengthSection::set_domain() -- element only works for 3 (2d) or 6 (3d) dof per node')

        if self.num_DOF==6:
            self.P = ZeroLengthSection.P6
            self.K = ZeroLengthSection.K6
        else:
            self.P = ZeroLengthSection.P12
            self.K = ZeroLengthSection.K12

        # Check that length is zero within tolerance
        end1Crd = self.nodes[0].getCrds()
        end2Crd = self.nodes[1].getCrds()
        diff = end1Crd - end2Crd
        L = np.linalg.norm(diff)
        v1 = np.linalg.norm(end1Crd)
        v2 = np.linalg.norm(end2Crd)

        if v1<v2:
            vm = v2
        else:
            vm = v1

        LENTOL = 1.0e-6
        if L > LENTOL*vm:
            print('ZeroLengthSection::set_domain() -- Element '+str(self.get_tag())
                  + 'has L= '+ str(L)+', which is greater than the tolerance')
        self.set_domain(theDomain)
        # Set up the A matrix
        self.set_transformation()



    # private method
    # Establish the external nodes and set up the transformation matrix for orientation
    def set_up(self, Nd1, Nd2, x, yp):
        # x: vector in global coordinates defining local x-axis
        # yp: vector in global coordinates defining
        # vector yp which lies in the local x-y plane for the element.
        # ensure the connectedExternalNode ID is of correct size & set values
        if len(self.connected_external_nodes) != 2:
            print('ZeroLengthSection::set_up -- failed to create an ID of correct size\n')

        self.connected_external_nodes[0] = Nd1
        self.connected_external_nodes[1] = Nd2

        # check that vectors for orientation are correct size
        if len(x)!=3 or len(yp)!= 3:
            print('ZeroLengthSection::set_up -- incorrect dimension of orientation vectors\n')

        # establish orientation of element for the tranformation matrix
        # z = x cross yp
        z = np.zeros(3)
        z[0] = x[1]*yp[2] - x[2]*yp[1]
        z[1] = x[2]*yp[0] - x[0]*yp[2]
        z[2] = x[0]*yp[1] - x[1]*yp[0]
        # y = z cross x
        # y 不是等于 y'吗？为什么要区分？要再算一次？
        y = np.zeros(3)
        y[0] = z[1] * x[2] - z[2] * x[1]
        y[1] = z[2] * x[0] - z[0] * x[2]
        y[2] = z[0] * x[1] - z[1] * x[0]

        # compute length(norm) of vectors
        xn = np.linalg.norm(x)
        yn = np.linalg.norm(y)
        zn = np.linalg.norm(z)

        # check valid x and y vectors, i.e. not parallel and of zero length
        if xn==0 or yn==0 or zn ==0:
            print('ZeroLengthSection::set_up -- invalid vectors to constructor\n')

        # create transformation matrix of direction cosines
        for i in range(0,3):
            self.transformation[0,i] = x[i] / xn
            self.transformation[1,i] = y[i] / yn
            self.transformation[2,i] = z[i] / zn

    # Set basic deformation-displacement transformation matrix for section
    def set_transformation(self):
        # transformation matrix
        self.A = np.zeros((self.order, self.num_DOF))
        # section deformation vector
        self.v = np.zeros(self.order)
        # Get the section code
        code = self.section.get_type()
        # Loop over the section code
        for i in range(0, self.order):
            # Fill in row i of A based on section code
            # The in-plane transformations
            if code[i] == SECTION_RESPONSE_MZ:
                if self.num_DOF == 6:
                    self.A[i, 3] = 0.0
                    self.A[i, 4] = 0.0
                    self.A[i, 5] = self.transformation[2, 2]
                elif self.num_DOF == 12:
                    self.A[i, 9] = self.transformation[2, 0]
                    self.A[i, 10] = self.transformation[2, 1]
                    self.A[i, 11] = self.transformation[2, 2]
            elif code[i] == SECTION_RESPONSE_P:
                if self.num_DOF == 6:
                    self.A[i, 3] = self.transformation[0, 0]
                    self.A[i, 4] = self.transformation[0, 1]
                    self.A[i, 5] = 0.0
                elif self.num_DOF == 12:
                    pass
            elif code[i] == SECTION_RESPONSE_VY:
                if self.num_DOF == 6:
                    self.A[i, 3] = self.transformation[1, 0]
                    self.A[i, 4] = self.transformation[1, 1]
                    self.A[i, 5] = 0.0
                elif self.num_DOF == 12:
                    pass
            #     The out-of-plane transformations
            elif code[i] == SECTION_RESPONSE_MY:
                if self.num_DOF == 12:
                    self.A[i, 6] = self.transformation[2, 0]
                    self.A[i, 7] = self.transformation[2, 1]
                    self.A[i, 8] = self.transformation[2, 2]
            elif code[i] == SECTION_RESPONSE_VZ:
                pass
            elif code[i] == SECTION_RESPONSE_T:
                pass
            # Fill in first half of transformation matrix with negative sign
            for j in range(0, int(self.num_DOF/2)):
                self.A[i, j] = - self.A[i, j+self.num_DOF/2]
