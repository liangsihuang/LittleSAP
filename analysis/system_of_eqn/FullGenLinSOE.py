from analysis.system_of_eqn import LinearSOE
# LinearSOE:
# storing linear system of equations of form Ax = b
# abstract base class, subclasses are:
# BandSPDLinearSOE
# SparseSPDLinearSOE
# BandGeneralLinearSOE
# EleByEleLinearSOE
# subclass do not actually store the components of the system, for example the A matrix


class FullGenLinSOE(LinearSOE):

    def __init__(self, theSolvr):
        super().__init__(theSolvr)
        self.size = 0
        # numpy array
        self.A = None  # 以rank-2 array A来储存矩阵A
        self.B = None
        self.X = None

        # Vector
        self.vectX = None
        self.vectB = None
        self.matA = None

        self.Asize = 0  # 矩阵A的行数×列数
        self.Bsize = 0  # size 和 Bize 有什么区别？
        self.factored = False

        theSolvr.setLinearSOE(self)

    def addA(self, m, id1, fact=1.0):
        # 刚度矩阵组装
        # m 是 narray，单元刚度矩阵
        # id1 是 list? narray? , id是保留字，所以用id1，一个单元里所有节点的自由度=方程数，方程数从0开始
        # check for a quick return
        if fact == 0.0:
            return
        # check that m and id are of similar size
        idSize = len(id1)
        if idSize != m.shape[0] and idSize != m.shape[1]:
            print('FullGenLinSOE::addA() - Matrix and ID not of similar sizes.\n')
            return -1

        for i in range(0, idSize):
            row = id1[i]
            for j in range(0, idSize):
                col = id1[j]
                self.A[row, col] += m[j, i] * fact