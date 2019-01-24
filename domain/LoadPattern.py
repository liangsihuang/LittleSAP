from domain.DomainComponent import DomainComponent

class LoadPattern(DomainComponent):

    def __init__(self, tag, fact=1.0):
        super().__init__(tag)
        self.isConstant = 1        # to indicate whether setConstant has been called
        self.loadFactor = 0        # current load factor
        self.scaleFactor = fact    # factor to scale load factor from time series

        self.theSeries = None      

        self.currentGeoTag = 0
        self.lastGeoSendTag = -1
        # storage objects for the loads and constraints
        self.theNodalLoads = {}
        self.theElementalLoads = {}
        self.theSPs = {}

    # methods to set the associated TimeSeries and Domain
    def setTimeSeries(self, theTimeSeries):
        self.theSeries = theTimeSeries

    def setDomain(self, theDomain):
        for tag in self.theNodalLoads:
            nodLoad = self.theNodalLoads[tag]
            nodLoad.setDomain(theDomain)
        for tag in self.theElementalLoads:
            eleLoad = self.theElementalLoads[tag]
            eleLoad.setDomain(theDomain)
        for tag in self.theSPs:
            theSP = self.theSPs[tag]
            theSP.setDomain(theDomain)
        
        super().setDomain(theDomain)

    # methods to add loads
    def addNodalLoad(self, load):
        theDomain = self.getDomain()
        self.theNodalLoads[load.getTag()] = load
        if theDomain is not None:
            load.setDomain(theDomain)
        load.setLoadPatternTag(self.getTag())
        self.currentGeoTag += 1
        
    # def addElementalLoad(self, load):
    #     pass
    # def addSP_Constraint(self, theSP):
    #     pass
    
    def getNodalLoads(self):
        return self.theNodalLoads
    def getElementalLoads(self):
        return self.theElementalLoads
    def getSPs(self):
        return self.theSPs

    # methods to remove loads
    # def clearAll(self):
    #     pass
    # def removeNodalLoad(self, tag):
    #     pass
    # def removeElementalLoad(self, tag):
    #     pass
    # def removeSP_Constraint(self, tag):
    #     pass

    # methods to apply loads
    def applyLoad(self, pseudoTime=0.0):
        # first determine the load factor
        if self.theSeries is not None and self.isConstant != 0:
            self.loadFactor = self.theSeries.getFactor(pseudoTime)
            self.loadFactor *= self.scaleFactor

        theNodalLoads = self.getNodalLoads()
        for tag in theNodalLoads:
            nodLoad = theNodalLoads[tag]

        # eleLoad 略

        theSPs = self.getSPs()
        for tag in theSPs:
            sp = theSPs[tag]
            sp.applyConstraint(self.loadFactor)


    # def setLoadConstant(self):
    #     pass
    # def unsetLoadConstant(self):
    #     pass
    # def getLoadFactor(self):
    #     pass

    # methods for o/p

    # methods to obtain a blank copy of the LoadPattern
    


    


