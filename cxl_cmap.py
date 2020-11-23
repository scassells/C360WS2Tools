"""
cxl_map

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
import xml.etree.ElementTree as ET
import vertex as V
from collections import namedtuple
import concept_type as TYPE
import subset as SUB

"""
Rules:
- skip "-" and "--" labeled concepts
- ???? labeled concepts are attribute bundles
"""

DEFAULT_NS = {"cxl": "http://cmap.ihmc.us/xml/cmap/"}
Connection = namedtuple("Connection", "id from_id to_id")

class CxlCmap:
    """
    parse the CMAP CXL file and create a graph from the nodes and relationships
    """
    def __init__(self, config):
        """
        :param config: a configuration object that provides access to the program's config setting
        """
        self.cxl_file = config.data_file                           # CXL CMAP export to parse
        self.skip_concepts = config.config["skip_concept_labels"]  # list of concepts in the CMAP that are not used and skipped
        self.config = config                                       # configuration object
        self.vertexes = {}                                         # concepts represented as a node in a graph
        self.linking_phrase = {}
        self.keys = {}                                             # legend keys - not part of the graph
        self.connection = {}
        self.concepts = []
        self.iter_count = 0
        self.cxl_root = None
        self.key_id = None

    def load(self):
        """
        parse the CMAP CXL file and create a graph from the concepts and relationships
        :return: a list of concept ids
        """
        cxl_tree = self._parse_cxl_file()
        cxl_root = self._load_root(cxl_tree)
        map_elem = self._get_map_elem(cxl_root)
        self._set_key_id(map_elem)
        self.concepts = self._load_concepts(map_elem)
        self._add_node_types(map_elem)
        self._load_parent_edges()
        self._load_linking_phrases(map_elem)
        self._load_connection_edges(map_elem)
        self._add_connections()                                    # add source and targets to vertexes
        return self.concepts

    def __iter__(self):
        """
        create an interator to iterate over the vertexes in the CMAP graph
        """
        return self

    def __next__(self):
        """
        iterator that gets the next Vertex object in the vertex dictionary using the concepts list as keys
        :return: a Vertex object
        """
        if self.iter_count >= len(self.vertexes.keys()):
            raise StopIteration
        node = self.vertexes[self.concepts[self.iter_count]]
        self.iter_count += 1
        return node

    def _load_connection_edges(self, map_elem):
        """
        load all the connections in the connection dictionary as Connection named tuples
        :param map_elem: a CXL map element used to find all the connections
        """
        for c in map_elem.findall("./cxl:connection-list/cxl:connection", DEFAULT_NS):
            connect = Connection(c.get("id"), c.get("from-id"), c.get("to-id"))
            self.connection[c.get("from-id") + "." + c.get("to-id")] = connect

    def _add_connections(self):
        """
        add the connections as source and target nodes for nodes in the graph with the associated linking phrase
        """
        for connect_ids, connection in self.connection.items():
            from_id, to_id = connect_ids.split(".")
            if from_id in self.vertexes and to_id in self.vertexes:
                # case of dotted line direct connection
                # TODO - not sure what this line means - how do we intpret it
                pass
            elif from_id in self.vertexes:
                # normal case where there's a directed association
                from_node = self.vertexes[from_id]
                to_node = self._get_connected_to_node(to_id)
                from_node.add_target(to_node, self.linking_phrase[to_id])
                to_node.add_source(from_node, self.linking_phrase[to_id])
            elif to_id in self.vertexes:
                # hack to account for the fact that nodes have one To link, and the link_phrase may have multiple links
                from_node = self._get_connected_from_node(from_id)
                to_node = self.vertexes[to_id]
                from_node.add_target(to_node, self.linking_phrase[from_id])
                to_node.add_source(from_node, self.linking_phrase[from_id])
            else:
                raise ValueError(f"ID not in to_id or from_id: {from_node.label} to node {to_node.label} with link: {self.linking_phrase[from_id]}")

    def _get_connected_from_node(self, from_id):
        return [self.vertexes[connection.from_id] for connection in self.connection.values() if connection.to_id == from_id][0]

    def _get_connected_to_node(self, to_id):
        return [self.vertexes[connection.to_id] for connection in self.connection.values() if connection.from_id == to_id][0]

    def _get_connected_from_link(self, from_id, to_id):
        from_link = None
        for connect_ids, connection  in self.connection.items():
            if connection.to_id == to_id and connection.from_id == from_id:
                from_link = self.linking_phrase[connection.from_id]
                break;
        return from_link

    def _load_linking_phrases(self, map_elem):
        """
        load the linking phrases in the CMAP CXL file for each given relationship between concepts
        :param map_elem: the CMAP CXL file map element
        """
        for link in map_elem.findall("./cxl:linking-phrase-list/cxl:linking-phrase", DEFAULT_NS):
            self.linking_phrase[link.get("id")] = link.get("label")

    def _load_parent_edges(self):
        """
        if a parent id exists add the source and target nodes - assumes "has attribute" linking phrase should be used
        """
        for id, v in self.vertexes.items():
            if v.parent_id:
                v.add_source(self.vertexes[v.parent_id], "has attribute") # add parent vertex as source
                self.vertexes[v.parent_id].add_target(v, "has attribute") # add vertex as target of parent

    def _add_node_types(self, map_elem):
        """
        assign the content type as determined by a ContentType object for each vertex; identify the root concept
        :param map_elem: the map element in the CMAP CXL file
        """
        for id, v in self.vertexes.items():
            c_type = TYPE.ConceptType(id, map_elem, self.config)
            v.type = c_type.type
            v.color = c_type.color
            if c_type.is_root_node():
                v.is_root = True

    def _load_concepts(self, map_elem):
        """
        create Vertex objects from each concept found in the CMAP except those with labels in the skip list
        :param map_elem: a CXL map element used to find all the concepts in the CMAP
        """
        concepts = []
        for c in map_elem.findall("./cxl:concept-list/cxl:concept", DEFAULT_NS):
            label = c.get("label")
            is_key = self._is_a_key(c)
            if is_key:
                self.keys[c.get("id")] = label
            elif label not in self.skip_concepts:
                concepts.append(c.get("id"))
                attrs = self._get_additional_attributes(c)
                node = V.Vertex(c.get("id"), label.replace('\n', ''), parent_id=c.get("parent-id"), **attrs)
                self.vertexes[c.get("id")] = node
                self._add_codelist_subset(c, node)
        return concepts

    def _get_additional_attributes(self, concept):
        """
        additional attributes are formatted as newline delimitted json in the concept short-comment
        :param concept: concept element from CMAP cxl file
        :return: dictionary with attribute name value pairs
        """
        kwargs = {}
        attrs = concept.get("short-comment", "")
        if not attrs:
            return kwargs
        for key_value in attrs.split("\n"):
            pair = key_value.split(":")
            if len(pair) > 1:
                kwargs[pair[0]] = pair[1].strip()
                print("Short commment " + pair[1].strip())
            else:
                print("short comment: " + key_value)
        return kwargs

    def _add_codelist_subset(self, concept, node):
        """
        for cmap nodes with CT subsets (e.g. CDs) create a subset and add it to the node
        :param concept: CMAP concept element
        :param node: node, or vertex, in the internal graph
        """
        subset_terms = concept.get("long-comment", "")
        if not subset_terms:
            return              # no subset to add to the node
        # example long-comment on CD node: SITTING (C62122) default; SUPINE (C62167); STANDING (C62166)
        llist = node.label.split("(")
        if len(llist) > 1:
            cl_subset = SUB.Subset(c_code=node.label.split("(")[1].strip()[:-1], name=node.label.split("(")[0].strip())
            for term_value in subset_terms.split(";"):
                parts = self._parse_cd_subset(term_value)
                cl_subset.add_term(c_code=parts[1], sub_val=parts[0], default=parts[2])
                node.add_ct_subset(cl_subset)

    def _parse_cd_subset(self, term_value):
        subset = []
        parts = term_value.strip().split("(")
        subset.append(parts[0].strip())
        subset.append(parts[1].strip().split(")")[0])
        if "default" in parts[1].lower():
            subset.append("Yes")
        else:
            subset.append("No")
        return subset

    def _is_a_key(self, c):
        # TODO assumption that keys are stable in config and can just skip them - can we remove key?
        is_key = False
        if c.get("label") == "????":
            is_key = True
        elif self.key_id and c.get("parent-id") == self.key_id:
            is_key = True
        return is_key

    def _set_key_id(self, map_elem):
        """
        Sets key_id which is the Key Concept that is the parent of the individual keys. This assumes there is only
        one container box in the CMAP
        :param map_elem: the map element in the CMAP CXL file
        """
        for c in map_elem.findall("./cxl:concept-list/cxl:concept[@label='????']", DEFAULT_NS):
            self.key_id = c.get("id")

    @staticmethod
    def _get_name_ccode_from_label(label):
        """
        takes a CMAP concept label and creates separate name a c-code values in a named tuple
        value in a named tuple
        :param label: CD or DEC concept label formatted as "concept name (c-code)"
        :return: named tuple with name and c_code components
        """

    @staticmethod
    def _load_root(cxl_tree):
        return cxl_tree.getroot()

    @staticmethod
    def _get_map_elem(cxl_root):
        return cxl_root.find("cxl:map", DEFAULT_NS)

    def _parse_cxl_file(self):
        ET.register_namespace('cxl', "http://cmap.ihmc.us/xml/cmap/")
        return ET.parse(self.cxl_file)
