"""
cxl_report

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
import xlsxwriter as XSL


class CxlReport:
    """
    generate a listing of the components of the CMAP with identifying details and any obvious errors listed
    """
    def __init__(self, cmap, config):
        """
        :param cmap is a graph structure build from the CMAP CXL format
        :param config: a configuration object that provides access to the program's config setting
        """
        self.cmap = cmap
        self.cfg = config

    def create_report(self):
        """
        generates an Excel spreadsheet documenting the contents of the CMAP for use as a Biomedical Concept
        :return:
        """
        workbook = XSL.Workbook(self.cfg.report_file)
        bold = workbook.add_format({'bold': True})
        self._create_node_worksheet(workbook, bold)
        self._create_edge_worksheet(workbook, bold)
        workbook.close()

    def _create_edge_worksheet(self, workbook, bold):
        """
        generate the worksheet listing and describing the edges found in the CMAP
        :param workbook: the excel workbook to create the worksheet in
        :param bold: bold format used to highlight column headers and noteworthy cells
        """
        worksheet = workbook.add_worksheet("CMAP Edges")
        self._write_header_record(worksheet, bold)
        row_number = 1
        for edge in set(self.cmap.linking_phrase.values()):
            worksheet.write(row_number, 0, edge)
            worksheet.write(row_number, 1, list(self.cmap.linking_phrase.values()).count(edge))
            row_number += 1

    def _create_node_worksheet(self, workbook, bold):
        """
        generate the worksheet listing and describing each node in the CMAP
        :param workbook: the excel workbook to create the worksheet in
        :param bold: bold format used to highlight column headers and noteworthy cells
        """
        worksheet = workbook.add_worksheet("CMAP Nodes")
        self._write_header_record(worksheet, bold)
        row_number = 1
        for vertex in self.cmap:
            print(" report " + vertex.type)
            if vertex.is_root:
                worksheet.write(row_number, 0, vertex.label, bold)
            else:
                if vertex.type == 'Data Element Concept':
                    if hasattr(vertex,"varName") :
                        print("Found one")
                        worksheet.write(row_number, 0, vertex.varName)
                    else:
                        worksheet.write(row_number, 0, vertex.label)
                else:
                    worksheet.write(row_number, 0, vertex.label)
            worksheet.write(row_number, 1, vertex.type)
            print(vertex.type)
            worksheet.write(row_number, 2, vertex.id)
            worksheet.write(row_number, 3, self._is_orphan(len(vertex.source), len(vertex.target)))
            worksheet.write(row_number, 4, self._is_entry_point(len(vertex.source), len(vertex.target)))
            worksheet.write(row_number, 5, len(vertex.source)/2)
            worksheet.write(row_number, 6, len(vertex.target)/2)
            worksheet.write(row_number, 7, self._get_invalid_links(vertex))
            row_number += 1

    def _get_invalid_links(self, vertex):
        """
        for each vertext return invalid relationship source and target links. Valid links are defined in the metamodel
        and listed in the configuration file
        :param vertex: vertext object that includes all references to and from the vertex (node)
        :return: a string of comma separated invalid link (relationship) names or empty string if all are valid
        """
        node_type = self.cfg.get_node_type(vertex.type)
        if node_type is None:          # if invalid node then do not report links as invalid
            return ""
        to_links = set([link[1] for link in vertex.source if link[1] not in node_type.valid_source_links])
        from_links = set([link[1] for link in vertex.target if link[1] not in node_type.valid_target_links])
        return ", ".join(to_links | from_links)

    def _is_entry_point(self, source_node_count, target_node_count):
        """
        an entry_point is defined as a node with no source, but there are targets
        :param source_node_count: number of source vertexes for a given vertex in the CMAP graph
        :param target_node_count: number of target vertexes for a given vertex in the CMAP graph
        :return: string "Yes" if it is an orphan or empty_string if not ""
        """
        return "Yes" if source_node_count == 0 and target_node_count > 0 else ""

    def _is_orphan(self, source_node_count, target_node_count):
        """
        an orphan is defined as a node with no source and no targets
        :param source_node_count: number of source vertexes for a given vertex in the CMAP graph
        :param target_node_count: number of target vertexes for a given vertex in the CMAP graph
        :return: string "Yes" if it is an orphan or empty_string if not ""
        """
        return "Yes" if source_node_count == 0 and target_node_count == 0 else ""

    def _write_header_record(self, worksheet, bold):
        """
        write the headers from the config file as the first line in the report
        :param worksheet: worksheet object - the active worksheet
        :return:
        """
        col_number = 0
        for header in self.cfg.report_headers(worksheet.name):
            worksheet.write(0, col_number, header, bold)
            col_number += 1

