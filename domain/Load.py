from domain.DomainComponent import DomainComponent

class Load(DomainComponent):

    def __init__(self, tag):
        super().__init__(tag)
        self.loadPatternTag = -1

    def setLoadPatternTag(self, tag):
        self.loadPatternTag = tag
    
    def getLoadPatternTag(self):
        return self.loadPatternTag
    

    