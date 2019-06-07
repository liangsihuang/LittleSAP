from domain.DomainComponent import DomainComponent


class LoadPattern(DomainComponent):

    def __init__(self, tag, fact=1.0):
        super().__init__(tag)
        self.is_constant = 1  # to indicate whether setConstant has been called
        self.load_factor = 0  # current load factor
        self.scale_factor = fact  # factor to scale load factor from time series

        self.series = None

        self.current_Geo_tag = 0
        # self.lastGeoSendTag = -1
        # storage objects for the loads and constraints
        self.nodal_loads = {}
        self.elemental_loads = {}
        self.SPs = {}

    # methods to set the associated TimeSeries and Domain
    def set_time_series(self, theTimeSeries):
        self.series = theTimeSeries

    def set_domain(self, domain):
        for tag in self.nodal_loads:
            nodLoad = self.nodal_loads[tag]
            nodLoad.set_domain(domain)
        for tag in self.elemental_loads:
            eleLoad = self.elemental_loads[tag]
            eleLoad.set_domain(domain)
        for tag in self.SPs:
            theSP = self.SPs[tag]
            theSP.set_domain(domain)

        super().set_domain(domain)

    # methods to add loads
    def add_nodal_load(self, load):
        domain = self.get_domain()
        self.nodal_loads[load.get_tag()] = load
        if domain is not None:
            load.set_domain(domain)
        load.set_loadpattern_tag(self.get_tag())
        self.current_Geo_tag += 1

    # def addElementalLoad(self, load):
    #     pass
    # def addSP_Constraint(self, theSP):
    #     pass

    def get_nodal_loads(self):
        return self.nodal_loads

    def get_elemental_loads(self):
        return self.elemental_loads

    def get_SPs(self):
        return self.SPs

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
    def apply_load(self, pseudoTime=0.0):
        # first determine the load factor
        if self.series is not None and self.is_constant != 0:
            self.load_factor = self.series.get_factor(pseudoTime)
            self.load_factor *= self.scale_factor

        nodal_loads = self.get_nodal_loads()
        for tag in nodal_loads:
            nodLoad = nodal_loads[tag]
            nodLoad.apply_load(self.load_factor)

        # eleLoad 略

        SPs = self.get_SPs()
        for tag in SPs:
            sp = SPs[tag]
            sp.apply_constraint(self.load_factor)

    # def setLoadConstant(self):
    #     pass
    # def unsetLoadConstant(self):
    #     pass
    # def getLoadFactor(self):
    #     pass

    # methods for o/p

    # methods to obtain a blank copy of the LoadPattern
