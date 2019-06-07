
class Graph(object):
    START_VERTEX_NUM = 0

    def __init__(self, theVerticesStorage):
        # theVerticesStorage is TaggedObjectStorage , usually MapOfTaggedObjects/{}
        self.vertices = theVerticesStorage
        self.num_edge = 0
        self.next_free_tag = Graph.START_VERTEX_NUM

        for key in self.vertices:
            theObject = self.vertices.get(key)
            if theObject.get_tag() > self.next_free_tag:
                self.next_free_tag = theObject.get_tag() + 1


    def add_vertex(self, vertex, checkAdjacency=True):
        # check the vertex and its adjacency list
        # 略
        self.vertices[vertex.get_tag()] = vertex
        if vertex.get_tag() >= self.next_free_tag:
            self.next_free_tag = self.next_free_tag + 1
    
    def add_edge(self, vertexTag, otherVertexTag):
        # get pointers to the vertices, if one does not exist return
        vertex1 = self.get_vertex(vertexTag)
        vertex2 = self.get_vertex(otherVertexTag)
        if vertex1 is None or vertex2 is None:
            print('WARNING Graph::add_edge() - one or both of the vertices '+str(vertexTag)+' '+str(otherVertexTag)+' not in Graph.\n')
            return -1
        # add an edge to each vertex
        result = vertex1.add_edge(otherVertexTag)
        if result == 1:
            return 0 # already there
        elif result == 0: # added to vertexTag now add to other
            result=vertex2.add_edge(vertexTag)
            if result == 0:
                self.num_edge += 1
            else:
                print('WARNING Graph::add_edge() - '+str(vertexTag)+' added to '+str(otherVertexTag)+
                ' adjacency - but already there in otherVertexTag!.\n')
                return -2
        else:
            print('WARNING Graph::add_edge() - '+str(vertexTag)+' added to '+str(otherVertexTag)+
            ' adjacency - but not vica versa!.\n')
            return -2
        return result

    def get_vertex(self, vertexTag):
        res = self.vertices.get(vertexTag)
        return res
    
    def get_vertices(self):
        return self.vertices
    
    def get_num_vertex(self):
        return len(self.vertices)
    
    def get_num_edge(self):
        return self.num_edge

    def get_free_tag(self):
        return self.next_free_tag

    def remove_vertex(self, tag, removeEdgeFlag = True):
        result = self.vertices.pop(tag)
        if result == 0:
            return 0
        if removeEdgeFlag == True:
            # remove all edges associated with the vertex
            print('Graph::remove_vertex(int tag, bool flag = true) - no code to remove edges yet.\n')
        return result
    
    # def merge(self, other):
    #     # other is Graph
    #     pass
    
    


    
