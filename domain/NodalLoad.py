from domain.Load import Load

class NodalLoad(Load):

    def __init__(self, tag, node, theLoad, isLoadConstant=False):
        super().__init__(tag)
        self.myNodeTag = node                 # tag indicating associated Node objects tag
        self.myNode = None              # pointer to Node object on which load acts
        self.load = theLoad                # a vector / list
        self.konstant = isLoadConstant     # true if load is load factor independent
    
    def setDomain(self, newDomain):
        if newDomain is None:
            return
        super().setDomain(newDomain)
    
    def getNodeTag(self):
        return self.myNodeTag

    def applyLoad(self, loadFactor):
        if self.myNode is None:
            theDomain = self.getDomain()
            self.myNode = theDomain.getNode(self.myNodeTag)
            if theDomain is None or self.myNode is None:
                print('WARNING NodalLoad::applyLoad() - No associated Node node for NodalLoad')
                return
        # add the load times the loadfactor to nodal unbalanced load
        if self.konstant == False:
            self.myNode.addUnbalancedLoad(self.load, loadFactor)
        else:
            self.myNode.addUnbalancedLoad(self.load, 1.0)

     
    
