from element.Element import Element
from math import sqrt
import numpy as np
from copy import deepcopy

class FourNodeQuad(Element):

    def __init__(self, tag, nd1, nd2, nd3, nd4, material, type, t, pressure=0.0, rho=0.0, b1=0.0, b2=0.0):
        super().__init__(tag)

        self.pts = [[-0.5773502691896258, -0.5773502691896258],
                    [0.5773502691896258, -0.5773502691896258],
                    [0.5773502691896258, 0.5773502691896258],
                    [-0.5773502691896258, 0.5773502691896258]]
        self.wts = [1.0, 1.0, 1.0, 1.0]

        # shape functions and derivatives (overwritten)
        # 只存储某一个积分点上的形函数及其对真实坐标(x,y)导数，所以会被覆盖
        self.shp = np.zeros((3, 4))


        if type!='PlaneStrain' and type!='PlaneStress':
            print('FourNodeQuad::FourNodeQuad -- material type must be PlainStrain or PlainStress.\n')

        # body force
        self.b = [b1, b2]

        # Allocate arrays of pointers to NDMaterials
        # Get copies of the material model for each integration point
        self.material = [None, None, None, None]
        for i in range(0,4):
            self.material[i] = deepcopy(material)

        self.connected_external_nodes = [nd1, nd2, nd3, nd4]
        self.nodes = [None, None, None, None]
        self.q = [] # Applied nodal loads
        self.thickness = t
        self.pressure = pressure
        self.rho = rho


    def get_num_external_nodes(self):
        return 4

    def get_external_nodes(self):
        return self.connected_external_nodes

    def get_nodes(self):
        return self.nodes

    def get_num_dof(self):
        return 8

    def set_domain(self, domain):

        # Check Domain is not null - invoked when object removed from a domain
        if domain is None:
            self.nodes[0] = None
            self.nodes[1] = None
            self.nodes[2] = None
            self.nodes[3] = None
            return

        nd1 = self.connected_external_nodes[0]
        nd2 = self.connected_external_nodes[1]
        nd3 = self.connected_external_nodes[2]
        nd4 = self.connected_external_nodes[3]

        self.nodes[0] = domain.get_node(nd1)
        self.nodes[1] = domain.get_node(nd2)
        self.nodes[2] = domain.get_node(nd3)
        self.nodes[3] = domain.get_node(nd4)

        super().set_domain(domain)

        # Compute consistent nodal loads due to pressure
        # self.set_pressure_load_at_nodes()

    def commit_state(self):
        value = 0
        # Loop over the integration points and commit the material states
        for i in range(0, 4):
            value += self.material[i].commit_state()
        return value

    def update(self):
        # 注意：提出来是1-d array
        d1 = self.nodes[0].get_trial_disp()
        d2 = self.nodes[1].get_trial_disp()
        d3 = self.nodes[2].get_trial_disp()
        d4 = self.nodes[3].get_trial_disp()

        di = [d1, d2, d3, d4]

        eps = np.zeros(3) # strain
        value = 0

        # Loop over the integration points
        for i in range(0, 4):
            # Determine Jacobian for this integration point
            self.shape_function(self.pts[i][0], self.pts[i][1])
            # Interpolate strains
            # eps = B*u;
            for j in range(0, 4):
                Ni_x = self.shp[0, i]
                Ni_y = self.shp[1, i]
                Bi = np.array([[Ni_x, 0], [0, Ni_y], [Ni_y, Ni_x]])
                eps += np.dot(Bi, di[i])
            # set the material strain
            value += self.material[i].set_trial_strain(eps)
        return value






    def shape_function(self, xi, eta):
        nd1_crds = self.nodes[0].get_crds()
        nd2_crds = self.nodes[1].get_crds()
        nd3_crds = self.nodes[2].get_crds()
        nd4_crds = self.nodes[3].get_crds()


        x1 = nd1_crds[0]
        y1 = nd1_crds[1]
        x2 = nd2_crds[0]
        y2 = nd2_crds[1]
        x3 = nd3_crds[0]
        y3 = nd3_crds[1]
        x4 = nd4_crds[0]
        y4 = nd4_crds[1]

        one_minus_eta = 1.0 - eta
        one_plus_eta = 1.0 + eta
        one_minus_xi = 1.0 - xi
        one_plus_xi = 1.0 + xi

        # 形函数(Ni) 放在第3行 Ni = 1/4 * (1+xi_i*xi) * (1+eta_i * eta)
        self.shp[2, 0] = 0.25 * one_minus_xi * one_minus_eta # N1
        self.shp[2, 1] = 0.25 * one_plus_xi * one_minus_eta  # N2
        self.shp[2, 2] = 0.25 * one_plus_xi * one_plus_eta  # N3
        self.shp[2, 3] = 0.25 * one_minus_xi * one_plus_eta  # N4

        # _ 代表“求导”
        N1_xi = -0.25 * one_minus_eta
        N2_xi = 0.25 * one_minus_eta
        N3_xi = 0.25 * one_plus_eta
        N4_xi = -0.25 * one_plus_eta

        N1_eta = -0.25 * one_minus_xi
        N2_eta = -0.25 * one_plus_xi
        N3_eta = 0.25 * one_plus_xi
        N4_eta = 0.25 * one_minus_xi

        # 单元的Jacobian 矩阵
        J = np.zeros((2, 2))
        J[0, 0] = x1 * N1_xi + x2 * N2_xi + x3 * N3_xi + x4 * N4_xi
        J[0, 1] = y1 * N1_xi + y2 * N2_xi + y3 * N3_xi + y4 * N4_xi
        J[1, 0] = x1 * N1_eta + x2 * N2_eta + x3 * N3_eta + x4 * N4_eta
        J[1, 1] = y1 * N1_eta + y2 * N2_eta + y3 * N3_eta + y4 * N4_eta

        Jinv = np.linalg.inv(J)

        temp = np.dot(Jinv, np.array([N1_xi, N1_eta]))
        N1_x = temp[0]
        N1_y = temp[1]
        temp = np.dot(Jinv, np.array([N2_xi, N2_eta]))
        N2_x = temp[0]
        N2_y = temp[1]
        temp = np.dot(Jinv, np.array([N3_xi, N3_eta]))
        N3_x = temp[0]
        N3_y = temp[1]
        temp = np.dot(Jinv, np.array([N4_xi, N4_eta]))
        N4_x = temp[0]
        N4_y = temp[1]
        # 形函数对原坐标（x,y）的导数，用来后续计算B矩阵
        # 第1行：Ni,x
        self.shp[0, 0] = N1_x
        self.shp[0, 1] = N2_x
        self.shp[0, 2] = N3_x
        self.shp[0, 3] = N4_x
        # 第2行：Ni,y
        self.shp[1, 0] = N1_y
        self.shp[1, 1] = N2_y
        self.shp[1, 2] = N3_y
        self.shp[1, 3] = N4_y

        detJ = np.linalg.det(J)
        return detJ



