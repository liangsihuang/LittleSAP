from analysis.system_of_eqn.LinearSOE import LinearSOE
import numpy as np

class FullGenLinSOE(LinearSOE):

    def __init__(self, theSolvr):

        super().__init__(theSolvr)
        self.size = 0
        # 普通 array，本来是用来构造Vector的？现在好像没有存在的意义？统一用narray
        self.A = np.zeros((self.size, self.size))  # 以rank-2 array A来储存矩阵A
        self.b = np.zeros(self.size)
        self.x = np.zeros(self.size)

        # # Vector/narray
        # self.vectX = np.zeros(self.size)
        # self.vectB = np.zeros(self.size)
        # self.matA = np.zeros((self.size, self.size))

        self.Asize = 0  # 矩阵A的行数×列数
        self.bsize = 0  # size 和 bsize 有什么区别？没区别，两者相等
        self.factored = False

        theSolvr.set_linear_SOE(self)

    def add_A(self, m, id1, fact=1.0):
        # 刚度矩阵组装
        # m 是 narray，单元刚度矩阵
        # id1 是 list? narray? , id是保留字，所以用id1，一个单元里所有节点的自由度=方程数，方程数从0开始
        # check for a quick return
        if fact == 0.0:
            return 0
        # check that m and id are of similar size
        idSize = len(id1)
        if idSize != m.shape[0] and idSize != m.shape[1]:
            print('FullGenLinSOE::addA() - Matrix and ID not of similar sizes.\n')
            return -1

        for i in range(0, idSize):
            row = id1[i]
            if row >= 0 and row < self.size:
                for j in range(0, idSize):
                    col = id1[j]
                    if col >= 0 and col < self.size:
                        self.A[row, col] += m[j, i] * fact
        return 0

    def add_b(self, v, id1, fact=1.0):
        # check for a quick return
        if fact == 0.0:
            return 0
        idSize = len(id1)
        # check that v and id are of similar size
        if idSize != len(v):
            print('FullGenLinSOE::add_b() - Vector and ID not of similar sizes\n')
            return -1
        for i in range(0, idSize):
            pos = id1[i]
            if pos >=0 and pos < self.size:
                self.b[pos] += v[i]*fact
        return 0

    def zero_A(self):
        self.A[:, :] = 0.0
        self.factored = False

    def zero_b(self):
        self.b[:] = 0.0

    def set_size(self, graph):
        result = 0
        # oldSize = self.size
        self.size = graph.get_num_vertex()

        if self.size*self.size > self.Asize:
            self.A = np.zeros((self.size, self.size))
            self.Asize = self.size * self.size
        self.factored = False

        if self.size > self.bsize:
            self.b = np.zeros(self.size)
            self.x = np.zeros(self.size)
            self.bsize = self.size

        # create new Vectors/narray
        # if self.size != oldSize:
        #     self.vectX = np.zeros(self.size)
        #     self.vectB = np.zeros(self.size)
        #     self.matA = np.zeros((self.size, self.size))

        # invoke set_size() on the Solver， 没必要了
        # theSolvr = self.getSolver()

        return result

    def get_x(self):
        return self.x

    def get_b(self):
        return self.b

    def get_A(self):
        return self.A

    def set_x(self, x):
        if len(x) == self.size:
            self.x = x

