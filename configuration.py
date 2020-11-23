"""
configuration

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
import os
import json
import node_type as NT

CONFIG_FILE_NAME = "cmap_config.json"
DATA_PATH = os.path.dirname(os.path.realpath(__file__)) + '\\data'

class Configuration:
    """
    provides basic configuration information for the cxl_load application
    """
    def __init__(self, concept_name,  concept_file_name, cfg_file_name=CONFIG_FILE_NAME, path=DATA_PATH):
        """
        constructor
        :param concept_name: name of the root concept for the CMAP - this is the main concept described by the CMAP
        :param concept_file_name: name of the CXL file created as an export from the CMAP
        :param cfg_file_name: name of the JSON configuration file (default provided)
        :param path: name of the path to the data directory (default provided)
        """
        self.concept_name = concept_name
        self.cfg_file = os.path.join(path, cfg_file_name)
        self.data_file = os.path.join(path, concept_file_name)
        self.config = dict()
        self.data_path = path
        self._load_config()
        self.node_types = []
        self._load_node_types()
        self.unknown_node_type = self._set_unknown_node_type()

    def _load_config(self):
        """
        load the configuration options from the CONFIG_FILE_NAME json file
        """
        with open(self.cfg_file, "r") as f:
            json_config = f.read()
            self.config = json.loads(json_config)

    def _load_node_types(self):
        """
        load the list of node types found in the config file into a list of node type objects
        """
        for type in self.config["node_types"]:
            self.node_types.append(NT.NodeType(type["name"], type.get("label"), type.get("node_color"),
                                   type.get("source_links"), type.get("target_links"), type.get("background_color"),
                                   type.get("border_color"), type.get("border_shape")))

    def get_node_type(self, name):
        """
        lookup a node_type based on a name
        :param name: name of the node type to return
        :return: node type if a match is found, otherwise None
        """
        for node_type in self.node_types:
            if node_type.label == name:
                return node_type
        return None

    def get_concept_type(self, background_color=None, border_color=None, border_shape=None):
        """
        given information about the CMAP concept representation, find the matching concept type
        :param background_color: background color of the concept in the CMAP (e.g. 255,255,150,255)
        :param border_color: border color of the concept in the CMAP (e.g. 0,0,255,255)
        :param border_shape: border shape of the concept in the CMAP (e.g. rectangle)
        :return: concept type object
        """
        concept_type = self.unknown_node_type
        for node in self.node_types:
            if self._is_type_match(node, background_color, border_color, border_shape):
                concept_type = node
                break
        return concept_type

    def _is_type_match(self, node, background_color, border_color, border_shape):
        """
        does the detailed matching between configuration nodes and CMAP nodes to determine if a node is a match
        :param node: node type object
        :param background_color: background color of the concept in the CMAP (e.g. 255,255,150,255)
        :param border_color: border color of the concept in the CMAP (e.g. 0,0,255,255)
        :param border_shape: border shape of the concept in the CMAP (e.g. rectangle)
        :return: boolean
        """
        is_type_match = True
        if (border_color is not None and node.border_color is not None and border_color != node.border_color) or \
                (background_color is not None and node.background_color is not None and background_color != node.background_color) or \
                (border_shape is not None and node.border_shape is not None and border_shape != node.border_shape):
            is_type_match = False
        return is_type_match

    def _set_unknown_node_type(self):
        """
        create a node type object to represent Unknown types in the CMAP graph
        :return: node type object
        """
        return NT.NodeType("Unknown", "Unknown", "#FFFFFF", "0,0,0,0", "0,0,0,0", "Unknown")

    @property
    def data_path_dir(self):
        return self.data_path

    @property
    def graphml_file(self):
        return os.path.join(self.data_path, self.config["graphml_file_name"])

    @property
    def json_tree_file(self):
        return os.path.join(self.data_path, self.config["json_tree_file_name"])

    @property
    def json_force_file(self):
        return os.path.join(self.data_path, self.config["json_force_file_name"])

    @property
    def report_file(self):
        return os.path.join(self.data_path, self.config["report_file_name"])

    def report_headers(self, worksheet_name):
        """
        for a named worksheet in a report spreadsheet return the column headers
        :param worksheet_name:
        :return: list of column headers
        """
        if "node" in worksheet_name.lower():
            return self.config["report_node_headers"]
        elif "edge" in worksheet_name.lower():
            return self.config["report_edge_headers"]