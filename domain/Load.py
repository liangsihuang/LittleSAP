from domain.DomainComponent import DomainComponent

class Load(DomainComponent):

    def __init__(self, tag):
        super().__init__(tag)
        self.loadpattern_tag = -1

    def set_loadpattern_tag(self, tag):
        self.loadpattern_tag = tag
    
    def get_loadpattern_tag(self):
        return self.loadpattern_tag
    

    