from domain.Node import Node
from domain.SP_Constraint import SP_Constraint
from element.ZeroLengthSection import ZeroLengthSection
from domain.timeSeries.ConstantSeries import ConstantSeries
from domain.LoadPattern import LoadPattern
from domain.Domain import Domain
import numpy as np
from domain.NodalLoad import NodalLoad
from analysis.integrator.LoadControl import LoadControl

def MomentCurvature(secTag, axialLoad, maxK, numIncr=100):
    theDomain = Domain()
    # define two nodes at (0,0)
    node1 = Node(1, 3, 0.0, 0.0)
    node2 = Node(2, 3, 0.0, 0.0)

    # Fix all degrees of freedom except axial and bending
    sp1 = SP_Constraint(1, 1, 0.0, True)
    sp2 = SP_Constraint(1, 2, 0.0, True)
    sp3 = SP_Constraint(1, 3, 0.0, True)
    sp4 = SP_Constraint(2, 2, 0.0, True)

    # define element
    zerolengthsection1 = ZeroLengthSection(1, 1, 2, secTag)

    # Define constant axial load
    theSeries = ConstantSeries(1)
    theLoadPattern = LoadPattern(1)
    theLoadPattern.setTimeSeries(theSeries)
    theDomain.addLoadPattern(theLoadPattern)
    theLoadValues = np.array([axialLoad, 0.0, 0.0])
    theLoad = NodalLoad(1, 2, theLoadValues)
    theDomain.addNodalLoad(theLoad, 1)

    # define analysis parameters
    theModel = AnalysisModel()
    theSolnAlgo = Linear()
    theIntegrator = LoadControl(0.0, 1, 0.0, 0.0)
    theHandler = PlainHandler()
    theNumberer = PlainNumberer()
    theSolver = FullGenLinSolver()
    theSOE = FullGenLinSOE(theSolver)

    theAnalysis = StaticAnalysis(theDomain, theHandler, theNumberer, theModel, theSolnAlgo, theSOE, theIntegrator)

    numSteps = 1
    theAnalysis.analyze(numSteps)