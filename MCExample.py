from domain.Node import Node
from domain.SP_Constraint import SP_Constraint
from element.ZeroLengthSection import ZeroLengthSection
from domain.timeSeries.ConstantSeries import ConstantSeries
from domain.LoadPattern import LoadPattern
from domain.Domain import Domain
import numpy as np
from domain.NodalLoad import NodalLoad
from analysis.integrator.LoadControl import LoadControl
from analysis.algorithm.NewtonRaphson import NewtonRaphson
from analysis.model.AnalysisModel import AnalysisModel
from analysis.PlainHandler import  PlainHandler
from analysis.PlainNumberer import PlainNumberer
from analysis.system_of_eqn.FullGenLinSOE import FullGenLinSOE
from analysis.system_of_eqn.FullGenLinSolver import FullGenLinSolver
from analysis.StaticAnalysis import StaticAnalysis
from domain.timeSeries.LinearSeries import LinearSeries
from analysis.integrator.DisplacementControl import DisplacementControl

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
    theSeries1 = ConstantSeries(1)
    theLoadPattern1 = LoadPattern(1)
    theLoadPattern1.setTimeSeries(theSeries1)
    theDomain.addLoadPattern(theLoadPattern1)
    theLoadValues = np.array([axialLoad, 0.0, 0.0])
    theLoad1 = NodalLoad(1, 2, theLoadValues)
    theDomain.addNodalLoad(theLoad1, 1)

    # define analysis parameters
    theModel = AnalysisModel()
    theSolnAlgo = NewtonRaphson()
    theIntegrator = LoadControl(0.0, 1, 0.0, 0.0)
    theHandler = PlainHandler()
    theNumberer = PlainNumberer()
    theSolver = FullGenLinSolver()
    theSOE = FullGenLinSOE(theSolver)

    theAnalysis = StaticAnalysis(theDomain, theHandler, theNumberer, theModel, theSolnAlgo, theSOE, theIntegrator)
    # Do one analysis for constant axial load
    numSteps = 1
    theAnalysis.analyze(numSteps)

    # Define reference moment
    theSeries2 = LinearSeries(2)
    theLoadPattern2 = LoadPattern(2)
    theLoadPattern2.setTimeSeries(theSeries2)
    theDomain.addLoadPattern(theLoadPattern2)
    theLoadValues = np.array([0.0, 0.0, 1.0])
    theLoad2 = NodalLoad(2, 2, theLoadValues)
    theDomain.addNodalLoad(theLoad2, 2)

    # Compute curvature increment
    dK = maxK/numIncr
    theIntegrator2 = DisplacementControl(2,3,dK,theDomain,1,dK,dK)
    theAnalysis2 = StaticAnalysis(theDomain, theHandler, theNumberer, theModel, theSolnAlgo, theSOE, theIntegrator2)
    theAnalysis2.analyze(numIncr)

