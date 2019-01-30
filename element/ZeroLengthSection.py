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

    def __init__(self, tag, dimension, Nd1, Nd2, x, yprime, theSection, doRayleighDamping=0):
        super().__init__(tag)
        self.connectedExternalNodes = np.zeros(2, dtype=int)
        self.theNodes = []
        self.dimension = dimension
        self.numDOF = 0
        self.transformation = np.zeros((3,3))
        self.useRayleighDamping = doRayleighDamping # int

        self.A = None # Transformation matrix ... e = A*(u2-u1)
        self.v = None # Section deformation vector, the element basic deformations
        self.K = None # Pointer to element stiffness matrix
        self.P = None # Pointer to element force vector

        self.theSection = theSection.getCopy() # SectionForceDeformation object
        self.order = theSection.getOrder() # Order of the section model

        # Set up the transformation matrix of direction cosines
        self.setUp(Nd1, Nd2, x, yprime)

    def setUp(self, Nd1, Nd2, x, yp):
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
        y = np.zeros(3)
        y[0] = z[1]*x[2] - z[2]*x[1]
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



