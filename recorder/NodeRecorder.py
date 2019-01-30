from recorder.Recorder import Recorder
import numpy as np
class NodeRecorder(Recorder):

    def __init__(self, dofs, nodes, dataToStore, theDom, dT, timeFlag, theSeries):
        # dofs, nodes 都是 ID
        super().__init__()
        numDOF = len(dofs)
        if numDOF != 0:
            theDofs = np.zeros(numDOF, dtype=int)
            count = 0
            for i in range(0, numDOF):
                dof = dofs[i]
                if dof >= 0:
                    theDofs[count] = dof
                    count += 1
                else:
                    print('NodeRecorder::NodeRecorder - invalid dof '+str(dof)+' will be ignored\n')
        # create memory to hold nodal ID's
        numNode = len(nodes)
        if numNode != 0:
            self.theNodalTags = nodes

        self.theTimeSeries = theSeries
        if self.theTimeSeries is not None:
            self.timeSeriesValues = np.zeros(numDOF)

        # set the data flag used as a switch to get the response in a record
        if dataToStore == 'disp':
            self.dataFlag = 0
        else:
            self.dataFlag = 10
            print('NodeRecorder::NodeRecorder - dataToStore '+ str(dataToStore)+
                  ' not recognized (disp, vel, accel, incrDisp, incrDeltaDisp)\n')

        
    
    