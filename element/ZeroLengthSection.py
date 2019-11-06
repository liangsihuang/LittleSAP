from element.Element import Element
import numpy as np
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

    def __init__(self, tag, dimension, Nd1, Nd2, theSection, x=None, yprime=None, doRayleighDamping=0):
        super().__init__(tag)
        # 默认局部坐标和整体坐标相同
        if x is None:
            x = [1.0, 0.0, 0.0]
        if yprime is None:
            yprime = [0.0, 1.0, 0.0]

        self.connectedExternalNodes = np.zeros(2, dtype=int)
        self.theNodes = []
        self.dimension = dimension
        self.numDOF = 0
        self.transformation = np.zeros((3,3))
        self.useRayleighDamping = doRayleighDamping # int， 0：not including rayleigh damping

        self.A = None # Transformation matrix ... e = A*(u2-u1)
        self.v = None # Section deformation vector, the element basic deformations
        self.K = None # Pointer to element stiffness matrix
        self.P = None # Pointer to element force vector

        self.theSection = theSection.getCopy() # SectionForceDeformation object
        self.order = theSection.getOrder() # Order of the section model

        # Set up the transformation matrix of direction cosines
        self.setUp(Nd1, Nd2, x, yprime)

    def setUp(self, Nd1, Nd2, x, yp):
        # x: vector in global coordinates defining local x-axis
        # yp: vector in global coordinates defining
        # vector yp which lies in the local x-y plane for the element.
        # ensure the connectedExternalNode ID is of correct size & set values
        if len(self.connectedExternalNodes) != 2:
            print('ZeroLengthSection::setUp -- failed to create an ID of correct size\n')

        self.connectedExternalNodes[0] = Nd1
        self.connectedExternalNodes[1] = Nd2

        # check that vectors for orientation are correct size
        if len(x)!=3 or len(yp)!= 3:
            print('ZeroLengthSection::setUp -- incorrect dimension of orientation vectors\n')

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
            print('ZeroLengthSection::setUp -- invalid vectors to constructor\n')

        # create transformation matrix of direction cosines
        for i in range(0,3):
            self.transformation[0,i] = x[i] / xn
            self.transformation[1,i] = y[i] / yn
            self.transformation[2,i] = z[i] / zn

    def getNumExternalNodes(self):
        return 2

    def getExternalNodes(self):
        return self.connectedExternalNodes

    def getNodes(self):
        return self.theNodes

    def getNumDOF(self):
        return self.numDOF

    def setDomain(self, theDomain):
        if theDomain is None:
            self.theNodes[0] = None
            self.theNodes[1] = None
            return
        Nd1 = self.connectedExternalNodes[0]
        Nd2 = self.connectedExternalNodes[1]
        self.theNodes[0] = theDomain.getNode(Nd1)
        self.theNodes[1] = theDomain.getNode(Nd2)
        # check
        if self.theNodes[0] is None or self.theNodes[1] is None:
            if self.theNodes[0] is None:
                print('ZeroLengthSection::setDomain() -- Nd1:' +str(Nd1)+
                      ' does not exist in ')
            else:
                print('ZeroLengthSection::setDomain() -- Nd2:' +str(Nd2)+
                      ' does not exist in ')
            print('model for ZeroLengthSection with id '+str(self.getTag()))
            return
        # now determine the number of dof and the dimension
        dofNd1 = self.theNodes[0].getNumberDOF()
        dofNd2 = self.theNodes[1].getNumberDOF()
        if dofNd1!=dofNd2:
            print('ZeroLengthSection::setDomain() -- nodes '+str(Nd1)+' and '+str(Nd2)+
                  'have differing dof at ends for ZeroLengthSection '+str(self.getTag()))
            return
        self.numDOF = 2 * dofNd1
        if self.numDOF!=6 and self.numDOF!=12:
            print('ZeroLengthSection::setDomain() -- element only works for 3 (2d) or 6 (3d) dof per node')

        if self.numDOF==6:
            self.P = ZeroLengthSection.P6
            self.K = ZeroLengthSection.K6
        else:
            self.P = ZeroLengthSection.P12
            self.K = ZeroLengthSection.K12

        # Check that length is zero within tolerance
        end1Crd = self.theNodes[0].getCrds()
        end2Crd = self.theNodes[1].getCrds()
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
            print('ZeroLengthSection::setDomain() -- Element '+str(self.getTag())
                  + 'has L= '+ str(L)+', which is greater than the tolerance')
        self.setDomain(theDomain)
        # Set up the A matrix
        self.setTransformation()

    def setTransformation(self):
        # transformation matrix
        self.A = np.zeros((self.order, self.numDOF))
        # section deformation vector
        self.v = np.zeros(self.order)
        # Get the section code
        code = self.theSection.get_type()



