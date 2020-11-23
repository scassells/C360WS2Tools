"""
concept_type

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
ConceptType identifies the type of a given concept. This class will be refactored once a Concept Model has been created.
The means of identifying a type in the CMAP (e.g. border_color, background_color, border_shape, etc) will be linked
to the Concept Model. This class could help with conformance checking by reporting unknown concept types.
"""
DEFAULT_NS = {"cxl": "http://cmap.ihmc.us/xml/cmap/"}

class ConceptType:
    def __init__(self, concept_id, map_element, config):
        """
        constructor
        :param concept_id:  the CXL XML concept id used to lookup the associated concept-appearance element
        :param map_element: the CXL XML export map element, as parsed by xml.etree.ElementTree, used to lookup the
        concept appearance which in turn is used to determine the concept type
        :param config: a configuration object with program configuration data
        """
        self.id = concept_id
        self.map_elem = map_element
        self.cfg = config
        self.node_type = self._set_concept_type()
        self.type = self.node_type.label
        self.color = self.node_type.node_color

    def is_root_node(self):
        """
        :return: returns a boolean indicataing if a node is the root node
        """
        return True if self.node_type.is_root_concept() else False

    def _set_concept_type(self):
        """
        identifies and assigns the concept type; in the future Types will be identified by a Concept Model; after
        the Concept Model has been created the strings will be replaced with type objects
        :return: string indicating concept type that is determined by appearance
        """
        c = self.map_elem.find("cxl:concept-appearance-list/cxl:concept-appearance/[@id='" + self.id + "']", DEFAULT_NS)
        border_shape = c.get("border-shape", None)
        background_color = c.get("background-color", None)
        border_color = c.get("border-color", None)
        node_type = self.cfg.get_concept_type(background_color, border_color, border_shape)
        return node_type
