"""
bc_factory

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
import bc
import os

class BCFactory:
    """ BCFactory creates a BC object using metadata extracted from the CMAP graph"""
    def __init__(self, cmap, config):
        """
        BCFactory constructor
        :param cmap: CMAP graph containing vertexes and edges used to generate BC content
        :param config: configuration object with config parameters
        """
        self.cmap = cmap
        self.cfg = config
        self.kwargs = {}
        self._node_types = {}
        self._qualifiers = {}
        self._get_node_types()

    def save_bc(self, bc):
        """
        serializes a BC object as JSON and writes it to a file
        :param bc: a BC object
        """
        json_bc = bc.serialize_json()
        file_name = os.path.join(self.cfg.data_path_dir, bc.name.replace(" ", "_") + ".json")
        with open(file_name, "w", encoding="utf-8") as fo:
            fo.write(json_bc)

    def create_bc(self):
        """
        use information in the graph created from the CMAP to create a BC object
        :return: a BC object
        """
        for node_name, vertex in self.cmap.vertexes.items():
            if vertex.is_root:
                self._set_name_c_code(vertex.label)
            elif vertex.type == self._node_types["dec"]:
                self._set_dec_attributes(vertex)
            # TODO process other vertex types as needed
        self.kwargs["qualifiers"] = self._qualifiers
        return bc.BiomedicalConcept(**self.kwargs)

    def _set_dec_attributes(self, vertex):
        """
        for data element concept (DEC) typed nodes set the BC attributes based on the role
        :param vertex: node object from the graph created using the CMAP
        """
        try:
            # TODO fix hard coded roles
            if vertex.role.lower() == "qualifier.variable.units":
                self._set_units(vertex)
            elif vertex.role.lower() == "qualifier.result":
                self._set_result(vertex)
            elif vertex.role.lower() == "topic":
                self._set_test_code(vertex)
            elif vertex.role.lower() == "qualifier.synonym.name":
                self._set_test_name(vertex)
            elif vertex.role.lower() == "qualifier.synonym.loinc":
                self._set_loinc_code(vertex)
            elif vertex.role.lower() == "qualifier.record" or vertex.role.lower() == "qualifier.variable" or \
                vertex.role.lower() == "qualifier.grouping":
                self._set_qualifier(vertex)
            else:
                #TODO check to see if it's an invalid role
                print(f"not processing role: {vertex.role}")
        except AttributeError:
            print(f"Concept {vertex.label} is missing the role attribute")

    def _set_qualifier(self, vertex):
        """
        for DECs with role qualifier set the BC attributes
        :param vertex: node object from the graph created using the CMAP
        """
        for node in vertex.target:
            if node[0].type == "Conceptual Domain":
                if node[0].ct_subset:
                    self._qualifiers[vertex.label] = self._set_qualifier_subset(node[0].ct_subset)
                else:
                    self._qualifiers[vertex.label] = node[0].label
                break

    def _set_qualifier_subset(self, subset):
        """
        return the name, c-code, and terms for a CT subset that defines a DEC CD (conceptual domain)
        :param subset: CT subset object that includes the list of terms
        :return: qualifier CT subset dictionary
        """
        qualifier_subset = {"name": subset.name, "c_code": subset.c_code}
        terms = []
        for term in subset.terms:
            term_label = term.label
            if term.is_default:
                term_label = term_label + " default"
            terms.append(term_label)
            qualifier_subset["terms"] = terms
        return qualifier_subset

    def _set_test_code(self, vertex):
        """
        sets the TESTCD and associated c-code for findings domain BCs; set to one value for the BC
        :param vertex: node object from the graph created using the CMAP
        """
        for node in vertex.target:
            if node[0].type == "Conceptual Domain":
                self.kwargs["test_cd"] = node[0].label.split("(")[0].strip()
                self.kwargs["test_c_code"] = node[0].label.split("(")[1].strip()[:-1]
                break

    def _set_test_name(self, vertex):
        """
        sets the test name for findings domain BCs; set to one value for the BC
        :param vertex: node object from the graph created using the CMAP
        """
        for node in vertex.target:
            if node[0].type == "Conceptual Domain":
                self.kwargs["test_name"] = node[0].label.split("(")[0].strip()
                break

    def _set_loinc_code(self, vertex):
        """
        sets the loinc code for findings domain BCs; set to one value for the BC
        :param vertex: node object from the graph created using the CMAP
        """
        for node in vertex.target:
            if node[0].type == "Conceptual Domain":
                self.kwargs["loinc"] = node[0].label.strip()
                break

    def _set_result(self, vertex):
        """
        sets the result type (e.g. Numeric) for a BC
        :param vertex: node object from the graph created using the CMAP
        """
        for node in vertex.target:
            if node[0].type == "Conceptual Domain":
                self.kwargs["result_type"] = node[0].label
                break

    def _set_units(self, vertex):
        """
        sets the valid units for a BC measurement
        :param vertex: node object from the graph created using the CMAP
        """
        for node in vertex.target:
            if node[0].type == "Conceptual Domain":
                self._set_unit_list(node[0].ct_subset)
                break

    def _set_unit_list(self, subset):
        """
        builds and sets the valid units for a BC measurement
        :param subset: CT subset object that includes the list of terms
        """
        if subset is None:
            return
        unit_list = []
        for term in subset.terms:
            unit_list.append(term.label)
            if term.is_default:
                self.kwargs["default_unit"] = term.label
        self.kwargs["unit_list"] = unit_list

    def _get_node_types(self):
        """
        loads the types of nodes that may be included in the graph generated from the CMAP
        """
        for type in self.cfg.node_types:
            self._node_types[type.name] = type.label

    def _set_name_c_code(self, label):
        """
        uses the observation concept, or root node, label from the CMAP graph to set the BC name, label, and c-code
        :param label: label from the root node, the observation concept node, in the CMAP
        """
        lsplit = label.split("(")
        if len(lsplit) > 1:
            self.kwargs["c_code"] = label.split("(")[1].strip()[:-1]
            self.kwargs["name"] = label.split("(")[0].strip().replace(" ", "_").lower()
            self.kwargs["label"] = label.split("(")[0].strip()