from analysis.algorithm.Linear import Linear
from analysis.StaticAnalysis import StaticAnalysis
from analysis.PlainNumberer import PlainNumberer
from analysis.PlainHandler import PlainHandler
from analysis.integrator.LoadControl import LoadControl
from analysis.integrator.DisplacementControl import DisplacementControl
from analysis.model.AnalysisModel import AnalysisModel
from domain.Domain import Domain
from domain.LoadPattern import LoadPattern
from domain.NodalLoad import NodalLoad
from domain.Node import Node
from domain.SP_Constraint import SP_Constraint
from domain.timeSeries.LinearSeries import LinearSeries
from element.Truss import Truss
from material.uniaxial.ElasticMaterial import ElasticMaterial
from analysis.system_of_eqn.FullGenLinSolver import FullGenLinSolver
from analysis.system_of_eqn.FullGenLinSOE import FullGenLinSOE
import numpy as np
theDomain = Domain()

node1 = Node(1, 2, 0.0, 0.0)
node2 = Node(2, 2, 144.0, 0.0)
node3 = Node(3, 2, 168.0, 0.0)
node4 = Node(4, 2, 72.0, 96.0)

theDomain.addNode(node1)
theDomain.addNode(node2)
theDomain.addNode(node3)
theDomain.addNode(node4)

theMaterial = ElasticMaterial(1, 3000.0)

truss1 = Truss(1, 2, 1, 4, theMaterial, 10.0)
truss2 = Truss(2, 2, 2, 4, theMaterial, 5.0)
truss3 = Truss(3, 2, 3, 4, theMaterial, 5.0)

theDomain.addElement(truss1)
theDomain.addElement(truss2)
theDomain.addElement(truss3)

sp1 = SP_Constraint(1, 1, 0.0, True)
sp2 = SP_Constraint(1, 2, 0.0, True)
sp3 = SP_Constraint(2, 1, 0.0, True)
sp4 = SP_Constraint(2, 2, 0.0, True)
sp5 = SP_Constraint(3, 1, 0.0, True)
sp6 = SP_Constraint(3, 2, 0.0, True)

theDomain.addSP_Constraint(sp1)
theDomain.addSP_Constraint(sp2)
theDomain.addSP_Constraint(sp3)
theDomain.addSP_Constraint(sp4)
theDomain.addSP_Constraint(sp5)
theDomain.addSP_Constraint(sp6)

theSeries = LinearSeries()
theLoadPattern = LoadPattern(1)
theLoadPattern.setTimeSeries(theSeries)
theDomain.addLoadPattern(theLoadPattern)

theLoadValues = np.array([100.0, -50.0])
# theLoadValues = np.array([100.0, 0.0])
theLoad = NodalLoad(1, 4, theLoadValues)
theDomain.addNodalLoad(theLoad, 1)

theModel = AnalysisModel()
theSolnAlgo = Linear()
theIntegrator = LoadControl(1.0, 1, 1.0, 1.0)
# theIntegrator = DisplacementControl(4, 1, 1.0, theDomain, 1.0, 1.0, 1.0)
theHandler = PlainHandler()
theNumberer = PlainNumberer()
theSolver = FullGenLinSolver()
theSOE = FullGenLinSOE(theSolver)

theAnalysis = StaticAnalysis(theDomain, theHandler, theNumberer, theModel, theSolnAlgo, theSOE, theIntegrator)

numSteps = 1
theAnalysis.analyze(numSteps)

d4 = node4.getDisp()
print(d4)
d3 = node3.getDisp()
print(d3)
d2 = node2.getDisp()
print(d2)
d1 = node1.getDisp()
print(d1)

print(theSOE.getA())
print(theSOE.getB())