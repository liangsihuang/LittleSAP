from TaggedObject import TaggedObject
import numpy as np

MAX_NUM_DOF = 64

class FE_Element(TaggedObject):
    # static variables - single copy for all objects of the class	
    errMatrix = None # matrix
    errVector = None # vector
    theMatrices = None # array of pointers to 'class wide matrices'/ rank-2 narray
    theVectors = None # array of pointers to 'class wide vectors'/ narray
    num_FEs = 0  # number of objects

    def __init__(self, tag, ele):
        super().__init__(tag)
        self.DOF_groups = np.zeros(len(ele.get_external_nodes()), dtype=int)
        self.myID = np.zeros(ele.get_num_DOF(), dtype=int)
        self.num_DOF = ele.get_num_DOF()
        self.model = None
        self.ele = ele
        self.residual = None # vector
        self.tangent = None # matrix
        self.integrator = None # needed for subdomain???

        if self.num_DOF <= 0:
            print('FE_Element::FE_Element() - element must have 1 dof')
        
        # get element domain and check if it is valid
        domain = ele.get_domain()
        if domain is None:
            print('FE_Element::FE_Element() - element has no domain')
        # keep a pointer to all DOF_Groups
        num_group = ele.get_num_external_nodes() # int
        nodes = ele.get_external_nodes()  # int's list
        for i in range(0, num_group):
            node = domain.get_node(nodes[i])
            if node is None:
                print('FATAL FE_Element::FE_Element() - Node: '+str(nodes[i]))
                print('does not exist in the Domain\n')
            dofGrp = node.get_DOF_group()
            if dofGrp is not None:
                self.DOF_groups[i] = dofGrp.get_tag()
            else:
                print('FATAL FE_Element::FE_Element() - Node: ')
                print('has no DOF_Group associated with it\n')

        # if this is the first FE_Element we now
        # create the arrays used to store pointers to class wide
        # matrix and vector objects used to return tangent and residual
        if FE_Element.num_FEs == 0:
            FE_Element.theMatrices = []
            FE_Element.theVectors = []
        for i in range(0, MAX_NUM_DOF+1):
            FE_Element.theMatrices.append(None)
            FE_Element.theVectors.append(None)
        # if Elements are not subdomains, set up pointers to
        # objects to return tangent Matrix and residual Vector.
        if self.num_DOF <= MAX_NUM_DOF:
            # use class wide objects
            if FE_Element.theVectors[self.num_DOF] is None:
                FE_Element.theVectors[self.num_DOF] = np.zeros(self.num_DOF)
                FE_Element.theMatrices[self.num_DOF] = np.zeros((self.num_DOF,self.num_DOF))
                self.residual = FE_Element.theVectors[self.num_DOF]
                self.tangent = FE_Element.theMatrices[self.num_DOF]
            else:
                self.residual = FE_Element.theVectors[self.num_DOF]
                self.tangent = FE_Element.theMatrices[self.num_DOF]
        else:
            # create matrices and vectors for each object instance
            self.residual = np.zeros(self.num_DOF)
            self.tangent = np.zeros((self.num_DOF, self.num_DOF))

        FE_Element.num_FEs += 1

    # public methods for setting/obtaining mapping information
    def get_DOF_tags(self):
        return self.DOF_groups

    def get_ID(self):
        return self.myID

    def set_analysis_model(self, theAnalysisModel):
        self.model = theAnalysisModel

    def set_ID(self):
        current = 0
        if self.model is None:
            print('WARNING FE_Element::set_ID() - no AnalysisModel set.\n')
            return -1
        numGrps = len(self.DOF_groups)
        for i in range(0, numGrps):
            tag = self.DOF_groups[i]
            dof = self.model.get_DOF_group(tag)
            if dof is None:
                print('WARNING FE_Element::set_ID: 0 DOF_Group Pointer.\n')
                return -2
            DOFid = dof.get_ID()
            for j in range(0, len(DOFid)):
                if current < self.num_DOF:
                    self.myID[current] = DOFid[j]
                    current += 1
                else:
                    print('WARNING FE_Element::set_ID() - num_DOF and number of dof at the DOF_Groups.\n')
                    return -3
        return 0
    
    # methods to form and obtain the tangent and residual
    def get_tangent(self, theNewIntegrator):
        self.integrator = theNewIntegrator
        if self.ele is None:
            print('FATAL FE_Element::get_tangent() - no Element *given.\n')

        if theNewIntegrator is not None:
            theNewIntegrator.form_ele_tangent(self)
            return self.tangent


    def get_residual(self, theNewIntegrator):
        self.integrator = theNewIntegrator
        if self.integrator is None:
            return self.residual
        if self.ele is None:
            print('FATAL FE_Element::get_tangent() - no Element *given.\n')
        theNewIntegrator.form_ele_residual(self)
        return self.residual

    
    # methods to allow integrator to build tangent
    def zero_tangent(self):
        if self.ele is not None:
            self.tangent[:, :] = 0.0

    def add_Kt_to_tang(self, fact=1.0):
        if self.ele is not None:
            # check for a quick return	
            if fact == 0.0:
                return 
            else:
                self.tangent += self.ele.get_tangent_stiff() * fact

    def add_Ki_to_tang(self, fact=1.0):
        if self.ele is not None:
            # check for a quick return 
            if fact == 0.0:
                return 
            else:
                self.tangent += self.ele.getInitialStiff() * fact

    def add_kg_to_tang(self, fact=1.0):
        if self.ele is not None:
            # check for a quick return 
            if fact == 0.0:
                return 
            else:
                self.tangent += self.ele.getGeometricTangentStiff() * fact

    # def addCtoTang(self, fact=1.0):
    #     pass
    # def addMtoTang(self, fact=1.0):
    #     pass

    def add_Kp_to_tang(self, fact=1.0, numP=0):
        if self.ele is not None:
            # check for a quick return 
            if fact == 0.0:
                return 
            else:
                thePrevMat = self.ele.getPreviousK(numP)
                if thePrevMat is not None:
                    self.tangent += thePrevMat * fact

    def store_previous_K(self, numP):
        res = None
        if self.ele is not None:
            res = self.ele.store_previous_K(numP)
        return res
    
    # methods to allow integrator to build residual
    def zero_residual(self):
        if self.ele is not None:
                self.residual[:] = 0.0
        else:
            print('FATAL FE_Element::zero_residual() - no Element *given.\n')

    def add_R_to_residual(self, fact=1.0):
        if self.ele is not None:
            # check for a quick return 
            if fact == 0.0:
                return 
            eleResisting = self.ele.get_resisting_force()
            self.residual += (eleResisting * -1.0)
        else:
            print('FATAL FE_Element::add_R_to_residual() - no Element *given.\n')


    # def addRIncInertiaToResidual(self, fact=1.0):
    #     pass
    
    # methods for ele-by-ele strategies
    def get_tang_force(self, disp, fact=1.0):
        if self.ele is not None:
            # zero out the force vector
            self.residual[:] = 0.0
            # check for a quick return
            if fact == 0.0:
                return self.residual
            # get the component we need out of the vector and place in a temporary vector
            tmp = np.zeros(self.num_DOF)
            for i in range(0, self.num_DOF):
                dof = self.myID[i]
                if dof >= 0:
                    tmp[i] = disp[dof]
                else:
                    tmp[i] = 0.0
            # form the tangent again and then add the force
            self.integrator.formEleTangent(self)
            self.residual += self.tangent @ tmp * fact
            return self.residual
        else:
            print('WARNING FE_Element::addTangForce() - no Element *given.\n')
            return FE_Element.errVector

    def get_K_force(self, disp, fact=1.0):
        if self.ele is not None:
            self.residual[:] = 0.0
            if fact == 0.0:
                return self.residual
            tmp = np.zeros(self.num_DOF)
            for i in range(0, self.num_DOF):
                dof = self.myID[i]
                if dof >= 0:
                    tmp[i] = disp[dof]
                else:
                    tmp[i] = 0.0
            self.residual += self.ele.get_tangent_stiff() @ tmp * fact
            return self.residual
        else:
            print('WARNING FE_Element::getKForce() - no Element *given.\n')
            return FE_Element.errVector

    def get_Ki_force(self, disp, fact=1.0):
        if self.ele is not None:
            self.residual[:] = 0.0
            if fact == 0.0:
                return self.residual
            tmp = np.zeros(self.num_DOF)
            for i in range(0, self.num_DOF):
                dof = self.myID[i]
                if dof >= 0:
                    tmp[i] = disp[dof]
                else:
                    tmp[i] = 0.0
            self.residual += self.ele.getInitialStiff() @ tmp * fact
            return self.residual
        else:
            print('WARNING FE_Element::getKForce() - no Element *given.\n')
            return FE_Element.errVector



    # def getC_Force(self, x, fact=1.0):
    #     pass
    # def getM_Force(self, x, fact=1.0):
    #     pass
    #
    # def addM_Force(self, accel, fact=1.0):
    #     pass
    # def addD_Force(self, vel, fact=1.0):
    #     pass

    def add_K_force(self, disp, fact=1.0):
        if self.ele is not None:
            if fact == 0.0:
                return
            tmp = np.zeros(self.num_DOF)
            for i in range(0, self.num_DOF):
                loc = self.myID[i]
                if loc >= 0:
                    tmp[i] = disp[loc]
                else:
                    tmp[i] = 0.0
            self.residual += self.ele.get_tangent_stiff() @ tmp * fact
        else:
            print('WARNING FE_Element::add_K_force() - no Element *given.\n')

    def add_Kg_force(self, disp, fact=1.0):
        if self.ele is not None:
            if fact == 0.0:
                return
            tmp = np.zeros(self.num_DOF)
            for i in range(0, self.num_DOF):
                loc = self.myID[i]
                if loc >= 0:
                    tmp[i] = disp[loc]
                else:
                    tmp[i] = 0.0
            self.residual += self.ele.get_geometric_tangentStiff() @ tmp * fact # ???
        else:
            print('WARNING FE_Element::add_Kg_force() - no Element *given.\n')
    
    def update_element(self):
        if self.ele is not None:
            return self.ele.update()
        # else: =None 不用 print 吗？
        return 0

    def get_last_integrator(self):
        return self.integrator

    def get_last_response(self):
        if self.ele is not None:
            if self.integrator is not None:
                if self.integrator.get_last_response(self.residual, self.myID) < 0:
                    print('WARNING FE_Element::get_last_response(void) - the Integrator had problems with get_last_response().\n')
            else:
                self.residual[:] = 0.0
                print('WARNING  FE_Element::get_last_response() - No Integrator yet passed.\n')
            return self.residual
        else:
            print('WARNING  FE_Element::get_last_response() - No Element passed in constructor.\n')
            return FE_Element.errVector

    def get_element(self):
        return self.ele
    
    # protected:
    # def addLocalM_Force(self, accel, fact=1.0):
    #     pass
    # def addLocalD_Force(self, vel, fact=1.0):
    #     pass
        

    