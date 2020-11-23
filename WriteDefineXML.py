# WriteDefXML
#
# The MIT License (MIT)
#
#   Copyright (c) 2019 CDISC
#
#   Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
#   associated documentation files (the "Software"), to deal in the Software without restriction,
#   including without limitation the rights to use, copy, modify, merge, publish, distribute,
#   sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is
#   furnished to do so, subject to the following conditions:
#   The above copyright notice and this permission notice shall be included in all copies or
#   substantial portions of the Software.
#
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT
#   NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
#   NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#   DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT
#   OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""
Usage: python WriteDefineXML.py


"""
from typing import Dict, Any
from xml.dom import minidom

import datetime, logging
import json, os, sys, argparse


odmURL = 'http://www.cdisc.org/ns/odm/v1.3'
defnsURI = 'http://www.cdisc.org/ns/def/v2.1'
mdrDefURL = 'http://www.cdisc.org/ns/LIBRARY-Define/v1.0'
mdrURL = 'http://www.cdisc.org/ns/c360/LIBRARY-XML/v1.0'
mdrnsURI = "https://www.cdisc.org/ns/mdr/c360"

C360_SDTMIG_Version = "3-2"
classTopic = {"Findings": "TESTCD", "Interventions": "TRT", "Events": "DECOD"}
genObsClasses = ["Findings", "Interventions", "Events"]
classTerminology = { "Special-Purpose": "SPECIAL PURPOSE","Interventions":"INTERVENTIONS", "Events": "EVENTS", "Findings":"FINDINGS", "Findings About": "FINDINGS ABOUT",
                     "Trial Design":"TRIAL DESIGN"}
C360NoVLM_List = ["DM", "EC"]
C360DomainList = ["DM", "EC", "DS", "AE", "VS"] #Included Domains
#C360DomainList = ["DS", "VS"]

codelistRefs = []
codelists = []

igstdRef = "C360.SDTMIG-VERS"
cdt = datetime.datetime.now()

def main():
    logging.basicConfig(filename="c360WriteXMLAll.log",format="%(module)s %(message)s",filemode="w",level=logging.INFO)
    args = set_cmd_line_args()  # Individual domains no longer supported
    domainPrefix = args.domainPrefix
    bcInfoFN = args.bcInfo
    sdtmMetadata = {"prodVers": "SDTMIG-3-2"}
    domainMetadata = []
    for domain in C360DomainList:
        bcInfoFN = domain + "_bcConcepts.json"
        bcInfo = getJsonInfo(bcInfoFN)
        clibInfoFN = domain + "_sdtmClib.json"
        clibInfo = getJsonInfo(clibInfoFN)
        logging.info(domain)
        domainMetadata.append(bindBC2Domain(clibInfo, bcInfo))
    sdtmMetadata["CodelistRefs"] = codelistRefs
    sdtmMetadata["Codelists"] = codelists
    sdtmMetadata["DomainList"] = domainMetadata
    jsonFN = "Temp_defineInfo.json"
    with open(jsonFN, "w", encoding="utf-8") as fo:
        fo.write(json.dumps(sdtmMetadata))
    writeXML(sdtmMetadata)


def bindBC2Domain(defInfo: dict, bcInfo: dict) ->dict:
    outputMetadata = {}
    prodVers = defInfo["ProdVersion"]
    varsetInfo= defInfo["domain"]
    dsname = varsetInfo["Name"]
    outputMetadata["domain"] = dsname

    #bcprodVers = bcInfo["prodVers"]
    clibCodelists = defInfo["codelists"]
    igList = []
    idefList = []

    vsn = 0
    comments = []
    vlmList = []
    methodsList = []

    bcParent = bcInfo["parent"]
    bcDomain = bcParent.split("-")[0]
    bcKey = bcDomain + "_bcConcepts"
    bcConcepts = bcInfo[bcKey]
    bcVarnames = []
    bcValueDefs = {}
    bcCodeListDefs = []
    bcvlm = bcInfo2VLM(bcDomain, bcConcepts)
    ds = varsetInfo
    outputMetadata["bcconcepts"] = bcConcepts

    if len(bcConcepts) > 1:
        for bcDef in bcConcepts:
            if "bcCond" in bcDef:
                bcCond = bcDef["bcCond"]
                topicVarWCRef = bcCond2OID(bcDef["bcID"], bcCond)
                # getCondVarname(bcCond)
                vdefOID = "C360.VLD." + bcDef["bcID"] + "." + getBcCondVar(bcCond)
            else:
                topicVarWCRef = "C360.WC." + bcDef["bcID"]
                vdefOID = "C360.VLD." + bcDef["bcID"] + getBcCondVar(bcCond)
            wcDefOID = topicVarWCRef
            bcLabel = bcDef["bcLabel"]
            bcName = bcDef["bcName"]
            prefixVLoid = "C360.BC.VLM." + bcName + "." + bcDef["bcTopicVar"] + "."
            vlmOrdinal = 1
            bcValueDef = {}
            # bcValueDef["bcName"] = bcName
            bcItemRefs = {}
            bcItemDefs = []

            bcVarList = bcDef["bcVarList"]
            for bcVar in bcVarList:
                itemRef = {}
                itemDef = {}
                bcClibRef = bcVar["ClibRef"]
                logging.DEBUG("WriteXML: %s (DEC)", bcVar["DEC"])
                if bcClibRef is not None and "self" in bcClibRef:
                    bcvarname = bcVarName(bcClibRef)
                    if bcvarname not in bcVarnames:
                        bcVarnames.append(bcvarname)
                    hasCL = bcHasCL(bcClibRef)
                    valname = bcVar["DEC"]
                    vlOID = prefixVLoid + valname + "." + bcvarname
                    itemRef["ItemOID"] = vlOID
                    itemRef["OrderNumber"] = vlmOrdinal
                    itemDef["OID"] = vlOID
                    itemDef["Name"] = bcvarname + "-" + bcName
                    itemDef["Label"] = bcvarname + " for " + bcName
                    if "cdType" in bcVar:
                        if bcVar["cdType"] == "ISO 8610":
                            itemDef["DataType"] = "datetime"
                        else:
                            itemDef["DataType"] = bcVar["cdType"]
                    else:
                        itemDef["DataType"] = "text"
                    itemDef["Label"] = valname + "_" + bcLabel
                    #
                    if hasCL:
                        clhref = bcCLRef(bcClibRef)
                        if "CDVal" in bcVar:
                            bcCodeList = {}
                            #clOID = "CL." + bcvarname + "." + valname + "." + bcCLRef(bcClibRef)
                            clOID = "C360.CL.BC." + bcName + "." + valname + "." + clhref
                            bcCLDef = cdVal2bcCLDef(clOID, bcName, bcVar["CDVal"])
                            clDef = {}
                            clDef["name"] = bcName + "_360"
                            clDef["href"] = clOID
                            clDef["terms"] = bcCDVal2TermsList(bcvarname, bcConcepts, bcName)
                            if "subset" in bcCLDef:
                                clDef["subset"] = bcCLDef["subset"]
                                if "defaultVal" in bcCLDef:
                                    clDef["c360DefaultVal"] = bcCLDef["defaultVal"]
                            if clOID not in codelistRefs:
                                codelistRefs.append(clOID)
                                bcCodeListDefs.append(bcCLDef)
                                codelists.append(clDef)
                            itemDef["CodeListOID"] = clOID
                            #print("added Codelist " + bcCLDef["name"])
                        else:
                            clOID = "CL." + bcCLRef(bcClibRef)
                            if clOID not in codelistRefs:
                                codelistRefs.append(clOID)
                                if "codelist" in bcClibRef:
                                    logging.debug("Adding Codelist %s", bcClibRef["codelist"])
                                    codelists.append(bcClibRef["codelist"])
                                else:
                                    logging.error("Expected codelist definition in bc Concept for  %s.", bcvarname)
                            itemDef["CodeListOID"] = clOID
                    elif "CDVal" in bcVar:  #need to handle this -- some Cmaps do not include cmap citations but include a codelist-style label
                        bcCodeList= {}
                        cdValDef = bcVar["CDVal"]
                        if "value" in cdValDef:
                            cdValLabel = cdValDef["value"]
                            clOID = "C360.BC.CDVal." + bcvarname + "." + valname
                            bcCLDef = cdVal2bcCLDef(clOID, bcvarname, bcVar["CDVal"])
                            clDef = {"name": bcvarname + "_360","href": clOID,
                                     "terms": bcCDVal2TermsList(bcvarname,bcConcepts,bcName)}
                            if clOID not in codelistRefs:
                                codelistRefs.append(clOID)
                                bcCodeListDefs.append(bcCLDef)
                                codelists.append(clDef)
                            itemDef["CodeListOID"] = clOID
                            logging.debug("added Codelist " + clOID)
                    vlName = bcvarname.upper() + "-" + bcName.upper()
                    if "origin" in bcVar:
                        varMapping = bcVar["origin"]
                        varMappingType = varMapping["MappingType"]
                        if varMappingType not in ["Computation"]:
                            itemDef["OriginType"] = varMappingType
                            if varMappingType == "Assigned":
                                commentOID = "C360.COM." + vlOID
                                itemDef["CommentOID"] =  commentOID
                                comments.append(makeComment(commentOID, varMapping["Description"]))
                                logging.debug("Adding Comment " + commentOID)
                            else:
                                itemDef["OriginPredecessor"] = varMapping["SourceVar"]
                        else:
                            itemDef["OriginType"] = "Derived"
                            mapMethodsList = varMapping["Methods"]
                            methodOID = "C360.MTH." + vlName
                            methodDef = {}
                            methodDef["OID"] = methodOID
                            methodDef["Name"] = vlName
                            methodDef["Definition"] = mapMethodsList[0]
                            methodsList.append(methodDef)
                            itemRef["MethodOID"] = methodOID
                            if len(mapMethodsList) > 1:
                                methodOID = "C360.MTH.ALT." + vlName
                                itemRef["C360AltMethodOID"] = methodOID
                                methodDef = {}
                                methodDef["OID"] = methodOID
                                methodDef["Name"] = vlName + "- Alt"
                                methodDef["Definition"] = mapMethodsList[1]
                                methodsList.append(methodDef)


                    itemRef["WhereClauseOID"] = wcDefOID
                    logging.debug(" WhereClause " + wcDefOID)
                    bcItemRefs[bcvarname] = itemRef
                    idefList.append(itemDef)
                    vlmOrdinal += 1
            bcValueDef["ItemRefs"] = bcItemRefs
            bcValueDef["oid"] = vdefOID
            bcValueDefs[bcName] = bcValueDef

        bcvlm["bcValueDefs"] = bcValueDefs
        bcvlm["vlIdefs"] = idefList
        outputMetadata["VLDefs"] = bcValueDefs
        outputMetadata["bcvlm"] = bcvlm
        fname = dsname + "_vlm.json"
        with open(fname, "w", encoding="utf-8") as fo:
            fo.write(json.dumps(bcValueDefs))

    itemGroup = {}
    dsClass = ds["Class"]
    itemGroup["Class"] = dsClass
    itemGroup["OID"] = ds["OID"]
    itemGroup["Name"] = ds["Name"]
    itemGroup["Label"] = ds["Label"]
    itemGroup["defStructure"] = ds["datasetStructure"]
    # C360 specific value
    itemGroup["Purpose"] = "C360 Biomedical Concept"
    itemGroup["defStandardOID"] = igstdRef
    vsAVarList = ds["bcVarsets"]
    if dsClass in genObsClasses:
        classSuffix = classTopic[ds["Class"]]
        classTopicVar = ds["Name"] + classSuffix

    irefList = []
    iorder = 1
    for vsAvars in vsAVarList:
        itemDef = {}
        itemRef = {}
        codeListDef = {}
        varName = vsAvars["name"]
        itemOID = "C360." + itemGroup["Name"] + ".IT." + varName
        itemDef["OID"] = itemOID
        itemRef["ItemOID"] = itemOID
        itemRef["OrderNumber"] = str(iorder)
        iorder += 1
        itemRef["Role"] = vsAvars["role"]
        itemRef["mdrCore"] = vsAvars["core"]
        itemDef["Name"] = vsAvars["name"]
        itemDef["label"] = vsAvars["label"]

        itemDef["DataType"] = getDataType(vsAvars)
        if ("_links" in vsAvars):
            links = vsAvars["_links"]
            clDef = {}
            if ("codelist" in links):
                cl = links["codelist"]  # codelist has a list
                clibClRef = cl[0]
                clOID = "CL." + clibClRef["href"]
                itemDef["CodeListOID"] = clOID
                if clOID not in codelistRefs:
                    codelistRefs.append(clOID)
                    cldef = domainCLDef(clOID, clibCodelists)
                    codelists.append(domainCLDef(clOID, clibCodelists))
                # This handles the multiple codelist case which is not needed for sdtm 3.2
                if len(cl) >1:
                    logging.error("Multiple Codelist References not yet implemented.")
                    # codelists such as units could  be used for more than one variable
                    """ if the variable appears in the  bcConcepts list and has Codelist defined, it may also have a "CDVal".
                        If there is a CDVal, the Codelist will be represented in the define as a subset or a single value.
                        The text will be parcelled up into terms only if it is a perfectly formed sequence of  "value (c-code)" 
                        strings separated by a comma. If the same codelist has the same subset for more than one variable, it will have a different name.
                      """
            if hasCDVal(varName,bcConcepts):
                # if the cmap references a CDVAL but the standard version does not provide CT still want the CL
                clOID = "C360.BC.CDVal." + varName
                itemDef["CodeListOID"] = clOID
                if clOID not in codelistRefs:
                    codelistRefs.append(clOID)
                    clDef["name"] = varName + "_C360"
                    clDef["href"] = clOID
                    clDefTermList = bcCDVal2TermsList(varName, bcConcepts)
                    clDef["terms"] = clDefTermList
                    codelists.append(clDef)
            if "valueList" in vsAvars:
                clOID = "CL." + bcDomain + "." + varName
                itemDef["CodeListOID"] = clOID
                if clOID not in codelistRefs:
                    codelistRefs.append(clOID)
                    clDef["name"] = varName + "_C360"
                    clDef["href"] = clOID
                    clDef["terms"] = vsAvars["valueList"]
                    codelists.append(clDef)
                itemDef["CodeListOID"] = clOID
            elif "describedValueDomain" in vsAvars:
                clOID = "C360.CL." + vsAvars["describedValueDomain"]
                if clOID not in codelistRefs:
                    codelistRefs.append(clOID)
                    clDef["name"] = vsAvars["describedValueDomain"]
                    clDef["href"] = clOID
                    clDef["terms"] = []
                    codelists.append(clDef)
                    itemDef['CodeListOID'] = clOID
            elif ("valueDescription" in vsAvars):
                clOID = "CL." + vsAvars["valueDescription"]
                itemDef['CodeListOID'] = clOID
                if clOID not in codelistRefs:
                    codelistRefs.append(clOID)

        if hasOrigin(varName, bcConcepts):
            varMappingInfo = getOrigin(varName, bcConcepts)
            if varMappingInfo is not None:
                logging.info("Adding mapping for " + varName)
                #print(varMappingInfo)
                #varMapping = varMappingInfo[varName]
                varMappingType = varMappingInfo["MappingType"]
                if varMappingType not in ["Computation"]:
                    itemDef["OriginType"] = varMappingType
                    if varMappingType == "Assigned":
                        commentOID = "C360.COM." + itemOID
                        itemDef["CommentOID"] =  commentOID
                        comments.append(makeComment(commentOID, varMappingInfo["Description"]))
                        logging.debug("adding Comment " + commentOID)
                    else:
                        itemDef["OriginPredecessor"] = varMappingInfo["SourceVar"]
                else:
                    itemDef["OriginType"] = "Derived"
                    mapMethodsList = varMappingInfo["Methods"]
                    methodOID = "C360.MTH." + itemOID
                    methodDef = {}
                    methodDef["OID"] = methodOID
                    methodDef["Name"] = varName
                    methodDef["Definition"] = mapMethodsList[0]
                    methodsList.append(methodDef)
                    itemRef["MethodOID"] = methodOID
                    if len(mapMethodsList)  > 1:
                        methodOID = "C360.MTH.ALT." + itemOID
                        itemRef["C360AltMethodOID"] = methodOID
                        methodDef = {}
                        methodDef["OID"] = methodOID
                        methodDef["Name"] = varName + "- Alt"
                        methodDef["Definition"] = mapMethodsList[1]
                        methodsList.append(methodDef)

        if bcVarnames is not None and bcDomain != 'DM':
            # attach a vlref to each variable that is part of one of the BC Concepts
            if varName in bcVarnames:
                #
                vlmOID = "C360.VLM." + varName  # should be a lambda expression
                itemDef["vlRef"] = vlmOID
                vlmList.append(vlmOID)
        irefList.append(itemRef)
        idefList.append(itemDef)
    itemGroup["irefs"] = irefList
    igList.append(itemGroup)
    logging.info("Done %s", str(vsn))
    outputMetadata["igdef"] = itemGroup
    outputMetadata["bcCodeListDefs"] = bcCodeListDefs
    outputMetadata["itemdefs"] = idefList
    outputMetadata["methodslist"] = methodsList
    outputMetadata["comments"] = comments


    return outputMetadata

def writeXML(sdtmMetadata:dict):
    """

    :param sdtmMetadata: compiled metadata for all C360 domains
    :return:
    """
    domainmetadata = sdtmMetadata["DomainList"]


    prodVers = "SDTMIG-3-2"
    ODMdoc = minidom.Document()
    ODMdoc.toprettyxml(encoding="utf8")
    odmStudy = ODMdoc.createElementNS(odmURL, 'ODM')
    odmStudy.setAttribute('xmlns:def', defnsURI)
    odmStudy.setAttribute("xmlns:mdr", mdrnsURI)
    odmStudy.setAttribute('xmlns', odmURL)
    odmAttribs = createODMAttribs(prodVers)

    for k, v in odmAttribs.items():
        odmStudy.setAttribute(k, v)
        logging.info("ODM attribute %s: %s", k, v)

    StudyTop = ODMdoc.createElement("Study")
    GlobalVariables = ODMdoc.createElement("GlobalVariables")
    StudyName = ODMdoc.createElement("StudyName")
    studyNameText = ODMdoc.createTextNode("CDISC 360")  #C360 Biomat
    StudyName.appendChild(studyNameText)
    StudyDescription = ODMdoc.createElement("StudyDescription")
    studyDescriptionText = ODMdoc.createTextNode("CLIB BC Examples")  # Add In BC identification
    StudyDescription.appendChild(studyDescriptionText)
    ProtocolName = ODMdoc.createElement("ProtocolName")
    protocolName = ODMdoc.createTextNode("C360 WS1 BC Definitions")
    ProtocolName.appendChild(protocolName)
    GlobalVariables.appendChild(StudyName)
    GlobalVariables.appendChild(StudyDescription)
    GlobalVariables.appendChild(ProtocolName)
    studyOID = "[C360.Library.Example." + prodVers + "]"
    StudyTop.setAttribute("OID", studyOID)
    StudyTop.appendChild(GlobalVariables)

    MDV = ODMdoc.createElement("MetaDataVersion")
    MDV.setAttribute("OID", "MDV01")
    MDV.setAttribute("Name", "CDISC Library MetaData")
    MDV.setAttribute("def:DefineVersion", "2.1.0")
    MDV.setAttribute("xmlns:def", defnsURI)

    stdsDeclare = ODMdoc.createElement("def:Standards")
    igstd = ODMdoc.createElement("def:Standard")
    igstd.setAttribute("OID", igstdRef)
    igstd.setAttribute("Name", "SDTMIG")
    igstd.setAttribute("Type", "IG")
    igstd.setAttribute("Status", "Final")
    igstd.setAttribute("Version", C360_SDTMIG_Version)
    stdsDeclare.appendChild(igstd)
    assert isinstance(stdsDeclare, object)
    MDV.appendChild(stdsDeclare)
    """ Standard declaration for the BC Concepts"""

    for domain in domainmetadata:
        domainName = domain["domain"]
        bcConcepts = domain["bcconcepts"]
        for bc in bcConcepts:
            bcStdInfo = getBCStdInfo(bc)
            bcstd = ODMdoc.createElement("def:Standard")
            bcstd.setAttribute("OID", bcStdInfo["oid"])
            bcstd.setAttribute("Name", domainName + "-" + bcStdInfo["name"])
            bcstd.setAttribute("Type", bcStdInfo["type"])
            bcstd.setAttribute("Status", "Draft")
            bcstd.setAttribute("Version", "1-0")
            stdsDeclare.appendChild(bcstd)
            MDV.appendChild(stdsDeclare)
        """ bcvlm {"bcValueDefs":[],"wcDefs:[]} """

    wcDefs = []
    wcCount = 0
    for domain in domainmetadata:
        domainName = domain["domain"]
        bcConcepts = domain["bcconcepts"]
        if "VLDefs" in domain:
            vldefs = domain["VLDefs"]
            bcvlm = domain["bcvlm"]
            bcValueDefs = bcvlm["bcValueDefs"]
            bcwcDefs = bcvlm["wcDefs"]
            wcRefs = []
            vlmOrdinal = 1
            vlRefList = getVarList(bcValueDefs)
            for valVarName  in vlRefList:
                defValueDef = ODMdoc.createElement("def:ValueListDef")
                defValueDef.setAttribute("OID", "C360.VLM." + valVarName)
                valOrder = 1
                for bcName,bcValDef  in bcValueDefs.items():
                    bcIrefs = bcValDef["ItemRefs"]
                    if valVarName in bcIrefs:
                        ir = bcIrefs[valVarName]
                        ItemRef = ODMdoc.createElement("ItemRef")
                        ItemRef.setAttribute("ItemOID", ir["ItemOID"])
                        ItemRef.setAttribute("OrderNumber", str(valOrder))
                        valOrder += 1
                        ItemRef.setAttribute("Mandatory", "Yes")
                        if "MethodOID" in ir:
                            ItemRef.setAttribute("MethodOID", ir["MethodOID"])
                        if "C360AltMethodOID" in ir:
                            ItemRef.setAttribute("mdr:AltMethodOID", ir["C360AltMethodOID"])
                            ItemRef.setAttribute("xmlns:mdr",  mdrnsURI)
                        irWC = ODMdoc.createElement("def:WhereClauseRef")
                        irWC.setAttribute("WhereClauseOID", ir["WhereClauseOID"])
                        wcOID = ir["WhereClauseOID"]
                        logging.info("Adding WhereClause/@OID= " + wcOID)
                        if wcOID not in wcRefs:
                            wcRefs.append(wcOID)
                            wcDef = createWCdef(wcOID)
                            wcDefs.append(wcDef)
                            wcCount += 1
                        ItemRef.appendChild(irWC)
                        defValueDef.appendChild(ItemRef)
                    #print("wcCount " + str(wcCount) + " wcRefs " + str(len(wcRefs)))
                    MDV.appendChild(defValueDef)

    for domain in domainmetadata:
        domainName = domain["domain"]
        bcConcepts = domain["bcconcepts"]
        if "bcvlm" in domain:
            bcvlm = domain["bcvlm"]
            bcValueDefs = bcvlm["bcValueDefs"]
            bcwcDefs = bcvlm["wcDefs"]
            for wcdef in bcwcDefs:
                WhereClauseDef = ODMdoc.createElement("def:WhereClauseDef")
                #wcdef = wcDefs[wc]
                logging.info("Adding def:WhereClauseDef@OID= %s.", wcdef["OID"])
                WhereClauseDef.setAttribute("OID", wcdef["OID"])
                rangeChecks = wcdef["rangeChecks"]
                for rc in rangeChecks:
                    RangeCheck = ODMdoc.createElement("RangeCheck")
                    RangeCheck.setAttribute("SoftHard", "Soft")
                    RangeCheck.setAttribute("Comparator", "EQ")
                    RangeCheck.setAttribute("def:ItemOID", rc["varOID"])
                    CheckVal = ODMdoc.createElement("CheckValue")
                    cvaltext = ODMdoc.createTextNode(rc["chkVal"])
                    CheckVal.appendChild(cvaltext)
                    RangeCheck.appendChild(CheckVal)
                    WhereClauseDef.appendChild(RangeCheck)
                MDV.appendChild(WhereClauseDef)


    nIG = 0
    for domain in domainmetadata:
        ig = domain["igdef"]
        logging.info("Creating ItemGroup Def for %s", ig["OID"])
        dataStructure = ODMdoc.createElement('ItemGroupDef')
        dataStructure.setAttribute("OID", ig["OID"])
        dataStructure.setAttribute("Name", ig["Name"])
        dataStructure.setAttribute("Purpose", ig["Purpose"])
        if ig["Name"] == "DM":
            dataStructure.setAttribute("Repeating", "No")
        else:
            dataStructure.setAttribute("Repeating", "Yes")
        dataStructure.setAttribute("def:Structure", ig["defStructure"])
        dataStructure.setAttribute("def:StandardOID", ig["defStandardOID"])
        description = ODMdoc.createElement('Description')
        transText = ODMdoc.createElement("TranslatedText")
        ltext = ODMdoc.createTextNode(ig["Label"])
        transText.appendChild(ltext)
        description.appendChild(transText)
        dataStructure.appendChild(description)
        defClass = ODMdoc.createElementNS(defnsURI, "def:Class")

        defClass.setAttribute("Name", classTerminology[ig["Class"]])

        irefList = ig["irefs"]
        for iref in irefList:
            itemRef = ODMdoc.createElement('ItemRef')
            itemRef.setAttribute("ItemOID", iref["ItemOID"])
            itemRef.setAttribute("OrderNumber", iref["OrderNumber"])
            libCore = iref["mdrCore"]
            if (libCore == "Req"):
                itemRef.setAttribute("Mandatory", "Yes")
            else:
                itemRef.setAttribute("Mandatory", "No")
            itemRef.setAttribute("mdr:Core", iref["mdrCore"])
            itemRef.setAttribute("xmlns:mdr", mdrnsURI)
            itemRef.setAttribute("Role", iref["Role"])
            if "MethodOID" in iref:
                itemRef.setAttribute("MethodOID", iref["MethodOID"])
            if "C360AltMethodOID" in iref:
                itemRef.setAttribute("mdr:AltMethodOID", iref["C360AltMethodOID"])

            logging.info("ItemRef[%s]", iref["ItemOID"])
            dataStructure.appendChild(itemRef)
        dataStructure.appendChild(defClass)
        MDV.appendChild(dataStructure)

        nIG = nIG + 1

    for domain in domainmetadata:
        idefList = domain["itemdefs"]
        for idef in idefList:
            logging.info("Creating ItemDef[%s]", idef["OID"])
            itemDef = ODMdoc.createElement('ItemDef')
            itemDef.setAttribute("OID", idef["OID"])
            itemDef.setAttribute("Name", idef["Name"])
            if idef["DataType"] == "ISO 8601":
                itemDef.setAttribute("DataType", "datetime")
            else:
                itemDef.setAttribute("DataType", idef["DataType"])
            itemDef.setAttribute("Length", "50")
            if (idef["DataType"] == "Char"):
                itemDef.setAttribute("DataType", "text")
                itemDef.setAttribute("Length", "50")
            elif (idef["DataType"] == "Num"):
                itemDef.setAttribute("DataType", "float")
            if "commentOID" in idef:
                itemDef.setAttribute("def:CommentOID", idef["commentOID"])
            itemDef.setAttribute("xmlns:def", defnsURI)
            if "label" in idef:
                description = ODMdoc.createElement('Description')
                transText = ODMdoc.createElement("TranslatedText")
                ltext = ODMdoc.createTextNode(idef["label"])
                transText.appendChild(ltext)
                description.appendChild(transText)
                itemDef.appendChild(description)
            if "Label" in idef:
                description = ODMdoc.createElement('Description')
                transText = ODMdoc.createElement("TranslatedText")
                ltext = ODMdoc.createTextNode(idef["Label"])
                transText.appendChild(ltext)
                description.appendChild(transText)
                itemDef.appendChild(description)
            if "CodeListOID" in idef:
                CodeListRef = ODMdoc.createElement('CodeListRef')
                CodeListRef.setAttribute("CodeListOID", idef["CodeListOID"])
                itemDef.appendChild(CodeListRef)
            if "OriginType" in idef:
                otype = idef["OriginType"]
                defOrigin = ODMdoc.createElement("def:Origin")
                defOrigin.setAttribute("Type", otype)
                if otype == "Predecessor":
                    description = ODMdoc.createElement('Description')
                    transText = ODMdoc.createElement("TranslatedText")
                    ltext = ODMdoc.createTextNode(idef["OriginPredecessor"])
                    transText.appendChild(ltext)
                    description.appendChild(transText)
                    defOrigin.appendChild(description)
                elif otype == "Assigned":
                    itemDef.setAttribute("def:CommentOID", idef["CommentOID"])

                itemDef.appendChild(defOrigin)
            if "vlRef" in idef:
                ValueListRef = ODMdoc.createElement("def:ValueListRef")
                ValueListRef.setAttribute(("ValueListOID"), idef["vlRef"])
                itemDef.appendChild(ValueListRef)
            MDV.appendChild(itemDef)

    for cl in codelists:
        """  Codelistrefs with an OID that begins with CL. are directly from the CDISC LIbrary.
        Remove the "CL." then find the codelist definition from the codelists list.  (array of cdDefs with href)
        Each codelist in the codelists list has 3 elements "name", "href", "terms".  
        
        Add handling for codelists with a cloid beginning with "C360." there are 2 types value descriptions and CDVals.
         """
        if "href" in cl:
            clOID =  cl["href"]
        elif "cloid" in cl:
            clOID = cl["cloid"]
        CodeListDef = ODMdoc.createElement('CodeList')
        CodeListDef.setAttribute("OID", clOID)
        CodeListDef.setAttribute("Name", cl["name"])
        if clOID.startswith("CL.") or clOID.startswith("/"):  #variable level codelists with no bc specification
            logging.debug("Adding Codelist " , clOID)
            hasAlias = False
            clLibName = cl["name"]
            clibNameParts = cl["name"].split("(")
            if len(clibNameParts) < 2:
                CodeListDef.setAttribute("Name", clibNameParts[0])
                hasAlias = False
            else:
                CodeListDef.setAttribute("Name", clibNameParts[0])
                hasAlias = True
            CodeListDef.setAttribute("DataType", "text")
            if "terms" not in cl:
                if "CDVal" in cl and "subset" in cl:
                    termlist = []
                    for cli in clCDVal2Items(cl["CDVal"]):
                        terminfo = {}
                        parenpos = cli.find("(")
                        if parenpos > 0:
                            terminfo['submissionValue'] = cli[parenpos:].strip(" ")
                            endparenpos = cli.find(")")
                            terminfo["conceptID"] = cli[parenpos+1:endparenpos]
                            termlist.append(terminfo)
                        else:
                            terminfo['submissionValue'] = cli.strip(" ")
                            termlist.append(terminfo)
                    cl["terms"] = termlist
                elif "CDVal" in cl:
                    cl["terms"] = clCDVal2Items(cl["CDVal"])
                continue
            for cli in cl["terms"]:
                EnumeratedItem = ODMdoc.createElement("EnumeratedItem")
                if "submissionValue" in cli:
                    logging.debug("Adding Codelist Items for " + cli["submissionValue"])
                    EnumeratedItem.setAttribute("CodedValue", cli["submissionValue"])
                else:
                    EnumeratedItem.setAttribute("CodedValue", cli)
                if hasAlias:
                    CodeAlias = ODMdoc.createElement("Alias")
                    CodeAlias.setAttribute("Context", "nci:ExtCodeID")
                    CodeAlias.setAttribute("Name", cli["conceptId"])
                    EnumeratedItem.appendChild(CodeAlias)
                CodeListDef.appendChild(EnumeratedItem)
            if hasAlias:
                clAlias = ODMdoc.createElement("Alias")
                clAlias.setAttribute("Context", "nci:ExtCodeID")
                clAlias.setAttribute("Name", clibNameParts[1])
                CodeListDef.appendChild(clAlias)
            MDV.appendChild(CodeListDef)
        elif clOID.startswith("C360.CL.BC."):  # has clib codelist with a bc specification
            cldef = getClibCLDef(clOID, codelists)
            CodeListDef.setAttribute("Name", cldef["name"])
            CodeListDef.setAttribute("DataType", "text")
            if "subset" in cl:
                CodeListDef.setAttribute("mdr:Subset", "Yes")
                CodeListDef.setAttribute("xmlns:mdr", mdrnsURI)
            hasAlias = False
            for cli in cldef["terms"]:
                #print(cli)
                #print("Adding Codelist Items for cl " + clOID )
                EnumeratedItem = ODMdoc.createElement("EnumeratedItem")
                EnumeratedItem.setAttribute("CodedValue", cli)
                if "defaultVal" in cl:
                    if cli == cl["defaultVal"]:
                        EnumeratedItem.setAttribute("mdr:isDefault", "Yes" )
                        EnumeratedItem.setAttribute("xmlns:mdr", mdrnsURI)
                CodeListDef.appendChild(EnumeratedItem)
            MDV.appendChild(CodeListDef)
        elif clOID.startswith("C360.CL./"):
            # this means either it's a describedValue
            clibhref = clOID[7:]  # this is the href as  reported by the library
            if clibhref.startswith("/"):
                clClibDef = getClibCLDef(clibhref, codelists)
                if clClibDef is None:
                    logging.error("Expected to find Codelist " + clibhref)
                    exit()
                c360Cldef = getClibCLDef(clOID, codelists)
                if c360Cldef is None:
                    #print("Expected to find Codelist " + clOID)
                    exit()
                elif "href" in c360Cldef:
                    c360href = c360Cldef["href"]
                    if c360href[7:] != clibhref:
                        #print("Expected Clib Href " + clibhref +  " should be the same as C360 Href " + c360href)
                        exit()
                clNameParts = clClibDef["name"].split("(")
                if len(clNameParts) < 2:
                    #CodeListDef.setAttribute("Name", clNameParts[0])
                    hasAlias = False
                else:
                    #CodeListDef.setAttribute("Name", clNameParts[0])
                    hasAlias = True
                CodeListDef.setAttribute("DataType", "text")
                CodeListDef.setAttribute("Name", c360Cldef["name"])

                # check how the href val is set                                     clDef["href"] = clOID (C360cl./
                # The terms list will come from the CDVal -- and so will not be the
                for cli in c360Cldef["terms"]:
                    # first see if there is a c-code in the text
                    cliParts = cli.split("(")
                    hasAlias = False
                    if len(cliParts) > 1:
                        hasAlias = True
                    codevalue = cliParts[0].lstrip(" ").rstrip(" ")
                    enumeratedItem = ODMdoc.createElement("EnumeratedItem")
                    enumeratedItem.setAttribute("CodedValue", codevalue)
                    if hasAlias:
                        ccodeParts = cliParts[1].split(")")
                        if len(ccodeParts) < 2:
                            #print("Expected (c-code) " + ccodeParts[0])
                            exit()
                        ccode = ccodeParts[0]
                        alias = ODMdoc.createElement("Alias")
                        alias.setAttribute("Context", "nci:ExtCodeID")
                        alias.setAttribute("Name", ccode)
                        enumeratedItem.appendChild(alias)
                    CodeListDef.appendChild(enumeratedItem)
                    #print("Term from CDVal ")
                    #print(cli)
                if  len(clNameParts) >= 2:
                    clAlias = ODMdoc.createElement("Alias")
                    clAlias.setAttribute("Context", "nci:ExtCodeID")
                    clAlias.setAttribute("Name", clNameParts[1])
                    CodeListDef.appendChild(clAlias)
                MDV.appendChild(CodeListDef)
        elif clOID.startswith("C360.BC.CDVal."):
            # THis is the case where there is no Clib definition but there is a CDVal. in this case the href will end with the varname
            clDef = getClibCLDef(clOID, codelists)
            clname = clDef["name"]
            href = clDef["href"]
            if clname.endswith("_C360") and href.startswith("C360.CDVal."):
                if clname[:-5] != href[11:]:
                    #print("Expected same varname in Name and href" + clname[:-4] + href[10:])
                    exit()
            CodeListDef.setAttribute("DataType", "text")
            CodeListDef.setAttribute("Name", clname)
            # in this case, if there is an alias, it is taken directly from the string for the terms
            for cli in clDef["terms"]:
                cliParts = cli.split("(")
                hasAlias = False
                if len(cliParts) > 1:
                    hasAlias = True
                codevalue = cliParts[0].lstrip(" ").rstrip(" ")
                enumeratedItem = ODMdoc.createElement("EnumeratedItem")
                enumeratedItem.setAttribute("CodedValue", codevalue)
                if hasAlias:
                    ccodeParts = cliParts[1].split(")")
                    if len(ccodeParts) < 2:
                        #print("Expected (c-code) " + ccodeParts[0])
                        exit()
                    ccode = ccodeParts[0]
                    alias = ODMdoc.createElement("Alias")
                    alias.setAttribute("Context", "nci:ExtCodeID")
                    alias.setAttribute("Name", ccode)
                    enumeratedItem.appendChild(alias)
                CodeListDef.appendChild(enumeratedItem)
                #print("Term from CDVal ")
                #print(cli)
            MDV.appendChild(CodeListDef)
        elif clOID.startswith("C360."):
            # this is a described value domain.
            clDef = getClibCLDef(clOID, codelists)
            if clDef is None:
                #print("Expected to find  codelist " + clOID)
                exit()
            CodeListDef.setAttribute("DataType", "text")
            CodeListDef.setAttribute("Name", clDef["name"])
            if len(clDef["terms"]) != 0:
                print("Described Value Codelist should not have a list of terms CodeList[" + clOID + "].Name=" + clDef["name"])
            externalCodeList = ODMdoc.createElement("ExternalCodeList")
            externalCodeList.setAttribute("Dictionary", clDef["name"])
            externalCodeList.setAttribute("Version", "Current - as of " + str(cdt.year) + "-" + str(cdt.month).zfill(2) + "-" + str(cdt.day).zfill(2))
            externalCodeList.setAttribute("href", cloid2href(clOID))
            CodeListDef.appendChild(externalCodeList)
            MDV.appendChild(CodeListDef)


    for domain in domainmetadata:
        methodsList = domain["methodslist"]
        for mDef in methodsList:
            #print(mDef)
            mthoid = mDef["OID"]
            MethodDef =  ODMdoc.createElement('MethodDef')
            MethodDef.setAttribute("OID", mthoid)
            MethodDef.setAttribute("Name", mDef["Name"])
            MethodDef.setAttribute("Type", "Computation")
            methoddef = mDef["Definition"]
            if "Preferred" in methoddef:
                MethodDef.setAttribute("mdr:Preferred", methoddef["Preferred"])
            MethodDef.setAttribute("xmlns:mdr", mdrnsURI)
            description = ODMdoc.createElement("Description")
            transText = ODMdoc.createElement("TranslatedText")
            ltext = ODMdoc.createTextNode(methoddef["Description"])
            transText.appendChild(ltext)
            description.appendChild(transText)
            inputvars = methoddef["InputVariables"]
            MethodDef.appendChild((description))
            InputVars = ODMdoc.createElementNS(mdrnsURI,"mdr:InputVariables")
            InputVars.setAttribute("xmlns:mdr", mdrnsURI)
            for invar in inputvars:
                inputVariable = ODMdoc.createElementNS(mdrnsURI, "mdr:InputVariable")
                inputVariable.setAttribute("xmlns:mdr", mdrnsURI)
                inputVariable.setAttribute("SourceStandard", invar["Standard"])
                inputVariable.setAttribute("Domain", invar["Domain"])
                inputVariable.setAttribute("VarName", invar["VarName"])
                InputVars.appendChild(inputVariable)
            MethodDef.appendChild(InputVars)
            MDV.appendChild(MethodDef)

    for domain in domainmetadata:
        if "comments" in domain:
            comments = domain["comments"]
            nc = 0
            for com in comments:
                commentDef = ODMdoc.createElementNS(defnsURI, 'def:CommentDef')
                commentDef.setAttribute("xmlns:def", defnsURI)
                commentDef.setAttribute("OID", com["OID"])
                description = ODMdoc.createElement("Description")
                transText = ODMdoc.createElement("TranslatedText")
                ltext = ODMdoc.createTextNode(com["Description"])
                transText.appendChild(ltext)
                description.appendChild(transText)
                commentDef.appendChild(description)
                MDV.appendChild(commentDef)
                nc = nc + 1
        else:
            ig = domain["igdef"]
            print("No comments in " + ig["Name"])

    StudyTop.appendChild(MDV)
    odmStudy.appendChild(StudyTop)
    ODMdoc.appendChild(odmStudy)
    fn =  "C360define.xml"
    outfile = open(fn, "w")
    ODMdoc.writexml(outfile)
    outfile.close
    print("Look for output in ", fn)


def createODMAttribs(prodVers: str) -> dict:
    # build dict with creationDT, FileOID, FileType, Granularity

    #cdt = datetime.datetime.now()
    creationDT = cdt.isoformat()
    odmRootAttribs = {}
    odmRootAttribs['CreationDateTime'] = creationDT
    odmRootAttribs['FileOID'] = '[CDISC LIBRARY- ' + prodVers + ']'
    odmRootAttribs['FileType'] = 'Snapshot'
    odmRootAttribs['def:Context'] = 'Other'

    return odmRootAttribs


def getDomainClass(domainMD, bcInfo: dict) -> str:
    dmClass = ""
    parentInfo = bcInfo["parent"]
    domainPrefix = parentInfo.split("-")[0]
    bcKey = domainPrefix + "_bcConcepts"
    for dm in domainMD["domainList"]:
        if dm["Name"] == domainPrefix:
            return dm["Class"]
    return dmClass


def bcVarName(clibRef: dict) -> str:
    selfRef = clibRef["self"]
    varHrefParts = selfRef["href"].split("/")
    usePart = len(varHrefParts) - 1
    return varHrefParts[usePart]


def bcHasCL(clibRef: dict) -> bool:
    if "codelist" in clibRef:
        return True
    return False


def bcCLRef(clibRef: dict) -> str:
    clL = clibRef["codelist"]
    clref = clL[0]
    return clref["href"]

def getDataType(clibRef: dict) -> str:
    default = "text"
    #print(clibRef)
    label = clibRef["label"]
    if "describedValueDomain" in clibRef:
        if clibRef["describedValueDomain"] == "ISO 8601":
            return "datetime"
    simpleType = clibRef["simpleDatatype"]
    if simpleType == "Char":
        return default
    elif simpleType == "Num":
        return "integer"
    return default



def createWCdef(wcoid: str) -> dict:
    wcDef = {}
    wcOIDParts = wcoid.split(".")
    chkvalPart = len(wcOIDParts) - 1
    varNamePart = chkvalPart - 1
    chkval = wcOIDParts[chkvalPart]
    whereVal = wcOIDParts[varNamePart]
    # print("WC OID " + wcoid)
    wcDef["OID"] = wcoid
    wcDef["WhereVar"] = whereVal
    wcDef["CheckVal"] = chkval
    return wcDef

def oid2Name(vlmOid) ->str:
    oidparts = vlmOid.split(".")
    namePart = len(oidparts)-1
    return oidparts[namePart]

def cdVal2bcCLDef(cloid, bcname, bcCDVal:dict) ->dict:
    bcCLDef = {}
    if bcCDVal is None:
        return
    bcCLDef["cloid"] = cloid
    bcCLDef["name"] = bcname  + "_C360"
    #print("CodeList[@" + cloid + "] has @name " +  bcname + ".")
    #print(bcCDVal)
    if "subset" in bcCDVal:
        bcCLDef["CDVal"] = bcCDVal["subset"]
        bcCLDef["subset"] = True
        if "default" in bcCDVal:
            bcCLDef["defaultVal"] = bcCDVal["default"]
    elif "CDVal" in bcCDVal:
        bcCLDef["CDVal"] = bcCDVal["CDVal"]
    elif "default" in bcCDVal:
        bcCLDef["CDVal"] = bcCDVal["default"]
    elif "value" in bcCDVal:
        bcCLDef["CDVal"] = bcCDVal["value"]
    return bcCLDef

def hasbccl(vname:str, bcConcepts:list) -> bool:
    retval = False
    for bcConcept in bcConcepts:
        bcvl = bcConcept["bcVarList"]
        for bcvar in bcvl:
            if bcvar["DEC"] == vname:
                bcvarclibref = bcvar["ClibRef"]
                if "codelist" in bcvarclibref:
                    bcCodelistRef = bcvarclibref["codelist"]
                    nCLs = len(bcConcepts)
                    if nCLs >1:
                        print("Too many codelists for 360. Expected 1 found " + nCLs)
                    return True
                else:
                    return retval
    return retval


def hasCDVal(vname:str, bcConcepts:list) ->bool:
    retval = False
    for bcConcept in bcConcepts:
        bcvl = bcConcept["bcVarList"]
        for bcvar in bcvl:
            if bcvar["DEC"] == vname:
                bcvarclibref = bcvar["ClibRef"]
                if "CDVal" in bcvarclibref:
                    bcDeval = bcvarclibref["CDVal"]
                    return True
                else:
                    return retval
    return retval



def bcclOID(vname:str, bcConcepts:list) -> str:
    if len(bcConcepts) != 1:
        # TODO: list handling
        return

    bcDef = bcConcepts[0]
    bcName = bcDef["bcName"]
    bcVarlist = bcDef["bcVarList"]
    for bcvar in bcVarlist:
        if vname == bcvar["DEC"]:
            clibRef = bcvar["ClibRef"]
            CDVal = bcvar["CDVal"]
            if "codelist" in clibRef and CDVal is not None:
                clList = clibRef["codelist"]
                cl = clList[0]
                if "href" in cl:
                    clOID = "C360.CL." + cl["href"]
                    return clOID
            elif "CDVal" not in bcvar:
                clList = clibRef["codelist"]
                cl = clList[0]
                if "href" in cl:
                    """ If there is no CDVAL in the cmap, just use the standard codelist definition"""
                    clOID = "CL." + cl["href"]
                    return clOID
    print("vname " + vname + " No codelist definition available.")

def bcCDVal2TermsList(varname:str, bcConcepts:list, forBC="default") -> list:
    bcDef = bcConcepts[0]
    if forBC != "default":
        for bcc in bcConcepts:
            if forBC == bcc["bcName"]:
                bcDef = bcc

    bcName = bcDef["bcName"]
    bcVarlist = bcDef["bcVarList"]
    terms = []
    for bcvar in bcVarlist:
        if varname == bcvar["DEC"] and "CDVal" in bcvar:
            cdval = bcvar["CDVal"]
            if "value" in cdval:
                terms.append(cdval["value"])
            elif "subset" in cdval:
                terms = clCDVal2Items(cdval["subset"])
            else:
                print("bcCDVal2TermsList: ")
                print(cdval)
            return terms
    print("bcCDVal2TermsList: did not find a CDVal for " + varname + " in " + bcName)
    return

def clCDVal2Items(instr) ->list:
    itemList = instr.split(";")
    #print(instr + " has " + str(len(itemList)) + " items.")
    return itemList

def makeComment(oid, text) -> dict:
    commentDef = {}
    commentDef["OID"] =  oid
    commentDef["Description"] = text
    return commentDef

def isFindings(domainName, varset:dict) ->bool:
    if varset["Class"] == "Findings":
                return True
    return False

def isEvent(domainName, varset:dict) -> bool:
    if varset["Class"] == "Events":
                return True
    return False


def isIntervention(domainName, varset:dict) -> bool:
    if varset["Class"] == "Interventions":
                return True
    return False

def hasVarMapping(varname, mappings:dict)-> bool:
    count = 0
    for k in mappings:
        mappingLabel = k
        #print("MappingLabel: " +  mappingLabel)
        mlParts = mappingLabel.split("-from-CDASH")
        if len(mlParts) == 0:
            return False
        mapVar = mlParts[0]
        #print("mapVar = " + mapVar + " varName " + varname + ".")
        if varname == mapVar:
            if len(mlParts) == 1:
                #print(mapVar)
                return True
            else:
                mapSrc = mlParts[1]
                srcParts = mapSrc.split("_")
                if len(srcParts) == 1:
                    #print(mapVar + ":" + mapSrc)
                    return True

    return False


def getVarMapping(varname, mappings:dict)-> dict:
    mapping: Dict[str, dict] = {}
    for k in mappings:
        mappingLabel = k
        mlParts = mappingLabel.split("-from-CDASH")
        if len(mlParts) == 2:
            mapVar = mlParts[0]
            mapSrc = mlParts[1]
            if varname == mapVar:  #need to distinguish between variable and value level mappings
                srcParts = mapSrc.split("_")
                if len(srcParts) == 0:   # not sure this can even happen
                    print(" mapping source: " + mapSrc)
                    mapping[mapVar] = mappings[k]
                    return mapping
                elif len(srcParts) == 1:
                    mapping[mapVar] = mappings[k]
                    return mapping
        elif len(mlParts) == 1:
            mapVar = mappingLabel
            mapping[mapVar] = mappings[k]

    return mapping

def hasVarValMapping(bcvarname, bcname, mappings) ->bool:
    # In the mappings file the mapping labels have the format bcname_bcvarname
    # The key for the mapping definition in the returned dict will be bvarname - bcval
    mapping: Dict[str, dict] = {}
    matchSuffix = bcname.upper() + "_" + bcvarname.upper()
    count = 0
    for k in mappings:
        mappingLabel = k
        if mappingLabel.endswith(matchSuffix):
            return True
    return False

def getVarValMapping(bcvarname, bcname, mappings) ->dict:
    # In the mappings file the mapping labels have the format bcname_bcvarname
    # The key for the mapping definition in the returned dict will be bvarname - bcval
    mapping: Dict[str, dict] = {}
    matchSuffix = bcname.upper() + "_" + bcvarname.upper()
    mapKey = bcvarname.upper() + "-" + bcname.upper()
    for k in mappings:
        mappingLabel = k
        if mappingLabel.endswith(matchSuffix):
            mapping[mapKey] = mappings[k]
    return mapping


def set_cmd_line_args():
    """
    Example -c xx_bcConcepts.json -l xx_sdtmClib.json -d XX

    """
    parser = argparse.ArgumentParser(description="Generate Define-XML for domain with bcs and mappings.")
    parser.add_argument("-s", dest="bcInfo", help="Json file with bc definitions.", default="XX_bcConcepts.json")
    parser.add_argument("-l", dest="clibInfo", help="Json file with SDTM Clib information.", default="XX_sdtmClib.json")
    parser.add_argument("-d", dest="domainPrefix", help="Doman Name.", default="All")
    args= parser.parse_args()
    return args

def getJsonInfo(jsonFileName) -> dict:
    fname = os.path.join(os.path.realpath("."), jsonFileName)
    f = open(fname, "r")
    return json.load(f)

def getClibCLDef(cloid:str, codelists:list) -> dict:
    """

    :param cloid:
    :param codelists: this is really the bc codelist definition
    :return:
    """
    #print("Clib lookup " + cloid )
    clDef = {}
    for cldef in codelists:
        if "href" not in cldef:
            print("getClibCLDef: Expect href in codelist structure.")
            print(cldef)
            exit()
        if cloid == cldef["href"]:
            return cldef
    return

def domainCLDef(cloid:str, codelists:list) ->dict:
    """

    :param cloid:
    :param codelists: library codelist definition.
    :return:
    """
    cldef = {}
    for cl in codelists:
        if cloid[3:] == cl["href"]:
            cldef["name"] = cl["name"]
            cldef["href"] = cloid
            cldef["terms"] = cl["terms"]
            return cldef
    return cldef




def getBCCLDef(cloid:str, bcCodelists:list) ->dict:
    print("BC cl lookup " + cloid)
    bcCLdef = {}
    for bccldef in bcCodelists:
        if cloid == bccldef["cloid"]:
            return bccldef
    return

def getRootCLName(cloid, codelists) -> str:
    if not cloid.startswith("/"):
        print("incorrectly formatted href" + cloid)
        exit()
    for cl in codelists:
        if "href" in cl:
            if cl["href"] == cloid:
                return cl["name"]
    return cloid

def cloid2href(cloid:str)->str:
    startpos = cloid.find("/")
    return cloid[:startpos]



def bcInfo2VLM(domain, domain_bcConcept:list)->dict:
    # if the bcConcept structure is broken raise exception
    # return structure will have VLM structures populated
    # vldefs, wcDefs, vlIdefs
    # summary metadata
    bcvlm = {}
    bcvlm["vlDefs"] = []

    bcvlm["wcDefs"] = getWCDefs(domain, domain_bcConcept)
    bcvlm["vlIdefs"] = []
    bcvlm["clRefs"] = []
    bcvlm["methodDefs"] = []

    return bcvlm

def getBCStdInfo(domain_bcConcept:dict) -> dict:
    bcstdinfo = {}
    bcstdinfo["oid"] = "C360.std."+  domain_bcConcept["bcID"]
    bcstdinfo["name"] = domain_bcConcept["bcLabel"]
    bcstdinfo["type"] = "C360 Biomedical Concept"
    return bcstdinfo

def bcCond2OID(bcID:str, bcCond:str) ->str:
    bcCondList = bcCond.split(" ")
    condVarName = bcCondList[0]
    condChkVal = bcCondList[len(bcCondList)-1]
    strPref = "C360.WC." + bcID + "." + condVarName + "." + condChkVal
    return strPref

def getbcCondVars(bcCond:list) ->str:
    pref = "."
    s = ""
    for wcv in bcCond:
        s = s + wcv["varName"] + "."
    return pref + s


def getWCDefs(domain, bcConcepts:list) ->list:
    wcDefs = []
    for bc in bcConcepts:
        wcDef = {}
        bcID = bc["bcID"]
        bcCond = bc["bcCond"]
        bcCondList = bcCond.split(" ")
        wcOID = bcCond2OID(bcID, bcCond)
        rangeChecks = []
        rc = {}
        rc["varOID"] = "C360." + domain + ".IT." + bcCondList[0]
        rc["chkVal"] = bcCondList[len(bcCondList)-1]
        rangeChecks.append(rc)
        wcDef["OID"] = wcOID
        wcDef["rangeChecks"] = rangeChecks
        wcDefs.append(wcDef)
    return wcDefs

def hasOrigin(vname, bcConcepts:list) ->bool:
    # If there is more than bcConcept, the origin is added only in the value level metadata
    # If there is only 1 bcConcept, it will be added at the variable level
    retval = False
    if len(bcConcepts) != 1:
        return retval
    bcDef = bcConcepts[0]
    #
    bcDef = bcConcepts[0]
    bcName = bcDef["bcName"]
    bcVarlist = bcDef["bcVarList"]
    for bcvar in bcVarlist:
        if vname == bcvar["DEC"] and "origin" in bcvar:
            return True
    return retval

def getOrigin(vname, bcConcepts:list) ->dict:
    if len(bcConcepts) != 1:
        return
    #this is called only when hasOrigin returns True.
    bcDef = bcConcepts[0]
    bcName = bcDef["bcName"]
    bcVarlist = bcDef["bcVarList"]
    for bcvar in bcVarlist:
        if vname == bcvar["DEC"] and "origin" in bcvar:
            return bcvar["origin"]
    return

def getVarList(bcVlm:dict) -> list:
    varList = []
    for k, v in bcVlm.items():
        bIrefs = v["ItemRefs"]
        for varName, varInfo in bIrefs.items():
            if varName not in varList:
                varList.append(varName)
    print("Number of VL defs " + str(len(varList)))
    return varList

def getBcCondVar(bcCond:str)->str:
    # for C360 the bcCond has the form varName EQ Value
    condExprList = bcCond.split(" ")
    return condExprList[0]


if __name__ == "__main__":
    main()