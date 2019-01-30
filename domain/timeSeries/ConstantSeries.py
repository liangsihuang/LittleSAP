from domain.timeSeries.TimeSeries import TimeSeries

class ConstantSeries(TimeSeries):
    
    def __init__(self, tag=0, theFactor=1.0):
        super().__init__(tag)
        self.cFactor = theFactor # factor = pseudoTime * cFactor

