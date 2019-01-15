from TaggedObject import TaggedObject
class DomainComponent(TaggedObject):
    
    def __init__(self, tag):
        super().__init__(tag)
        self.theDomain = None
    
    def setDomain(self, model):
        self.theDomain = model
    
    def getDomain(self):
        return self.theDomain




