"""
C360LibraryTools

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
import getpass
import json, os, fnmatch, requests, logging
import config
import LookupStandardsMetadata as CLIB
"""
python Cmap_toJson.py -f cmap_report -s sdtName  -v stdVersion -p testOrProd -c multiconcept -m mappingsFile -x outputDefine


 -s standard_name -- optional. Name of standard for lookup.  SDTM or ADaM. Default is both.
 -v standard_version -- optional. Version of standard for look up. If not provided the CDISC 360 versions (sdtmig 3-2 and adamig 1-2) will be used. 
 -f xlsx_file -- required. Name of file containing concept map information generated from cxl_load tool.
 -p instanceAsk -- optional. When True, user will be prompted for the CDISC Library instance.  When False will default to the QA/Test instance.
 -c conceptsAsk -- optional.  Use True for domains where there is a value level metadata template.
 -m mappingsFile -- optional. Name of mappings file to include when creating Define-XML. Default is VS_Mappings.json.
 -x defineXML -- optional. If True, define-XML output file will be provided.  Default = True
 
"""

cdisc_test_LibraryURL = "https://api.library.cdisclibrary.org/api"
cdisc_prod_LibraryURL = "https://library.cdisc.org/api"
hdr4xml = {'accept': 'application/xml','api-key': ''}

testhdr = {'api-key': config.api_key}

DATA_PATH = os.path.dirname(os.path.realpath(".")) + "\\bcMetadata"


def main():
	""" Get standards information for specified standards versions.
	Used TestInstance by default.
	"""
	logging.basicConfig(filename="c360LibaryTools.log", filemode="w", level=logging.DEBUG)

	args = set_cmd_line_args()
	input_mapReport = os.path.join(DATA_PATH, args.cmap_report)
	if not os.path.exists(input_mapReport):
		logging.error("%s does not exist.", input_mapReport)
		exit()
	if args.instanceAsk != "test":
		tokenlist = getLibraryAuthInfo(True)
	else:
		tokenlist = getLibraryAuthInfo()
	# modularize?
	doConcepts = False
	bcList = []
	getConcepts = args.conceptsAsk
	if getConcepts :
		# Hardcode to bcConcepts.json  if argument is provided
		# TODO: prompt for the concepts file
		bcList = getJsonFromFile("bcConcepts.json")
		fname = os.path.join(DATA_PATH, "bcConcepts.json")
		if os.path.exists(fname):
			conceptsFile = open(fname)
			bcJson = json.load(conceptsFile)
			bcList = bcJson['conceptList']
			doConcepts = True
	stdName = args.standard_name
	stdVersion = args.standard_version

	mappingFile = args.mappingsFile
	if mappingFile == "none":
		# to do: check that file exists
		logging.info("No mappings file provided.")
		mappings = ""
	else:
		mappings = getJsonFromFile(mappingFile)  # will be None if not provided.
	outputDefine = args.doXMLout
	if stdName == "both":  # only does c360 versions
		sdtmInfo = CLIB.lookupStandard("sdtmig", "3-2", input_mapReport, tokenlist, bcList)
		if outputDefine:
			DEF.writeXML(sdtmInfo, bcList, mappings)
		cdashInfo = CLIB.lookupCDASHIG("2-1", input_mapReport, tokenlist, bcList)
		#ODM.writeXML(cdashInfo)
	elif stdName == "sdtmig":
		if stdVersion == "c360":
			sdtmInfo = CLIB.lookupStandard(stdName, "3-2", input_mapReport, tokenlist, bcList)
		else:
			sdtmInfo = CLIB.lookupStandard(args.standard_name, args.standard_version, input_mapReport, tokenlist,
										   bcList)
		if outputDefine:
			DEF.writeXML(sdtmInfo)
	elif stdName.startswith("adam"):
		adamInfo = CLIB.lookupADaMStd(args.standard_name, args.standard_version, input_mapReport, tokenlist,
										   bcList)
	elif stdName == "cdashig":
		if stdVersion == "c360":
			cdashInfo = CLIB.lookupCDASHIG("2-1", input_mapReport, tokenlist, bcList)
		else:
			cdashInfo = CLIB.lookupCDASHIG(args.standard_version, input_mapReport, tokenlist, bcList)
		#ODM.writeXML(cdashInfo)
	print("Done")


def set_cmd_line_args():
	"""
	Example: -f cmap_report_DM.xlsx -s "sdtmig" -v "3-2"
	:return: argparse object with command-line parameters
	"""
	parser = argparse.ArgumentParser(description="lookup DEC definitions in CDISC Library")
	parser.add_argument("-s", "--s", dest="standard_name", help="Name of standard", required=False, default="both")
	parser.add_argument("-f", "--xlsx_file", dest="cmap_report", help="Name of Excel file with cmap report.", required=True)
	parser.add_argument("-v", "--v", dest="standard_version", help="Version of standard", required=False, default="c360")
	parser.add_argument("-p", dest="instanceAsk", help="Prompt for library instance?", required=False, default="test")
	parser.add_argument("-c", dest="conceptsAsk", help="Prompt for list of concepts?", required=False, default=False)
	parser.add_argument("-m", dest="mappingsFile", help="Name of Mappings File", required=False, default="none")
	parser.add_argument("-x", dest="doXMLout", help="Output Define-XML?", required=False, default=False)
	args = parser.parse_args()
	return args


def ApiContact(testURL, tryTimes=1):
	logging.info("ApiContact called with %s.", testURL)
	tokenList = getLibraryAuthInfo()
	uname = tokenList[0]
	passwd = tokenList[1]
	r = requests.get(testURL, auth=(uname, passwd))
	status = r.status_code
	ctype = r.headers.get('content-type')
	if (status == 200):
		logging.DEBUG("Success! %s content available")
	else:
		logging.warning("Get request %s returned %s", testURL, status)
	logging.DEBUG("ApiContact: status check %s.", status)


def getLibraryAuthInfo(askme=False) -> list:
	logging.debug("getLibraryAuthInfo")
	alist = []
	uname = input("CDISC Library Username: ")
	passwd = getpass.getpass()
	useURL = askTestorProd(askme)
	print(useURL)
	alist.append(uname)
	alist.append(passwd)
	alist.append(useURL)
	return alist


def askUntilOk(askCount=3) -> list:
	logging.info("askUntilOk")
	counter = askCount
	clist = []
	while (counter > 0):
		clist = getLibraryAuthInfo()
		askPrompt = clist[0] + '/' + clist[1] + ' ok? [y/n] '
		keepIt = input(askPrompt)
		if (keepIt == 'y'):
			return clist
		counter = counter - 1
	return clist


def askTestorProd(askMe=False) -> str:
	defaultURL = config.default_url;
	if askMe:
		askPrompt = "Use " + defaultURL + "? "
		resp = input(askPrompt)
		if (resp.upper() != 'Y'):
			return cdisc_prod_LibraryURL;
	return defaultURL;


def askResponseType() -> str:
	askPrompt = "Response type Json[j], XML[x], Excel[e] or CSV[c] "
	resp = input(askPrompt)
	return resp


def testRequest(reqURL, uname, passwd, rformat='json') -> dict:

	r = requests.get(reqURL, headers=testhdr, auth=(uname, passwd))
	status = r.status_code
	if (status == 200):
		reqPayload = r.text
		reqJson = json.loads(reqPayload)
		return reqJson
	elif (status == 404):
		reqJson = {}
		reqJson["Status404"] = reqURL
		logging.info("%s returned %s", reqURL, status)
	else:
		reqJson = {}
		reqJson["status"] = "ErrorCode" + str(status)
		reqJson["href"] = reqURL
		logging.error("%s returned %s (%s %s)", reqURL, status, uname, passwd)
	return reqJson


def libraryURL() -> str:
	return 'https://library.cdisc.org/api'


def displayAnalysisProducts(prodListJson) -> list:
	prLinks = prodListJson["_links"]
	prodLinkList = prLinks["adam"]
	display = input("Display Product list? ")
	for prod in prodLinkList:
		prodHref = prod["href"]
		prodTitle = prod["title"]
		prodType = prod["type"]
		if (display == "Y"):
			print(prodHref, prodTitle, prodType)
	return prodLinkList


def adamG2URL(baseURL: str, prodHref: str) -> str:
	return baseURL + prodHref + '/datastructures'


def adamG3URL(baseURL: str, dsHref: str) -> str:
	return baseURL + dsHref


def adamG4URL(baseURL: str, dsHref: str) -> str:
	g4url = baseURL + dsHref + "/varsets"
	return g4url


def adamG5URL(baseURL: str, vsHref: str) -> str:
	g5url = baseURL + vsHref
	return g5url


def adamG6URL(baseURL: str, dsHref: str) -> str:
	g6url = baseURL + dsHref + "/variables"
	return g6url


def adamG7URL(baseURL: str, varHref: str) -> str:
	g7url = baseURL + varHref
	return g7url




def testRequestAll(reqURL, uname, passwd, rformat) -> dict:
	hdrs = {'accept': rformat}
	r = requests.get(reqURL, auth=(uname, passwd), headers=hdrs)
	status = r.status_code
	if (status != 200):
		logging.error("%s returned %s (%s %s)", reqURL, status, uname, passwd)

	reqPayload = r.text
	reqJson = json.loads(reqPayload)
	logging.info("%s Json %s xml %s", reqURL, status)
	return reqJson

def getJsonFromFile(jsonFileName) -> dict:
    fname = os.path.join(os.path.realpath("."), jsonFileName)
    f = open(fname, "r")
    return json.load(f)

if __name__ == "__main__":
	main()
