from graph.Graph import Graph
from graph.Vertex import Vertex


# AnalysisModel: hold and provide access to the FE_Element and DOF_Group objects
class AnalysisModel:
    START_EQN_NUM = 0
    START_VERTEX_NUM = 0

    def __init__(self):

        self.FEs = {}
        self.DOFs = {}
        
        self.domain = None
        self.handler = None

        self.DOF_graph = None      # 两者有什么区别？？？？？？？？一个是优化，一个没优化
        self.group_graph = None

        self.num_FE_Ele = 0         # number of FE_Elements objects added
        self.num_DOF_Grp = 0        # number of DOF_Group objects added
        self.num_eqn = 0            # num_eqn set by the ConstraintHandler typically

    # methods to populate/depopulate the AnalysisModel
    def add_FE_element(self, FE_Ele):
        # check we don't add a null pointer or this is a subclass trying to use this method when it should'nt
        if FE_Ele is None or self.get_FEs == {}:
            return False
        # check if an Element with a similar tag already exists in the Domain
        tag = FE_Ele.get_tag()
        other = self.FEs.get(tag)
        if other is not None:
            print('AnalysisModel::add_FE_element - fe_element with tag '+str(tag)+' already exists in model.\n')
            return False
        # add 
        self.FEs[tag] = FE_Ele
        FE_Ele.set_analysis_model(self)
        self.num_FE_Ele += 1
        return True

    def add_DOF_group(self, theDOF_Grp):
        # check we don't add a null pointer or this is a subclass trying to use a method it should'nt be using
        if theDOF_Grp is None:
            return False
        
        # check if a DOF_Group with a similar tag already exists in the Model
        tag = theDOF_Grp.get_tag()
        other = self.DOFs.get(tag)
        if other is not None:
            print('AnalysisModel::add_DOF_group - dof_group with tag '+str(tag)+' already exists in model.\n')
            return False
        # add
        self.DOFs[tag] = theDOF_Grp
        self.num_DOF_Grp += 1
        return True


    def clear_all(self):
        self.FEs = {}
        self.DOFs = {}

        self.DOF_graph = None
        self.group_graph = None

        self.num_FE_Ele = 0
        self.num_DOF_Grp = 0
        self.num_eqn = 0
    
    def clear_DOF_graph(self):
        self.DOF_graph = None

    # def clearDOFGroupGraph(self):
    #     self.group_graph = None

    # methods to access the FE_Elements and DOF_Groups and their numbers
    def get_num_DOF_groups(self):
        return self.num_DOF_Grp

    def get_DOF_group(self, tag):
        return self.DOFs.get(tag)

    def get_FEs(self):
        return self.FEs
        
    def get_DOFs(self):
        return self.DOFs
    # methods to access the connectivity for SysOfEqn to size itself
    def set_num_eqn(self, theNumEqn):
        self.num_eqn = theNumEqn

    def get_num_eqn(self):
        return self.num_eqn

    def get_DOF_graph(self):
        if self.DOF_graph is None:
            numVertex = self.get_num_DOF_groups()
            graphStorage = {}
            self.DOF_graph = Graph(graphStorage)

            # create a vertex for each dof
            DOFs = self.get_DOFs()
            for tag in DOFs:
                dof = DOFs[tag]
                id1= dof.get_ID()
                size = len(id1)
                for i in range(0, size):
                    dofTag = id1[i]
                    if dofTag >= AnalysisModel.START_EQN_NUM:
                        vertex = self.DOF_graph.get_vertex(dofTag)
                        if vertex is None:
                            vertex = Vertex(dofTag, dofTag)
                            if self.DOF_graph.add_vertex(vertex, False) == False:
                                print('WARNING AnalysisModel::get_DOF_graph - error adding vertex.\n')
                                return self.DOF_graph
            # now add the edges, by looping over the FE_elements, getting their IDs and adding edges between DOFs for equation numbers >= START_EQN_NUM
            FEs = self.get_FEs()
            cnt = 0
            for tag in FEs:
                ele = FEs[tag]
                id1 = ele.get_ID()
                cnt += 1
                size = len(id1)
                for i in range(0, size):
                    eqn1 = id1[i]
                    # if eqnNum of DOF is a valid eqn number add an edge to all other DOFs with valid eqn numbers.
                    if eqn1 >= AnalysisModel.START_EQN_NUM:
                        for j in range(i+1, size):
                            eqn2 = id1[j]
                            if eqn2 >= AnalysisModel.START_EQN_NUM:
                                self.DOF_graph.add_edge(eqn1 - AnalysisModel.START_EQN_NUM + AnalysisModel.START_VERTEX_NUM,
                                eqn2 - AnalysisModel.START_EQN_NUM + AnalysisModel.START_VERTEX_NUM)
        return self.DOF_graph
 
    # def getDOFGroupGraph(self):
    #     # 和 get_DOF_graph() 有什么区别？
    #     # DOFGraph ：number后（去除约束后）的节点里面的自由度（DOF），变成Vertex
    #     # DOFGroupGraph：所有节点（DOFGroup），变成Vertex
    #     if self.group_graph is None:
    #         numVertex = self.get_num_DOF_groups()
    #         if numVertex == 0:
    #             print('WARNING AnalysisMode::getDOFGroupGraph - 0 vertices, has the Domain been populated?\n')
    #             # exit(self, -1)
    #         graphStorage = {}
    #         self.group_graph = Graph(graphStorage) # 重点！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！
    #         # now create the vertices with a reference equal to the DOF_Group number.
    #         # and a tag which ranges from 0 through numVertex-1
    #         DOFs = self.get_DOFs()
    #         count = AnalysisModel.START_VERTEX_NUM
    #         for dof in DOFs:
    #             DOF_GroupTag = dof.get_tag()
    #             DOF_GroupNodeTag = dof.getNodeTag()
    #             numDOF = dof.getNumFreeDOF()
    #             vertex = Vertex(DOF_GroupTag, DOF_GroupNodeTag, 0, numDOF)
    #             self.group_graph.addVertex(vertex)
    #         # now add the edges, by looping over the Elements, getting their
    #         # IDs and adding edges between DOFs for equation numbers >= START_EQN_NUM
    #         FEs = self.get_FEs()
    #         for ele in FEs:
    #             id1 = ele.getDOFtags()
    #             size = id1.Size()
    #             for i in range(0, size):
    #                 dof1 = id1[i]
    #                 for j in range(0, size):
    #                     if i != j:
    #                         dof2 = id1[j]
    #                         self.group_graph.addEdge(dof1, dof2)
    #     return self.group_graph
    
    # methods to update the response quantities at the DOF_Groups,
    # which in turn set the new nodal trial response quantities
    def set_response(self, disp, vel, accel):
        # all is Vector
        DOFgrps = self.get_DOFs()
        for dof in DOFgrps:
            dof.set_node_disp(disp)
            dof.set_node_vel(vel)
            dof.set_node_accel(accel)

    def set_disp(self, disp):
        DOFgrps = self.get_DOFs()
        for dof in DOFgrps:
            dof.set_node_disp(disp)

    # def setVel(self, vel):
    #     DOFgrps = self.get_DOFs()
    #     for dof in DOFgrps:
    #         dof.setNodeVel(vel)
    #
    # def setAccel(self, accel):
    #     DOFgrps = self.get_DOFs()
    #     for dof in DOFgrps:
    #         dof.setNodeAccel(accel)

    def incr_disp(self, disp):
        # disp 是 Vector
        DOFgrps = self.get_DOFs()
        for tag in DOFgrps:
            dof = DOFgrps[tag]
            dof.incr_node_disp(disp)

    # def incrVel(self, vel):
    #     DOFgrps = self.get_DOFs()
    #     for dof in DOFgrps:
    #         dof.incrNodeVel(vel)
    #
    # def incrAccel(self, accel):
    #     DOFgrps = self.get_DOFs()
    #     for dof in DOFgrps:
    #         dof.incrNodeAccel(accel)
    
    # methods added to store the eigenvalues and vectors in the domain
    # def setNumEigenvectors(self, numEigenvectors):
    #     pass
    # def setEigenvector(self, mode, eigenvalue):
    #     pass
    # def setEigenvalues(self, eigenvalue):
    #     pass
    # def getEigenvalues(self):
    #     pass
    # def getModelDampingFactors(self):
    #     pass
    # def inclModalDampingMatrix(self):
    #     pass
    
    # methods which trigger operations in the Domain
    def set_links(self, theDomain, theHandler):
        self.domain = theDomain
        self.handler = theHandler

    def apply_load_domain(self, pseudoTime):
        # check to see there is a Domain linked to the Model
        if self.domain is None:
            print('WARNING: AnalysisModel::apply_load_domain - No Domain linked.\n')
            return None
        
        self.domain.apply_load(pseudoTime)
        self.handler.apply_load()

    def update_domain(self): # 有重载
        # check to see there is a Domain linked to the Model
        if self.domain is None:
            print('WARNING: AnalysisModel::update_domain. No Domain linked.\n')
            return -1
        
        res = self.domain.update()
        if res == 0:
            return self.handler.update()
        return res

    # def update_domain(self, newTime, dT):
    #     pass

    def analysis_step(self, dT=0.0):
        # check to see there is a Domain linked to the Model
        if self.domain is None:
            print('WARNING: AnalysisModel::newStep. No domain linked.\n')
            return -1
        # invoke the method
        return self.domain.analysis_step(dT)

    # def eigenAnalysis(self, numMode, generalized, findSmallest):
    #     pass

    def commit_domain(self):
        # check to see there is a Domain linked to the Model
        if self.domain is None:
            print('WARNING: AnalysisModel::commit_domain. No Domain linked.\n')
            return -1
        # invoke the method
        if self.domain.commit() < 0:
            print('WARNING: AnalysisModel::commit_domain - Domain::commit() failed.\n')
            return -2
        return 0

    def revert_domain_to_last_commit(self):
        if self.domain is None:
            print('WARNING: AnalysisModel::revert_domain_to_last_commit. No Domain linked.\n')
            return -1
        if self.domain.revert_to_last_commit() < 0:
            print('WARNING: AnalysisModel::revert_domain_to_last_commit. Domain::revertToLastCommit() failed.\n')
            return -2
        return 0

    def get_current_domain_time(self):
        # check to see there is a Domain linked to the Model
        if self.domain is None:
            print('WARNING: AnalysisModel::get_current_domain_time - No Domain linked.\n')
            return None
        return self.domain.get_current_time()

    def set_current_domain_time(self, newTime):
        if self.domain is None:
            print('WARNING: AnalysisModel::get_current_domain_time. No Domain linked.\n')
            return -1
        return self.domain.get_current_time()

    # def setRayleighDampingFactors(self, alphaM, betaK, betaKi, betaKc):
    #     pass

    def get_domain(self):
        return self.domain
    
    
    
    
        

        
