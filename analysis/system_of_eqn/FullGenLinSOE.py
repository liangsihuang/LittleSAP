from analysis.system_of_eqn.LinearSOE import LinearSOE
import numpy as np

class FullGenLinSOE(LinearSOE):

    def __init__(self, theSolvr):
        super().__init__(theSolvr)
        self.size = 0
        # 普通 array，本来是用来构造Vector的？现在好像没有存在的意义？统一用narray
        self.A = np.zeros((self.size, self.size))  # 以rank-2 array A来储存矩阵A
        self.B = np.zeros(self.size)
        self.X = np.zeros(self.size)

        # Vector/narray
        self.vectX = np.zeros(self.size)
        self.vectB = np.zeros(self.size)
        self.matA = np.zeros((self.size, self.size))

        self.Asize = 0  # 矩阵A的行数×列数
        self.Bsize = 0  # size 和 Bize 有什么区别？没区别，两者相等
        self.factored = False

        theSolvr.setLinearSOE(self)

    def addA(self, m, id1, fact=1.0):
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

    def addB(self, v, id1, fact=1.0):
        # check for a quick return
        if fact == 0.0:
            return 0
        idSize = len(id1)
        # check that v and id are of similar size
        if idSize != len(v):
            print('FullGenLinSOE::addB() - Vector and ID not of similar sizes\n')
            return -1
        for i in range(0, idSize):
            pos = id1[i]
            if pos >=0 and pos < self.size:
                self.B[pos] += v[i]*fact
        return 0

    def zeroA(self):
        self.A[:, :] = 0.0
        self.factored = False

    def zeroB(self):
        self.B[:] = 0.0

    def setSize(self, graph):
        result = 0
        oldSize = self.size
        self.size = graph.getNumVertex()

        if self.size*self.size > self.Asize:
            self.A = np.zeros((self.size, self.size))
            self.Asize = self.size * self.size
        self.factored = False

        if self.size > self.Bsize:
            self.B = np.zeros(self.size)
            self.X = np.zeros(self.size)
            self.Bsize = self.size

        # create new Vectors/narray
        if self.size != oldSize:
            self.vectX = np.zeros(self.size)
            self.vectB = np.zeros(self.size)
            self.matA = np.zeros((self.size, self.size))

        # invoke setSize() on the Solver， 没必要了
        # theSolvr = self.getSolver()

        return result

    def getX(self):
        return self.vectX

    def setX(self, x):
        if len(x)==self.size:
            self.vectX = x
