"""
vertex

The MIT License (MIT)

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

class Vertex:
    """ a Vertex is a node in the CMAP graph that has related source and target nodes """
    def __init__(self, id, label, color="#0000FF", type=None, parent_id=None, **kwargs):
        """
        :param id: concept identifier string from the CMAP CXL file
        :param label: concept label string from the CMAP CXL file
        :param type: concept type assigned by the ConceptType class; currently a string, but will be changed to an object
        :param parent_id: CMAP CXL parent id means this is in a bundle - typically of attributes or keys
        """
        self.source = []
        self.target = []
        self.id = id
        self.label = label
        self.type = type
        self.parent_id = parent_id
        self.color = color
        self.is_root = False
        self.ct_subset = None
        for key, value in kwargs.items():
            setattr(self, key, value)
            s = key		
            assert isinstance(value, object)
            setattr(self, key, value)
            """self.label = value """
            if s == "varName":
                newLab = value + "-" + self.label
                self.label = newLab
                print("vertex: Set label to Varname")
            elif s == "cond":
                newLab = self.label + "-" + value
                #self.label = newLab
                print("vertex: Set label to condition ")
            elif s == "default":
                newLab = self.label + "(D++)" + value
                self.label = newLab
                print("vertex: Set default tag on label.")
            else:
                print("vertex: Key " + s)

    def add_source(self, node, relationship):
        """
        add a Vertex node as a source of this Vertex object
        :param node: a Vertex object representing a graph node that is added as a source to this object (node)
        :param relationship: string describing the relationship of the source node to this object (node)
        """
        if isinstance(node, Vertex):
            self.source.append((node, relationship))
        else:
            self._print_node_type_error(node)

    def add_target(self, node, relationship):
        """
        add a Vertex node as a target of this Vertex object
        :param node: a Vertex object representing a graph node that is added as a target from this object (node)
        :param relationship: string describing the relationship of this object (node) to the target node
        """
        if isinstance(node, Vertex):
            self.target.append((node, relationship))
        else:
            self._print_node_type_error(node)

    def add_ct_subset(self, subset):
        self.ct_subset = subset

    def _print_node_type_error(self, node):
        """
        the node requested to be added as a source or target of this Vertex is not a Vertex object
        :param node: node of unknown type; not of type Vertex as expected
        """
        raise ValueError(f"Unknown node type {type(node)} when adding a source or target in Vertex {self.id}")