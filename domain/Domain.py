from opensees import OPS_Globals

class Domain(object):

    def __init__(self):

        OPS_Globals.ops_dt = 0.0

        self.elements = {}
        self.nodes    = {}
        self.SPs      = {}
        self.loadpatterns = {}

        self.current_time = 0.0     # current pseudo time
        self.committed_time = 0.0   # the committed pseudo time
        self.dT = 0.0              # difference between committed and current time
        self.commit_tag = 0

        self.current_Geo_tag = 0                 # an integer used mark if domain has changed
        self.has_domain_changed_flag = False      # a bool flag used to indicate if GeoTag needs to be ++
        # self.lastGeoSendTag = -1               # the value of current_Geo_tag when sendSelf was last invoked

        self.node_graph_built_flag = False
        self.ele_graph_built_flag = False

        self.bounds = [0, 0, 0, 0, 0, 0]
        # x min, y min, z min ,x max, y max, z max

    # methods to populate a domain (add components to a domain)
    def add_node(self, node):
        node_tag = node.get_tag()
        other = self.nodes.get(node_tag)
        if other is not None:
            print('node with tag '+str(node_tag)+' already exist in domain./n' )
            return False
        
        self.nodes[node_tag] = node
        node.set_domain(self)
        self.domain_change()
        # see if the physical bounds are changed
        # note this assumes 0,0,0,0,0,0 as startup min,max values
        crds = node.get_crds()
        dim = len(crds)
        if dim >= 1:
            x = crds[0]
            if x < self.bounds[0]:
                self.bounds[0] = x
            if x > self.bounds[3]:
                self.bounds[3] = x
        if dim >= 2:
            y = crds[1]
            if y < self.bounds[1]:
                self.bounds[1] = y
            if y > self.bounds[4]:
                self.bounds[4] = y
        if dim >= 3:
            z = crds[2]
            if z < self.bounds[2]:
                self.bounds[2] = z
            if z > self.bounds[5]:
                self.bounds[5] = z


    def add_element(self, element):
        eleTag = element.get_tag()
        # check all the element nodes exists in the domain
        nodes = element.get_external_nodes()
        numDOF = 0
        for i in range(0, len(nodes)):
            nodeTag = nodes[i]
            node = self.get_node(nodeTag)
            if node is None:
                print('WARNING Domain::add_element - In element '+str(eleTag))
                print('\n no Node '+str(nodes[i])+' exists in the domain.\n')
                return False
            numDOF += node.get_number_DOF()
        # check if an Element with a similar tag already exists in the Domain
        other = self.elements.get(eleTag)
        if other is not None:
            print('Domain::add_element - element with tag '+str(eleTag)+' already exist in domain./n')
            return False
        # add
        self.elements[eleTag] = element

        element.set_domain(self)
        element.update()
        # finally check the ele has correct number of dof
        if numDOF != element.get_num_DOF():
            print('Domain::add_element - element '+str(eleTag)+' - #DOF does not match with number at nodes.\n')
            self.elements.pop(eleTag)
            return False
        # mark the Domain as having been changed
        self.domain_change()


    def add_SP_constraint(self, sp_constraint):
        nodeTag = sp_constraint.get_node_tag()
        dof = sp_constraint.get_DOF_number()

        # check node exists in the domain
        if self.nodes[nodeTag] is None:
            print('Domain::add_SP_Constraint - cannot add as node with tag ')
            print(str(nodeTag)+' dose not exist in the domain.\n')

        # check that the DOF specified exists at the Node
        node = self.get_node(nodeTag)
        numDOF = node.get_number_DOF()
        if numDOF < dof :
            print('Domain::add_SP_Constraint - cannnot add as node with tag '+str(nodeTag))
            print(' does not have associated constrainted DOF.\n')

        # check if an exsiting SP_Constraint exists for that dof at the node
        found = False
        for tag in self.SPs:
            sp = self.SPs[tag]
            spNodeTag = sp.get_node_tag()
            spDof = sp.get_DOF_number()
            if (nodeTag == spNodeTag & dof == spDof):
                found = True
        if found is True:
            print('Domain::add_SP_constraint - cannot add as node already constrained in that dof by existing SP_Constraint.\n')
            
        # check that no other object with similar tag exists in model
        tag = sp_constraint.get_tag()
        if self.SPs.get(tag) is not None:
            print('Domain::add_SP_Constraint - cannot add as constraint with tag ')
            print(str(tag)+' already exists in the domain.\n')
        else:
            self.SPs[tag] = sp_constraint
            sp_constraint.set_domain(self)


    def add_load_pattern(self, loadpattern):
        # first check if a load pattern with a similar tag exists in model
        tag = loadpattern.get_tag()
        other = self.loadpatterns.get(tag)
        if other is not None:
            print('Domain::add_load_pattern - cannot add as LoadPattern with tag'+str(tag)+' already exists in model.\n')
            return False
        # now we add the load pattern to the container for load pattrens
        self.loadpatterns[tag] = loadpattern
        loadpattern.set_domain(self)
        self.domain_change()

    # methods to add components to a LoadPattern object
    def add_nodal_load(self, load, pattern):
        # pattern(int) 是 loadPattern对象的tag!
        node_tag = load.get_node_tag()
        res = self.get_node(node_tag)
        if res is None:
            print('Domain::add_nodal_load() - no node with tag '+str(node_tag)+' exists in the model.')
            print('Not adding the nodal load.')
        # now add it to the pattern
        pattern = self.loadpatterns[pattern]
        if pattern is None:
            print('Domain::add_nodal_load() - no pattern with tag '+str(pattern)+' exists in the model.')
            print('Not adding the nodal load.')
        pattern.add_nodal_load(load)
        load.set_domain(self)


    # methods to remove the components

    # def removeSP_Constraint(self, loadPattern):

    # methods to access the components of a domain
    def get_elements(self):
        return self.elements
    def get_nodes(self):
        return self.nodes
    def get_SPs(self):
        return self.SPs
    def get_load_patterns(self):
        return self.loadpatterns
    def get_domain_and_loadpattern_SPs(self):
        allSPs = []
        for tag in self.SPs:
            sp = self.SPs[tag]
            allSPs.append(sp)

        for key in self.loadpatterns:
            lp = self.loadpatterns[key]
            SPs = lp.get_SPs()
            for tag in SPs:
                sp = SPs[tag]
                allSPs.append(sp)
        return allSPs

    # def getParameters():
    #     pass
    def get_element(self, tag):
        return self.elements[tag]
    def get_node(self, tag):
        return self.nodes[tag]
    def get_SP_constraint(self, tag):
        return self.SPs[tag]
    # def getPressure_Constraint(self, tag):
    #     pass
    # def getMP_Constraint(self, tag):
    #     pass
    def get_loadpattern(self, tag):
        return self.loadpatterns[tag]

    # methods to query the state of the domain
    def get_current_time(self):
        return self.current_time
    # def getCommitTag(self):
    #     pass
    # def getNumElements(self):
    #     pass
    # def getNumNodes(self):
    #     pass
    # def getNumSPs(self):
    #     pass
    # def getNumPCs(self):
    #     pass
    # def getNumMPs(self):
    #     pass
    # def getNumLoadPatterns(self):
    #     pass
    
    # def getPysicalBounds(self):
    #     pass
    #     # vector
    # def getNodeResponse(self, nodeTag):
    #     pass
    #     # vector
    # def getElementResponse(self, eleTag):
    #     pass
        # vector
    

    # methods to get element and node graph
    # def getElmentGraph(self):
    #     pass
    # def getNodeGraph(self):
    #     pass
    # def clearElementGraph(self):
    #     pass
    # def clearNodeGraph(self):
    #     pass
    
    # methods to update the domain
    # def setCommitTag(self, newTag):
    #     pass
    # def setCurrentTime(self, newTime):
    #     pass
    # def setCommittedTime(self, newTime):
    #     pass
        
    def apply_load(self, timeStep):
        # set the pseudo time in the domain to be newTime
        self.current_time = timeStep
        self.dT = self.current_time - self.committed_time
        # first loop over nodes and elements getting them to first zero their loads
        for tag in self.nodes:
            node = self.nodes[tag]
            node.zero_unbalanced_load()
        for tag in self.elements:
            ele = self.elements[tag]
            # if(ele.isSubdomain()==False):
            ele.zero_load()
        # now loop over load patterns, invoking apply_load on them
        for tag in self.loadpatterns:
            loadPat = self.loadpatterns[tag]
            loadPat.apply_load(timeStep)
        # finally loop over the MP_Constraints and SP_Constraints of the domain
        # for tag, theMP in self._theMPs:
            # theMP.apply_constraint(timeStep)
        for tag in self.SPs:
            sp = self.SPs[tag]
            sp.apply_constraint(timeStep)
    
    # def setLoadConstant(self):
    #     pass
    # def unsetLoadConstant(self):
    #     pass
    # def initialize(self):
    #     pass
    # def setRayleighDampingFactors(self, alphaM, betaK, betaK0, betaKc):
    #     pass
    
    def commit(self):
        # first invoke commit on all nodes and elements in the domain
        nodes = self.get_nodes()
        for tag in nodes:
            node = nodes[tag]
            node.commit_state()

        eles = self.get_elements()
        for tag in eles:
            ele = eles[tag]
            ele.commit_state()

        # set the new committed time in the domain
        self.committed_time = self.current_time
        self.dT = 0.0

        # invoke record on all recorders
        # update the commit_tag
        self.commit_tag += 1
        return 0


    # def revertToLastCommit(self):
    #     # first invoke revertToLastCommit on all nodes and elements in the domain
    #     for tag in self.nodes:
    #         node = self.nodes[tag]
    #         node.revertToLastCommit()
    #     for tag in self.elements:
    #         ele = self.elements[tag]
    #         ele.revertToLastCommit()
    #     # set the current time and load factor in the domain to last commited
    #     self.current_time = self.committed_time
    #     self.dT = 0.0
    #     # apply load for the last committed time
    #     self.apply_load(self.current_time)
    #     return self.update()


    # def revertToStart(self):
    #     pass
    def update(self):
        ok = 0
        # invoke update on all the ele's
        eles = self.get_elements()
        for tag in eles:
            ele = eles[tag]
            ok += ele.update()
        if ok != 0:
            print('Domain::update - domain failed in update\n')
        return ok
    
    #
    # def analysis_step(self, dT): # ???
    #     return 0
    #
    # def eigenAnalysis(self, numMode, generalized, findSmallest):
    #     pass
        
    # methods for eigenvalue analysis
    # methods for other objects to determine if model has changed
    def has_domain_changed(self):
        # if the flag, indicating the domain has changed since the last call to this method, has changed
        # increment the integer and reset the flag
        if self.has_domain_changed_flag is True:
            self.current_Geo_tag += 1
            self.node_graph_built_flag = False
            self.ele_graph_built_flag = False
        # 复位
        self.has_domain_changed_flag = False
        # return the integer so user can determine if domain has changed since their last call to this method
        return self.current_Geo_tag

    def get_domain_change_flag(self):
        return self.has_domain_changed_flag

    def domain_change(self):
        self.has_domain_changed_flag = True

    def set_domain_change_stamp(self, newStamp):
        self.current_Geo_tag = newStamp
        
    # methods for output
    # nodal methods required in domain interface for parallel interpreter


    



      
