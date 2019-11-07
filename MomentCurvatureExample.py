from domain.Node import Node
from domain.SP_Constraint import SP_Constraint
from element.ZeroLengthSection import ZeroLengthSection
from material.uniaxial.Concrete01 import Concrete01
from material.uniaxial.Steel01 import Steel01
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
from material.section.Fiber.UniaxialFiber3d import UniaxialFiber3d
from material.section.FiberSection3d import FiberSection3d

domain = Domain()

# core concrete (confined)
m1 = Concrete01(1, -6.0, -0.004, -5.0, -0.014)
# cover concrete (unconfined)
m2 = Concrete01(2, -5.0, -0.002, 0.0, -0.006)
# steel
m3 = Steel01(3, 60.0, 30000.0, 0.01)

colWidth = 15
colDepth = 24
cover = 1.5
As = 0.60 # area of no.7 bars
y1 = colDepth / 2.0
z1 = colWidth / 2.0

# core concrete (confined)
fibers =[]
fibers.append(UniaxialFiber3d(1, m1, 25.2, [9.45, 0]))
fibers.append(UniaxialFiber3d(2, m1, 25.2, [7.35, 0]))
fibers.append(UniaxialFiber3d(3, m1, 25.2, [5.25, 0]))
fibers.append(UniaxialFiber3d(4, m1, 25.2, [3.15, 0]))
fibers.append(UniaxialFiber3d(5, m1, 25.2, [1.05, 0]))
fibers.append(UniaxialFiber3d(6, m1, 25.2, [-1.05, 0]))
fibers.append(UniaxialFiber3d(7, m1, 25.2, [-3.15, 0]))
fibers.append(UniaxialFiber3d(8, m1, 25.2, [-5.25, 0]))
fibers.append(UniaxialFiber3d(9, m1, 25.2, [-7.35, 0]))
fibers.append(UniaxialFiber3d(10, m1, 25.2, [-9.45, 0]))
# cover concrete (unconfined)
fibers.append(UniaxialFiber3d(11, m2, 3.6, [10.8, 6.75]))
fibers.append(UniaxialFiber3d(12, m2, 3.6, [8.4, 6.75]))
fibers.append(UniaxialFiber3d(13, m2, 3.6, [6.0, 6.75]))
fibers.append(UniaxialFiber3d(14, m2, 3.6, [3.6, 6.75]))
fibers.append(UniaxialFiber3d(15, m2, 3.6, [1.2, 6.75]))
fibers.append(UniaxialFiber3d(16, m2, 3.6, [-1.2, 6.75]))
fibers.append(UniaxialFiber3d(17, m2, 3.6, [-3.6, 6.75]))
fibers.append(UniaxialFiber3d(18, m2, 3.6, [-6.0, 6.75]))
fibers.append(UniaxialFiber3d(19, m2, 3.6, [-8.4, 6.75]))
fibers.append(UniaxialFiber3d(20, m2, 3.6, [-10.8, 6.75]))

fibers.append(UniaxialFiber3d(21, m2, 3.6, [10.8, -6.75]))
fibers.append(UniaxialFiber3d(22, m2, 3.6, [8.4, -6.75]))
fibers.append(UniaxialFiber3d(23, m2, 3.6, [6.0, -6.75]))
fibers.append(UniaxialFiber3d(24, m2, 3.6, [3.6, -6.75]))
fibers.append(UniaxialFiber3d(25, m2, 3.6, [1.2, -6.75]))
fibers.append(UniaxialFiber3d(26, m2, 3.6, [-1.2, -6.75]))
fibers.append(UniaxialFiber3d(27, m2, 3.6, [-3.6, -6.75]))
fibers.append(UniaxialFiber3d(28, m2, 3.6, [-6.0, -6.75]))
fibers.append(UniaxialFiber3d(29, m2, 3.6, [-8.4, -6.75]))
fibers.append(UniaxialFiber3d(30, m2, 3.6, [-10.8, -6.75]))

fibers.append(UniaxialFiber3d(31, m2, 9, [11.625, 0.0]))
fibers.append(UniaxialFiber3d(32, m2, 9, [10.875, 0.0]))
fibers.append(UniaxialFiber3d(33, m2, 9, [-10.875, 0.0]))
fibers.append(UniaxialFiber3d(34, m2, 9, [-11.625, 0.0]))
# steel
fibers.append(UniaxialFiber3d(35, m3, 0.6, [10.5, -6.0]))
fibers.append(UniaxialFiber3d(36, m3, 0.6, [10.5, 0.0]))
fibers.append(UniaxialFiber3d(37, m3, 0.6, [10.5, 6.0]))
fibers.append(UniaxialFiber3d(38, m3, 0.6, [0.0, -6.0]))
fibers.append(UniaxialFiber3d(39, m3, 0.6, [0.0, 6.0]))
fibers.append(UniaxialFiber3d(40, m3, 0.6, [-10.5, -6.0]))
fibers.append(UniaxialFiber3d(41, m3, 0.6, [-10.5, 0.0]))
fibers.append(UniaxialFiber3d(42, m3, 0.6, [-10.5, 6.0]))

s1 = FiberSection3d(1, 42, fibers)

def MomentCurvature(s1, axialLoad, maxK, numIncr=100):
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
    zerolengthsection1 = ZeroLengthSection(1, 2, 1, 2, s1)
    theDomain.add_element(zerolengthsection1)

    # Define constant axial load
    theSeries1 = ConstantSeries(1)
    theLoadPattern1 = LoadPattern(1)
    theLoadPattern1.set_time_series(theSeries1)
    theDomain.add_load_pattern(theLoadPattern1)
    theLoadValues = np.array([axialLoad, 0.0, 0.0])
    theLoad1 = NodalLoad(1, 2, theLoadValues)
    theDomain.add_nodal_load(theLoad1, 1)

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
    theLoadPattern2.set_time_series(theSeries2)
    theDomain.add_load_pattern(theLoadPattern2)
    theLoadValues = np.array([0.0, 0.0, 1.0])
    theLoad2 = NodalLoad(2, 2, theLoadValues)
    theDomain.add_nodal_load(theLoad2, 2)

    # Compute curvature increment
    dK = maxK/numIncr
    theIntegrator2 = DisplacementControl(2,3,dK,theDomain,1,dK,dK)
    theAnalysis2 = StaticAnalysis(theDomain, theHandler, theNumberer, theModel, theSolnAlgo, theSOE, theIntegrator2)
    theAnalysis2.analyze(numIncr)

