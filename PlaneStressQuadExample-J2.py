from analysis.algorithm.Linear import Linear
from analysis.StaticAnalysis import StaticAnalysis
from analysis.PlainNumberer import PlainNumberer
from analysis.PlainHandler import PlainHandler
from analysis.integrator.LoadControl import LoadControl
from analysis.model.AnalysisModel import AnalysisModel
from domain.Domain import Domain
from domain.LoadPattern import LoadPattern
from domain.NodalLoad import NodalLoad
from domain.Node import Node
from domain.SP_Constraint import SP_Constraint
from domain.timeSeries.LinearSeries import LinearSeries
from element.FourNodeQuad import FourNodeQuad

# 使用3维的材料降维
from material.nD.PlaneStressMaterial import PlaneStressMaterial
from material.nD.elasticIsotropic.ElasticIsotropicThreeDimensional import ElasticIsotropicThreeDimensional
from material.nD.j2Plasticity.J2ThreeDimensional import J2ThreeDimensional
from material.nD.j2Plasticity.J2PlaneStress import J2PlaneStress

from analysis.system_of_eqn.FullGenLinSolver import FullGenLinSolver
from analysis.system_of_eqn.FullGenLinSOE import FullGenLinSOE
import numpy as np
theDomain = Domain()

node1 = Node(1, 2, -2.5, 0.0)
node2 = Node(2, 2, 2.5, 0.0)
node3 = Node(3, 2, 2.5, 1.0)
node4 = Node(4, 2, -2.5, 1.0)

theDomain.add_node(node1)
theDomain.add_node(node2)
theDomain.add_node(node3)
theDomain.add_node(node4)


# theMaterial1 = ElasticIsotropicThreeDimensional(1, 200000.0, 0.3)
E = 2e5
v = 0.3
G = E/2/(1+v)
K = E/3/(1-2*v)
material = J2PlaneStress(1, K, G, 200, 300, 1.0, 1.0)

quad1 = FourNodeQuad(1, 1, 2, 3, 4, material, 'PlaneStress', 1.0)

theDomain.add_element(quad1)

sp1 = SP_Constraint(2, 1, 0.0, True)
sp2 = SP_Constraint(2, 2, 0.0, True)
sp3 = SP_Constraint(3, 1, 0.0, True)
sp4 = SP_Constraint(3, 2, 0.0, True)

theDomain.add_SP_constraint(sp1)
theDomain.add_SP_constraint(sp2)
theDomain.add_SP_constraint(sp3)
theDomain.add_SP_constraint(sp4)

theSeries = LinearSeries()
theLoadPattern = LoadPattern(1)
theLoadPattern.set_time_series(theSeries)
theDomain.add_load_pattern(theLoadPattern)

# theLoadValues = np.array([100.0, -50.0])
theLoadValues = np.array([-1.0e5, 0.0])
theLoad = NodalLoad(1, 4, theLoadValues)
theDomain.add_nodal_load(theLoad, 1)

theModel = AnalysisModel()
theSolnAlgo = Linear()
theIntegrator = LoadControl(1.0, 1, 1.0, 1.0)
theHandler = PlainHandler()
theNumberer = PlainNumberer()
theSolver = FullGenLinSolver()
theSOE = FullGenLinSOE(theSolver)

theAnalysis = StaticAnalysis(theDomain, theHandler, theNumberer, theModel, theSolnAlgo, theSOE, theIntegrator)

numSteps = 1
theAnalysis.analyze(numSteps)

d4 = node4.get_disp()
print(d4)
# d3 = node3.get_disp()
# print(d3)
# d2 = node2.get_disp()
# print(d2)
# d1 = node1.get_disp()
# print(d1)
#
# print(theSOE.get_A())
# print(theSOE.get_b())
#
# print(quad1.get_tangent_stiff())