from element.Element import Element
from math import sqrt
import numpy as np

class FourNodeQuad(Element):

    def __init__(self, tag, ndl, nd2, nd3, nd4, m, type, t, pressure=0.0, rho=0.0, b1=0.0, b2=0.0):
        super().__init__(tag)

