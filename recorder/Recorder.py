from TaggedObject import TaggedObject

class Recorder(TaggedObject):
    lastRecorderTag = 0
    def __init__(self):
        super().__init__(Recorder.lastRecorderTag)
        Recorder.lastRecorderTag += 1

    
    