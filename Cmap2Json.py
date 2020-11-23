"""
Cmap2Json

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
import json, os, sys, argparse
import logging
import graphSelect as gs
import C360LibraryTools as la
import LookupStandardsMetadata as CLIB


""""
python Cmap2Json.py -g cmap_graph.graphml -d DomainPrefix
"""
DATA_PATH = os.path.dirname(os.path.realpath("."))
classTopic = {"Findings": "TESTCD","Interventions": "TRT","Events": "TERM","Special-Purpose":"SUBJID"}
bcList = []

def main():
    logging.basicConfig(filename="c360Cmap2Json.log",format="%(module)s %(message)s", filemode="w",level=logging.INFO)
    logging.info("Starting")
    args = set_cmd_line_args()
    cmap_graphFileName = args.cmapGraphFN
    domainName = args.domainPrefix
    tokenlist = la.getLibraryAuthInfo()
    sdtmInfo = CLIB.lookupStandardSDTM('sdtmig', '3-2', domainName, tokenlist)
    mappingFileName= domainName + "_Mappings.json"
    mappingInfo = getJsonFromFile(mappingFileName)

    g = getGraph(cmap_graphFileName)
    bcDef = cmapGraph2json(g, domainName, sdtmInfo, mappingInfo)
    logging.info("Done")

def cmapGraph2json(g, domainName, sdtmDomainInfo, mappingInfo) ->dict:
    domainMDFileName = domainName + "_sdtmClib.json"
    #sdtmDomainInfo= getJsonFromFile(domainMDFileName)

    domainInfo = sdtmDomainInfo["domain"]
    domainClass = domainInfo["Class"]
    topicVar = classTopic[domainClass]
    domainVars = getbcVarDefs(sdtmDomainInfo)


    nConcepts = gs.countNodeType(g,"Observation Concept")
    obsConceptList = gs.selectNodesType(g,"Observation Concept")

    domain_bcs = {}
    domain_bcs["parent"] = domainName + "-sdtmig"
    domain_bcs["prodVers"] = "sdtmig-3-2"
    bcName = domainName + "_bcConcepts"
    bcTopicVar = domainName + topicVar
    ocCounter = 1

    for obsConcept in obsConceptList:
        obsConceptNodeID = obsConcept["id"]
        print(obsConceptNodeID)
        logging.debug("cmapGraph2json:  " + obsConceptNodeID)
        obsConceptNamefromCmap = gs.selectNodeID(g, obsConceptNodeID)["name"]  # remove whitespace?
        obsConceptName = label2camel(obsConceptNamefromCmap)
        print("Assembling information for " + obsConceptName + "obsConceptName")
        obsConceptLabel = obsConceptNamefromCmap
        bcCond = gs.selectNodeID(g, obsConceptNodeID)["description"]
        obsDECList = list(g.neighbors(obsConceptNodeID))
        linkInfo = getTopicVarLink(domainVars)
        bcInfo = {}
        conceptName  = domainName + "_ObsConcept"
        bcInfo["ordinal"] = ocCounter
        ocCounter += 1
        bcInfo["bcID"] = "BC" + domainName + obsConceptName.strip()
        bcInfo["bcName"] =  obsConceptName
        logging.info("cmapGraph2json:  " + obsConceptName)
        logging.info("")
        bcInfo["bcLabel"] = obsConceptLabel
        bcInfo["bcTopicVar"] = bcTopicVar
        bcInfo["bcCond"] = bcCond
        bcInfo["_links"] = linkInfo
        bcVarList = []
        cdTypeList  = ["text", "enumerated", "integer", "described", "float", "ISO 8601"]
        for dec in obsDECList:
            bcVarInfo = {}
            DECname = gs.selectNodeID(g,dec)["name"]
            bcVarInfo["DEC" ] = DECname
            bcVarInfo["ClibRef"] = getClibVarRef(DECname, domainVars)
            cdList = list(g.neighbors(dec))
            # TODO: Add handling for DescribedValues, ISO 8601 and ISO 3166.
            # It might be better to construct the bcInfo so that it includes all of the variables identified n the cmap.
            if len(cdList) == 1:
                dcNodeRaw = gs.selectNodeID(g, cdList[0])["name"]
                dcNode = dcNodeRaw.replace(",",";")
                if "(D++)" in gs.selectNodeID(g, cdList[0])["description"]:
                    descr = gs.selectNodeID(g, cdList[0])["description"]
                    l = descr.find("(D++")
                    l2 = l + 5
                    cddefault = descr[l+5:]
                    cdlabel = descr[:l].rstrip(" ")
                    cdVal = {}
                    cdValParts = cdlabel.split(";")
                    if len(cdValParts) > 1:
                        bcVarInfo["CDVal"] = {"default":cddefault,"subset":cdlabel}
                elif dcNodeRaw not in  cdTypeList:
                    cdVal = {}
                    cdValParts = dcNode.split(";")
                    if len(cdValParts) > 1:
                        cdVal["subset"] = dcNode
                    else:
                        cdVal["value"] = dcNode
                    bcVarInfo["CDVal"] = cdVal
                else:
                    bcVarInfo["cdType"] = dcNodeRaw
            if DECname in mappingInfo:
                bcVarInfo["origin"] = mappingInfo[DECname]

            bcVarList.append(bcVarInfo)
            bcInfo["bcVarList"] = bcVarList

        bcList.append(bcInfo)
    domain_bcs[bcName] = bcList
    jsonFN = domainName + "_bcConcepts.json"
    with open(jsonFN, "w", encoding="utf-8") as fo:
        fo.write(json.dumps(domain_bcs))
    #Def.writeXML(sdtmDomainInfo, domain_bcs, mappingInfo)
    return bcInfo
def set_cmd_line_args():
    """
    Example -f cmap_graph.graphml
    return: argparse object with command line parameters
    """
    parser = argparse.ArgumentParser(description="process cmap_Graph")
    parser.add_argument("-g", dest="cmapGraphFN", help="GraphML file generated from csl_load tool.", default="cmap_graph.graphml")
    parser.add_argument("-d", dest="domainPrefix", help="Doman Name.", required=True)
    args= parser.parse_args()
    return args

def getGraph(graphFileName)-> object:
    f = os.path.join(os.path.realpath("."), graphFileName)
    g: object = nx.read_graphml(f)
    return g

def getJsonFromFile(jsonFileName) -> dict:
    fname = os.path.join(os.path.realpath("."), jsonFileName)
    f = open(fname, "r")
    return json.load(f)

def getTopicVarLink(domainVars:list) ->dict:
    retLinkInfo = {}
    for vdef in domainVars:
        logging.info("getTopicVarLink: " + vdef["role"])
        if vdef["role"] == "Topic":
            retLinkInfo["sdtmig-topic"] = vdef["_links"]["self"]
            return retLinkInfo
    logging.error("No topic variable found")
    return retLinkInfo

def getTopicVarname(topicVarRef:dict) -> str:
    topicHref = topicVarRef["sdtmig-topic"]["href"]
    hrefParts = topicHref.split("/")
    lastPartIndex = len(hrefParts)-1
    return hrefParts[lastPartIndex]

def getbcVarDefs(domainMD:dict) -> list:
    dmd = domainMD["domain"]
    return dmd["bcVarsets"]

def getClibVarRef(DECname:str, domainVars:list) ->dict:
    retVref = {}
    for vdef in domainVars:
        varLabel = vdef["label"]
        if DECname in varLabel:
            retVref["self"] = vdef["_links"]["self"]
            if "codelist" in vdef["_links"]:
                retVref["codelist"] = vdef["_links"] ["codelist"]
            return retVref
        elif DECname in vdef["name"]:
            retVref["self"] = vdef["_links"]["self"]
            if "codelist" in vdef["_links"]:
                retVref["codelist"] = vdef["_links"]["codelist"]
            return retVref
    return retVref

def label2camel(s:str)->str:
    strimmed = s.lstrip(" ").rstrip(" ")
    sparts = strimmed.split(" ")
    if len(sparts) == 0:
        scamel = strimmed[:1].upper() + strimmed[1:]
        return scamel
    else:
        scamel = ""
    for word in sparts:
        wordCamel = word[:1].upper() + word[1:]
        scamel = scamel + wordCamel
    return scamel


if __name__ == "__main__":
    main()
