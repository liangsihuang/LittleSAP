from domain.Load import Load

class NodalLoad(Load):

    def __init__(self, tag, node, theLoad, isLoadConstant=False):
        super().__init__(tag)
        self.node_tag = node                 # tag indicating associated Node objects tag
        self.node = None              # pointer to Node object on which load acts
        self.load = theLoad                # a vector / list
        self.konstant = isLoadConstant     # true if load is load factor independent
    
    def set_domain(self, newDomain):
        if newDomain is None:
            return
        super().set_domain(newDomain)
    
    def get_node_tag(self):
        return self.node_tag

    def apply_load(self, loadFactor):
        if self.node is None:
            domain = self.get_domain()
            self.node = domain.get_node(self.node_tag)
            if domain is None or self.node is None:
                print('WARNING NodalLoad::apply_load() - No associated Node node for NodalLoad')
                return
        # add the load times the loadfactor to nodal unbalanced load
        if self.konstant == False:
            self.node.add_unbalanced_load(self.load, loadFactor)
        else:
            self.node.add_unbalanced_load(self.load, 1.0)

     
    
