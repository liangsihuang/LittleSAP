from material.Material import Material

# 定义一些常数，子类引用
SECTION_RESPONSE_MZ = 1
SECTION_RESPONSE_P = 2
SECTION_RESPONSE_VY = 3
SECTION_RESPONSE_MY = 4
SECTION_RESPONSE_VZ = 5
SECTION_RESPONSE_T = 6
SECTION_RESPONSE_R = 7
SECTION_RESPONSE_Q = 8


class SectionForceDeformation(Material):

    def __init__(self, tag):
        super().__init__(tag)
        self.sDefault = None  # Vector  干嘛的？ stress
        self.fDefault = None  # Matrix  干什么？ flexibility 柔度矩阵


