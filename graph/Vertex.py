from TaggedObject import TaggedObject

class Vertex(TaggedObject):
    def __init__(self, tag, ref, weight=0, color=0):
        super().__init__(tag)
        self.ref = ref
        # reference: 1. 如果是DOFGraph，则 ref = tag = dof tag
        # 2. 如果是DOFGroupGraph，则 ref = DOF_Group相关的Node的tag
        self.weight = weight
        self.color = color

        self.degree = 0  # degree of node i is number of edges meeting at node i or number of vertices adjacent to it
        self.tmp = 0
        self.adjacency = []  # two nodes are said to be adjacent if they are connected by an edge

    # set method
    def set_weight(self, newWeight):
        self.weight = newWeight
    
    def set_color(self, newColor):
        self.color = newColor
    
    def set_tmp(self, newTmp):
        self.tmp = newTmp
    
    # get method
    def get_ref(self):
        return self.ref
    def get_weight(self):
        return self.weight
    def get_color(self):
        return self.color
    def get_tmp(self):
        return self.tmp
    def get_degree(self):
        return self.degree
    def get_adjacency(self):
        return self.adjacency
    
    # add method
    def add_edge(self, otherTag):
        # don't allow itself to be added
        if otherTag==self.get_tag():
            return 0
        # check the otherVertex has not already been added
        for i in range(0, len(self.adjacency)):
            if self.adjacency[i] == otherTag:
                print('Vertex.addEdge(): already exists. return!')
                return 0
        self.adjacency.append(otherTag)
        return 0





