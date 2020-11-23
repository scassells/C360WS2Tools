"""
node_type

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

"""
NodeType identifies the type of a node (or concept) found in a CMAP. In CMAPs node types are identified by visual
characteristics such as the background color, border color, or border shape. Each node has a name and a label,
in addition to the specific identifying characteristics for that node. The node types are created from the config file,
not from the individual key concepts found in the CMAPs.
"""
class NodeType:
    def __init__(self, name, label, node_color="#0000FF", source_links=[], target_links=[],
                 background_color=None, border_color=None, border_shape=None):
        self.name = name
        self.label = label
        self.border_color = border_color
        self.background_color = background_color
        self.border_shape = border_shape
        self.node_color = node_color
        self.valid_source_links = source_links
        self.valid_target_links = target_links

    def is_root_concept(self):
        """
        returns true when the node type is the root concept, or observation concept for BCs
        :return: boolean
        """
        if self.name == "root_concept":
            return True
        else:
            return False
