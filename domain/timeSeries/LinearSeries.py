from domain.timeSeries.TimeSeries import TimeSeries


class LinearSeries(TimeSeries):
    
    def __init__(self, tag=0, theFactor=1.0):
        super().__init__(tag)
        self.c_factor = theFactor # factor = pseudoTime * c_factor

    def get_factor(self, pesudoTime):
        return self.c_factor*pesudoTime
