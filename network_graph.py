"""
network_graph

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
import networkx as nx


class NetworkGraph:
    """
    NetworkGraph uses the networkx module to create a GraphML representation of the CMAP graph
    """
    def __init__(self, cmap):
        """
        :param cmap is a graph structure build from the CMAP CXL format
        """
        self.g = nx.DiGraph()               # this is a directed graph
        self.cmap = cmap                    # this graph is built from the cmap graph
        self._add_nodes()
        self.node_count = self.g.number_of_nodes()
        self._add_edges()
        self.edge_count = self.g.number_of_edges()

    def _add_nodes(self):
        """
        add the cmap nodes to the GraphML version of the graph
        """
        node_number = 0
        for id, v in self.cmap.vertexes.items():
            node_number += 1
            print("network_graph: " + v.label)
            if hasattr(v, "varName"):
                print("Found varName " + v.varName + " Label " + v.label)
                self.g.add_node(id, id=id, name=v.varName, type=v.type, description=v.label, color=v.color)
            elif hasattr(v, "cond"):
                print("Condition Label" + v.cond + " " + v.type + "  Label " + v.label)
                self.g.add_node(id, id=id, name=v.label, type=v.type, description=v.cond, color=v.color)
            elif hasattr(v, "default"):
                print("Default label " + v.default + " " + v.type + " Label " + v.label)
                self.g.add_node(id, id=id, name=v.default, type=v.type, description=v.label, color=v.color)
            else:
                self.g.add_node(id, id=id, name=v.label, type=v.type, description=v.label, color=v.color)

    def _add_edges(self):
        """
        add the cmap edges to the GraphML version of the graph
        """
        for id, v in self.cmap.vertexes.items():
            for s in v.source:
                self.g.add_edge(s[0].id, id, description=s[1])
            for t in v.target:
                self.g.add_edge(id, t[0].id, description=t[1])

    def save_graphml(self, file_name):
        """
        save the GraphML version of the graph to the
        :param file_name
        """
        nx.write_graphml(self.g, file_name)
