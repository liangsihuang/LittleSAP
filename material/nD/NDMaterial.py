
# abstract base class

from material.Material import Material

class NDMaterial(Material):

    def __init__(self, tag):
        super().__init__(tag)
