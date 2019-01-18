
class Domain(object):
    def __init__(self):
        self.theElements = {}
        self.theNodes    = {}
        self.theSPs      = {}
        self.theLoadPatterns = {}

        self.currentTime = 0.0     # current pseudo time
        self.committedTime = 0.0   # the committed pseudo time
        self.dT = 0.0              # difference between committed and current time

        self.currentGeoTag = 0                 # an integer used mark if domain has changed
        self.hasDomainChangedFlag = False      # a bool flag used to indicate if GeoTag needs to be ++
        self.lastGeoSendTag = -1               # the value of currentGeoTag when sendSelf was last invoked

        self.nodeGraphBuiltFlag = False 
        self.eleGraphBuiltFlag = False

        self.theBounds = [0, 0, 0, 0, 0, 0]
        # x min, y min, z min ,x max, y max, z max

    # methods to populate a domain (add components to a domain)
    def addNode(self, node):
        nodTag = node.getTag()
        other = self.theNodes.get(nodTag)
        if other is not None:
            print('node with tag '+str(nodTag)+' already exist in domain./n' )
            return False
        
        self.theNodes[nodTag] = node
        node.setDomain(self)
        self.domainChange()
        # see if the physical bounds are changed
        # note this assumes 0,0,0,0,0,0 as startup min,max values
        crds = node.getCrds()
        dim = len(crds)
        if dim >= 1:
            x = crds[0]
            if x < self.theBounds[0]:
                self.theBounds[0] = x
            if x > self.theBounds[3]:
                self.theBounds[3] = x
        if dim >= 2:
            y = crds[1]
            if y < self.theBounds[1]:
                self.theBounds[1] = y
            if y > self.theBounds[4]:
                self.theBounds[4] = y
        if dim >= 3:
            z = crds[2]
            if z < self.theBounds[2]:
                self.theBounds[2] = z
            if z > self.theBounds[5]:
                self.theBounds[5] = z


    def addElement(self, element):
        eleTag = element.getTag()
        # check all the element nodes exists in the domain
        nodes = element.getExternalNodes()
        numDOF = 0
        for i in range(0, len(nodes)):
            nodeTag = nodes[i]
            node = self.getNode(nodeTag)
            if node is None:
                print('WARNING Domain::addElement - In element '+str(eleTag))
                print('\n no Node '+str(nodes[i])+' exists in the domain.\n')
                return False
            numDOF += node.getNumberDOF()
        # check if an Element with a similar tag already exists in the Domain
        other = self.theElements.get(eleTag)
        if other is not None:
            print('Domain::addElement - element with tag '+str(eleTag)+' already exist in domain./n')
            return False
        # add
        self.theElements[eleTag] = element

        element.setDomain(self)
        element.update()
        # finally check the ele has correct number of dof
        if numDOF != element.getNumDOF():
            print('Domain::addElement - element '+str(eleTag)+' - #DOF does not match with number at nodes.\n')
            self.theElements.pop(eleTag)
            return False
        # mark the Domain as having been changed
        self.domainChange()


    def addSP_Constraint(self, spConstraint):
        nodeTag = spConstraint.getNodeTag()
        dof = spConstraint.getDOF_Number()

        # check node exists in the domain
        if self.theNodes[nodeTag] is None:
            print('Domain::addSP_Constraint - cannot add as node with tag ')
            print(str(nodeTag)+' dose not exist in the domain.\n')

        # check that the DOF specified exists at the Node
        node = self.getNode(nodeTag)
        numDOF = node.getNumberDOF()
        if numDOF < dof :
            print('Domain::addSP_Constraint - cannnot add as node with tag '+str(nodeTag))
            print(' does not have associated constrainted DOF.\n')

        # check if an exsiting SP_Constraint exists for that dof at the node
        found = False
        for tag in self.theSPs:
            sp = self.theSPs[tag]
            spNodeTag = sp.getNodeTag()
            spDof = sp.getDOF_Number()
            if(nodeTag == spNodeTag & dof == spDof):
                found = True
        if found == True:
            print('Domain::addSP_Constraint - cannot add as node already constrained in that dof by existing SP_Constraint.\n')
            
        # check that no other object with similar tag exists in model
        tag = spConstraint.getTag()
        if self.theSPs.get(tag) is not None:
            print('Domain::addSP_Constraint - cannot add as constraint with tag ')
            print(str(tag)+' already exists in the domain.\n')
        else:
            self.theSPs[tag] = spConstraint
            spConstraint.setDomain(self)


    def addLoadPattern(self, loadpattern):
        # first check if a load pattern with a similar tag exists in model
        tag = loadpattern.getTag()
        other = self.theLoadPatterns.get(tag)
        if other is not None:
            print('Domain::addLoadPattern - cannot add as LoadPattern with tag'+str(tag)+' already exists in model.\n')
            return False
        # now we add the load pattern to the container for load pattrens
        self.theLoadPatterns[tag] = loadpattern
        loadpattern.setDomain(self)
        self.domainChange()

    # methods to add components to a LoadPattern object
    def addNodalLoad(self, load, pattern):
        # pattern(int) 是 loadPattern对象的tag!
        nodTag = load.getNodeTag()
        res = self.getNode(nodTag)
        if res is None:
            print('Domain::addNodalLoad() - no node with tag '+str(nodTag)+' exists in the model.')
            print('Not adding the nodal load.')
        # now add it to the pattern
        thePattern = self.theLoadPatterns[pattern]
        if thePattern is None:
            print('Domain::addNodalLoad() - no pattern with tag '+str(pattern)+' exists in the model.')
            print('Not adding the nodal load.')
        thePattern.addNodalLoad(load)
        load.setDomain(self)


    # methods to remove the components

    # def removeSP_Constraint(self, loadPattern):

    # methods to access the components of a domain
    def getElements(self):
        return self.theElements
    def getNodes(self):
        return self.theNodes
    def getSPs(self):
        return self.theSPs
    def getLoadPatterns(self):
        return self.theLoadPatterns
    def getDomainAndLoadPatternSPs(self):
        allSPs = []
        for tag in self.theSPs:
            sp = self.theSPs[tag]
            allSPs.append(sp)

        for key in self.theLoadPatterns:
            lp = self.theLoadPatterns[key]
            theSPs = lp.getSPs()
            for tag in theSPs:
                sp = theSPs[tag]
                allSPs.append(sp)
        return allSPs

    # def getParameters():
    #     pass
    def getElement(self, tag):
        return self.theElements[tag]
    def getNode(self, tag):
        return self.theNodes[tag]
    def getSP_Constraint(self, tag):
        return self.theSPs[tag]
    # def getPressure_Constraint(self, tag):
    #     pass
    # def getMP_Constraint(self, tag):
    #     pass
    def getLoadPattern(self, tag):
        return self.theLoadPatterns[tag]

    # methods to query the state of the domain
    def getCurrentTime(self):
        return self.currentTime
    def getCommitTag(self):
        pass
    def getNumElements(self):
        pass
    def getNumNodes(self):
        pass
    def getNumSPs(self):
        pass
    def getNumPCs(self):
        pass
    def getNumMPs(self):
        pass
    def getNumLoadPatterns(self):
        pass
    
    def getPysicalBounds(self):
        pass
        # vector
    def getNodeResponse(self, nodeTag):
        pass
        # vector
    def getElementResponse(self, eleTag):
        pass
        # vector
    

    # methods to get element and node graph
    def getElmentGraph(self):
        pass
    def getNodeGraph(self):
        pass
    def clearElementGraph(self):
        pass
    def clearNodeGraph(self):
        pass
    
    # methods to update the domain
    def setCommitTag(self, newTag):
        pass
    def setCurrentTime(self, newTime):
        pass
    def setCommittedTime(self, newTime):
        pass
        
    def applyLoad(self, timeStep):
        # set the pseudo time in the domain to be newTime
        self.currentTime = timeStep
        self.dT = self.currentTime - self.committedTime
        # first loop over nodes and elements getting them to first zero their loads
        for tag in self.theNodes:
            node = self.theNodes[tag]
            node.zeroUnbalancedLoad()
        for tag in self.theElements:
            ele = self.theElements[tag]
            if(ele.isSubdomain()==False):
                ele.zeroLoad()
        # now loop over load patterns, invoking applyLoad on them
        for tag in self.theLoadPatterns:
            loadPat = self.theLoadPatterns[tag]
            loadPat.applyLoad(timeStep)
        # finally loop over the MP_Constraints and SP_Constraints of the domain
        # for tag, theMP in self._theMPs:
            # theMP.applyConstraint(timeStep)
        for tag in self.theSPs:
            theSP = self.theSPs[tag]
            theSP.applyConstraint(timeStep)
    
    def setLoadConstant(self):
        pass
    def unsetLoadConstant(self):
        pass
    def initialize(self):
        pass
    def setRayleighDampingFactors(self, alphaM, betaK, betaK0, betaKc):
        pass
    
    def commit(self):
        pass
    def revertToLastCommit(self):
        # first invoke revertToLastCommit on all nodes and elements in the domain
        for tag, node in self.theNodes:
            node.revertToLastCommit()
        for tag, ele in self.theElements:
            ele.revertToLastCommit()
        # set the current time and load factor in the domain to last commited
    def revertToStart(self):
        pass
    def update(self):
        pass
    

    def analysisStep(self, dT):
        return 0

    def eigenAnalysis(self, numMode, generalized, findSmallest):
        pass
        
    # methods for eigenvalue analysis
    # methods for other objects to determine if model has changed
    def hasDomainChanged(self):
        # if the flag, indicating the domain has changed since the last call to this method, has changed
        # increment the integer and reset the flag
        result = self.hasDomainChangedFlag
        if(result==True):
            self.currentGeoTag += 1
            self.nodeGraphBuiltFlag = False
            self.eleGraphBuiltFlag = False
        # 复位
        self.hasDomainChangedFlag = False
        # return the integer so user can determine if domain has changed since their last call to this method
        return self.currentGeoTag

    def getDomainChangeFlag(self):
        return self.hasDomainChangedFlag

    def domainChange(self):
        self.hasDomainChangedFlag = True

    def setDomainChangeStamp(self, newStamp):
        self.currentGeoTag = newStamp
        
    # methods for output
    # nodal methods required in domain interface for parallel interpreter


    



      
