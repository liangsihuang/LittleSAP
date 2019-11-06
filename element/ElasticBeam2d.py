from element.Element import Element
import numpy as np
from copy import deepcopy

class ElasticBeam2d(Element):

    def __init__(self, tag, a, e, i, nd1, nd2, coord_transf, alpha=0.0, depth=0.0, rho=0.0, cm=0):
        super().__init__(tag)
        self.A = a
        self.E = e
        self.I = i
        self.alpha = alpha  # coeff. of thermal expansion
        self.d = depth      # ?
        self.rho = rho      # mass per unit length
        self.c_mass = cm    # consistent mass flag

        self.Q = np.zeros(6)
        self.q = np.zeros(3)

        self.connected_external_nodes = [nd1, nd2]
        self.coord_transf = deepcopy(coord_transf)

        self.q0 = np.zeros(3)
        self.p0 = np.zeros(3)

        self.nodes = [None, None]

        self.K = np.zeros((6, 6))
        self.P = np.zeros(6)
        self.kb = np.zeros((3, 3))

    def get_tangent_stiff(self):
        v = self.coord_transf.get_basic_trial_disp()
        L = self.coord_transf.get_initial_length()
        # determine q = kv + q0
        t1 = self.E * self.A / L
        t2 = 2.0 * self.E * self.I / L
        t3 = 4.0 * self.E * self.I / L

        self.q[0] = t1 * v[0]
        self.q[1] = t3 * v[1] + t2 * v[2]
        self.q[2] = t2 * v[1] + t3 * v[2]

        self.q[0] += self.q0[0]
        self.q[1] += self.q0[1]
        self.q[2] += self.q0[2]

        self.kb[0, 0] = t1
        self.kb[1, 1] = t3
        self.kb[2, 2] = t3
        self.kb[2, 1] = t2
        self.kb[1, 2] = t2

        return self.coord_transf.get_global_stiff_matrix(self.kb, self.q)



