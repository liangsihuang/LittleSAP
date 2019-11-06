from element.crdTransf.CrdTransf import CrdTransf
import numpy as np

class LinearCrdTransf2d(CrdTransf):

    def __init__(self, tag):
        super().__init__(tag)
        # pointers to the element two endnodes
        self.node_i = None
        self.node_j = None
        # rigid joint offsets
        self.node_i_offset = None
        self.node_j_offset = None
        # direction cosines of undeformed element wrt to global system
        self.cos_theta = 0.0
        self.sin_theta = 0.0
        # undeformed element length
        self.L = 0.0
        # matrix that transforms from global to local coordinates
        self.tlg = np.zeros((6, 6))
        # global stiffness matrix
        self.kg = np.zeros((6, 6))

        self.node_i_initial_disp = None
        self.node_j_initial_disp = None


    def get_basic_trial_disp(self):
        # determine global displacements
        disp1 = self.node_i.get_trial_disp()
        disp2 = self.node_j.get_trial_disp()

        ug = np.zeros(6)
        for i in range(0, 3):
            ug[i] = disp1[i]
            ug[i+3] = disp2[i]
        if self.node_i_initial_disp is not None:
            for j in range(0, 3):
                ug[j] -= self.node_i_initial_disp[j]
        if self.node_j_initial_disp is not None:
            for j in range(0, 3):
                ug[j+3] -= self.node_j_initial_disp[j]

        ub = np.zeros(3)
        sl = self.sin_theta / self.L
        cl = self.cos_theta / self.L

        ub[0] = -self.cos_theta * ug[0] - self.sin_theta * ug[1] + \
                self.cos_theta * ug[3] + self.sin_theta * ug[4]
        ub[1] = -sl * ug[0] + cl * ug[1] + ug[2] + \
                sl * ug[3] - cl * ug[4]

        if self.node_i_offset is not None:
            t02 = -self.cos_theta * self.node_i_offset[1] + self.sin_theta * self.node_i_offset[0]
            t12 = self.sin_theta * self.node_i_offset[1] + self.cos_theta * self.node_i_offset[0]
            ub[0] -= t02 * ug[2]
            ub[1] += 1.0/self.L * t12 * ug[0]

        if self.node_j_offset is not None:
            t35 = -self.cos_theta * self.node_j_offset[1] + self.sin_theta * self.node_j_offset[0]
            t45 = self.sin_theta * self.node_j_offset[1] + self.cos_theta * self.node_j_offset[0]
            ub[0] += t35 * ug[5]
            ub[1] -= 1.0/self.L * t45 * ug[5]

        ub[2] = ub[1] + ug[5] - ug[2]
        return ub

    def get_initial_length(self):
        return self.L

    def get_global_stiff_matrix(self, kb, pb):
        temp = np.zeros((6, 6))
