"""
cxl_load

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
import argparse
import configuration as CFG
import cxl_cmap as CMAP
import network_graph as NETG
import cxl_report as REP
import bc_factory as BCF

"""
cxl_load is intended to be an example program that loads and processes CMAP CXL exports as part of CDISC 360.
This program may be expanded or replaced with one that executes conformance checks on the CMAP CXL content.
Use the -h command-line parameter to get help on running cxl_loader.py.
Examples: 
python cxl_loader.py -f 360-bc-HbA1C.cxl -c "Glycosylated hemoglobin A1c assay"
python cxl_loader.py -f 360-bc-HbA1C.cxl -c "Glycosylated hemoglobin A1c assay" -d "c:\\cmaps\\cxl\\data"
python cxl_loader.py -f HbA1C-Berlin-2020-01-22.cxl -c "Hemoglobin A1C to Hemoglobin Ratio Measurement (C111207)"
python cxl_loader.py -f VS-SYSBP-Metamodel3.cxl -c "Systolic Blood Pressure (C0005823)"
"""


def main():
    """
    main entry point into the cxl_load program that creates an internal representation of the CMAP graph that is used
    to create a report of the BC contents, generate a graphML version for visualization,
    """
    args = set_cmd_line_args()
    config = CFG.Configuration(args.concept_name, args.cxl_file)
    print("done config")
    cmap_graph = load_cmap(config)
    print("done load_cmap")
    create_network_graph(cmap_graph, config)
    print("done create network graph")
    create_cmap_report(cmap_graph, config)
    print("done create report")
    create_serialized_bc(cmap_graph, config)

def create_cmap_report(cmap, config):
    """
    generates an Excel based report based on the graph created from the CMAP export
    :param cmap: cmap graph object
    :param config: configuration object
    """
    report = REP.CxlReport(cmap, config)
    report.create_report()


def create_network_graph(cmap, config):
    """
    create a graphml file representation of the cmap graph. The graphML file can be viewed in yEd. In yEd use the Edit
    Property Mapper to set the node color
    :param cmap: the graph created from the cmap cxl file
    :param config: configuration object with config parameters
    """
    graph = NETG.NetworkGraph(cmap)
    graph.save_graphml(config.graphml_file)


def load_cmap(config):
    """
    load the cmap CXL file and create a graph from the contents
    :param config: configuration object with config parameters
    :return: the graph created from the cmap cxl file
    """
    cmap_graph = CMAP.CxlCmap(config)
    cmap_graph.load()
    return cmap_graph

def create_serialized_bc(cmap, config):
    """
    serializes the internal BC graph as JSON and saves it to a file
    :param cmap_graph: internal graph of vertex objects created from CMAP
    :param config: configuration object with config parameters
    """
    bc_factory = BCF.BCFactory(cmap, config)
    bc = bc_factory.create_bc()
    bc_factory.save_bc(bc)


def set_cmd_line_args():
    """
    Example: -f HbA1C-Interchange-Demo.cxl -c "Hemoglobin A1C to Hemoglobin Ratio Measurement (C111207)"
    :return: argparse object with command-line parameters
    """
    parser = argparse.ArgumentParser(description="parse the CMAP CXL export and convert it to biomedical concepts")
    parser.add_argument("-c", "--concept", dest="concept_name", help="Name of main concept", required=True)
    parser.add_argument("-f", "--cxl_file", dest="cxl_file", help="Name of cxl file to load (do not include the path)", required=True)
    parser.add_argument("-d", "--file_path", dest="file_path", help="Directory of cxl file to load", required=False)
    parser.add_argument("-j", "--json_file", dest="json_file", help="BC serialized as JSON", required=False)
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    main()
