from element.Element import Element
from math import sqrt
import numpy as np

class FourNodeQuad(Element):

    def __init__(self, tag, nd1, nd2, nd3, nd4, m, type, t, pressure=0.0, rho=0.0, b1=0.0, b2=0.0):
        super().__init__(tag)

        self.pts = [[-0.5773502691896258, -0.5773502691896258],
                    [0.5773502691896258, -0.5773502691896258],
                    [0.5773502691896258, 0.5773502691896258],
                    [-0.5773502691896258, 0.5773502691896258]]
        self.wts = [1.0, 1.0, 1.0, 1.0]

        if type!='PlaneStrain' and type!='PlaneStress':
            print('FourNodeQuad::FourNodeQuad -- material type must be PlainStrain or PlainStress.\n')

        # body force
        self.b = [b1, b2]

        # Get copies of the material model for each integration point
        self.material = [None, None, None, None]
        for i in range(0,4):
            self.material[i] = m.getCopy(type)

        self.connected_external_nodes = [nd1, nd2, nd3, nd4]
        self.nodes = [None, None, None, None]
        self.q = [] # Applied nodal loads
        self.thickness = t
        self.pressure = pressure
        self.rho = rho


