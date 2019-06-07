from TaggedObject import TaggedObject

class DomainComponent(TaggedObject):
    
    def __init__(self, tag):
        super().__init__(tag)
        self.domain = None
    
    def set_domain(self, model):
        self.domain = model
    
    def get_domain(self):
        return self.domain




