# C360WriteDefXML
#
# The MIT License (MIT)
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

# TO DO (09-26-2019: adapt to either ADaM or SDTM input)
from typing import Dict
from xml.dom import minidom
import sys
import json, datetime, time, logging

# called from c360LibraryTools to generate Define-XML from 360 BC library content

odmURL = 'http://www.cdisc.org/ns/odm/v1.3'
defnsURI = 'http://www.cdisc.org/ns/def/v2.1'
mdrDefURL = 'http://www.cdisc.org/ns/LIBRARY-Define/v1.0'
mdrURL = 'http://www.cdisc.org/ns/LIBRARY-XML/v1.0'
mdrnsURI = "https://www.cdisc.org/ns/mdr/c360"


def codeList(clOID, varName,  cdval:dict, addCcode=False) -> dict:
	cl = {}
	cl["OID"] = clOID
	cl["Name"] = varName
	cl["DataType"] = "text"
	if addCcode:
		cl["C-code"] = cloid2Ccode(clOID)

	cl["bcsubset"] = False
	if "subset" in cdval or "value" in cdval:
		cl["bcsubset"] = True
	if "value" in cdval:
		if "MedDRA" in cdval["value"]:
			cl["Dictionary"] = cdval["value"]
			return cl
	cl["enum"] = cdval2ItemList(cdval)
	return cl



def writeXML(defInfo: dict):
	""":param defInfo: Structure containing bc content to be displayed.
	The output is an ODM file for a single CDASH Domain.  Most domains have just one BC.
	BC's contain information about datatypes, codelist subsets and derivations.
	Note: some bc variables have multiple codelists defined-only one will be included.
	For bc varaibles that have a 'CDVal', the ODM codelist will include only the terms provided by the CDVal.
	For bc variables without a CDVal, the codelist will be defined as an external codelist.

	:return: """

	prodVers = defInfo["ProdVersion"]
	domain = defInfo["parent"]
	conceptListName  = domain + "_bcConcepts"
	bcConceptsList = defInfo[conceptListName]
	prodTitle =   domain + " CDISC 360 Data Collection Requirements"
	ODMdoc = minidom.Document()
	odmStudy = ODMdoc.createElementNS(odmURL, 'ODM')
	odmStudy.setAttribute("xmlns:mdr", mdrnsURI)
	odmStudy.setAttribute('xmlns', odmURL)
	odmAttribs = createODMAttribs(prodVers)
	
	for k, v in odmAttribs.items():
		odmStudy.setAttribute(k, v)
		logging.info("ODM attribute %s: %s", k, v)
	
	StudyTop = ODMdoc.createElement("Study")
	GlobalVariables = ODMdoc.createElement("GlobalVariables")
	StudyName = ODMdoc.createElement("StudyName")
	studyNameText = ODMdoc.createTextNode(prodTitle)
	StudyName.appendChild(studyNameText)
	StudyDescription = ODMdoc.createElement("StudyDescription")
	studyDescriptionText = ODMdoc.createTextNode("CLIB BC Examples")
	StudyDescription.appendChild(studyDescriptionText)
	ProtocolName = ODMdoc.createElement("ProtocolName")
	protocolName = ODMdoc.createTextNode("C360 WS1 BC Listing")
	ProtocolName.appendChild(protocolName)
	GlobalVariables.appendChild(StudyName)
	GlobalVariables.appendChild(StudyDescription)
	GlobalVariables.appendChild(ProtocolName)
	studyOID = "[C360.Library.Example." + prodVers + "]"
	StudyTop.setAttribute("OID", studyOID)
	StudyTop.appendChild(GlobalVariables)
		
	MDV = ODMdoc.createElement("MetaDataVersion")	
	igstdRef = "CDISCLIB." + prodVers
	MDV.setAttribute("OID", igstdRef)
	MDV.setAttribute("Name", "CDISC 360 Library MetaData")
	stdDesc = prodVers
	MDV.setAttribute("Description", stdDesc)
	
	frmList = []
	igList = []
	idefList = []
	nStructures = len(bcConceptsList)
	structVarsetList = []
	vsn = 0
	vsList = []
	comments = []
	codelistRefs = []
	codelists = []
	methods = []
	# TODO: manage multiple VS and LB case with multiple set of VLM
	#  If there are multiple sets of VLM for a domain set it up with VarsetInfoLists as a list
	#  and set up with each IG matching a set of VLM 
	# Currently bcConceptsList is a single item list.
	# Read in file bcName.json. The key domain_bcConcepts has a list of the bcConcepts.
	# Each Concept has the a "bcTestCD" key and a bcVarList. It will be represented in the CDASH ODM as an ItemGroupDef.

	for bc in bcConceptsList:
		# vsList = bcConceptsList[ln]
		c360OID	=  bc["bcID"]
		c360Name = bc["bcName"]
		c360Label = bc["bcLabel"]
		#dsClass = bc["Class"]
		#c360Class = dsClass["title"]

		# for each bcConcept, create a form and the corresponding ItemGroup, ItemGroupRef, with an ItemDef for each DEC in teh bcVarList
		formDef = {}
		formDef["OID"] = "FRM." + c360OID
		formDef["Name"] = c360Name + " Form"
		if domain != "DM" :
			formDef["Repeating"] = "Yes"
		else:
			formDef["Repeating"] = "No"
		itemGroupRefs = []
		itemGroupRef = {}
		# Need to make both an ItemGroupRef and an ItemGroupDef
		# for each bc

		itemGroupDef = {}
		itemGroupDef["OID"] = "IG." + c360OID
		itemGroupDef["Name"] = c360Name + " Item Group"
		itemGroupDef["Label"] = c360Label
		# todo: designate distinct value for purpose. Set in calling program.
		itemGroupDef["Domain"] = domain
		itemGroupDef["Purpose"] = "C360 Biomedical Concept"
		# Now set Ref attributes
		itemGroupRef["ItemGroupOID"] = "IG." + c360OID
		itemGroupRef["OrderNumber"] = "1"
		itemGroupRef["Mandatory"] = "Yes"
		itemGroupRefs.append(itemGroupRef)
		formDef["igrefs"] = itemGroupRefs
		frmList.append(formDef)
		
		
		bcVarList= bc["bcVarList"]
		irefList = []
		for bcVar in bcVarList:
			#print(str(bcVar["ordinal"]) + " " + bcVar["name"])
			
			itemDef = {}
			itemRef = {}
			codeListDef = {}
			varName = bcVar["DEC"]
			# varClibInfo = bcVar["ClibRef"]
			hasCodelist = False
			if "ClibRef" not in bcVar:
				itemDef = genericItemDef(varName,bcVar)
				if "cdType" in bcVar:
					itemDef["DataType"] = bcVar["cdType"]
				elif "CDVal" in bcVar:
					itemDef["DataType"] = "text"
				itemRef = genericItemRef(varName)
				if "vdFormat" in bcVar:
					vdformat = bcVar["vdFormat"]
					formatNoWS = "".join(vdformat.split())
					itemDef["CodeListOID"] = "C360.CL." + formatNoWS
					codeListDef = codeList(clOID, vdformat, bcVar)
					codelists.append(codeListDef)
			else:
				varClibInfo = bcVar["ClibRef"]
				clibVarDef = varClibInfo["def"]
				clibLinks = clibVarDef["_links"]
				selfLink = clibLinks["self"]
				varHref = selfLink["href"]
				if "clibCodelist" in varClibInfo:
					hasCodelist = True
				itemOID = "IT." + c360Name + "." + varHref
				itemDef["OID"] = itemOID
				itemRef["ItemOID"] = itemOID
				itemRef["OrderNumber"] = clibVarDef["ordinal"]
				itemRef["mdrCore"] = clibVarDef["core"]
				itemDef["Name"] = clibVarDef["name"]
				if "cdType" in bcVar:
					itemDef["DataType"] = bcVar["cdType"]
				elif "CDVal" in bcVar:
					itemDef["DataType"] = "text"
					print(varName + " has CDVal ")
				else:
					itemDef["DataType"] = clibVarDef["simpleDatatype"]
				itemDef["label"] = clibVarDef["label"]
				itemDef["definition"] = clibVarDef["definition"]
				if "questionText" in clibVarDef:
					itemDef["questionText"] = clibVarDef["questionText"]
				if "prompt" in clibVarDef:
					itemDef["prompt"] = clibVarDef["prompt"]
				if "completionInstructions" in clibVarDef:
					itemDef["completionInstructions"] = clibVarDef["completionInstructions"]
				if "clibCodelist" in varClibInfo:
					cldict = varClibInfo["clibCodelist"]
					print(varName + " Codelist List has " + str(len(cldict)) + " codelist references")
					clhref = getCLOID(varClibInfo)
					clOID = "CL." + clhref
					itemDef["CodeListOID"] = clOID
					if "CDVal" in bcVar:
						codeListDef = codeList(clOID,clibVarDef["name"], bcVar["CDVal"], True)
					else:
						codeListDef["OID"] = clOID
						codeListDef["Name"] = clibVarDef["name"]
						codeListDef["DataType"] = "text"
						codeListDef["bcSubset"] = False
						# make an external codelist reference to CDISC CT.

					if clOID not in codelistRefs:
						codelistRefs.append(clOID)
						codelists.append(codeListDef)
					print(varName + " Codelist OID is  " + clOID)
				elif "CDVal" in bcVar:
					clOID = "C360.CL." + varHref
					itemDef["CodeListOID"] = clOID
					codeListDef = codeList(clOID, varName, bcVar["CDVal"])
					if clOID not in codelists:
						codelists.append(codeListDef)
						print(varName + " Codelist OID is  " + clOID)


			# done adding clib information. Now look at the info in the bcStructure

			"""
				#itemDef["simpleDatatype"] = clibVarDef["simpleDatatype"]
				if "mappingInstructions" in clibVarDef:
					methodDef = {}
					methodDef["OID"] = "MTH." + varName   # lambda expression?
					methodDef["Name"] = varName + "-Mapping"
					methodDef["Type"] = "Computation"
					methodDef["description"] = bcVar["mappingInstructions"]
					itemRef["MethodOID"] = "c360.Mapping.MTH." + varName
					methods.append(methodDef)
				if "sdtmigDatasetMappingTargets" in varLinks:
					itemDef["alias"] = varLinks["sdtmigDatasetMappingTargets"]
			itemDef["DataType"] = bcVar["simpleDatatype"]
			if "codelist" in varLinks:
				cl = varLinks["codelist"]
				itemDef["CodeListRef"] = varLinks["codelist"]
				# add handling for bcConcepts
				if len(cl) == 1:
					clLink = cl[0]
					clHref = clLink["href"]
					clOID = "C360.CL." + clHref
					clDef = {}
					clDef["OID"] = clOID
					clDef["href"] = clHref
					clDef["Name"] = varName + "-Codelist"
					codelists.append(clDef)
				"""
			irefList.append(itemRef)
			idefList.append(itemDef)
		itemGroupDef["irefs"] =  irefList
		igList.append(itemGroupDef)
		
	logging.info("Done %s", str(vsn))
		
	# now start assembling ODM FormDef ItemGroupDef and ItemDef elements. Need to add comments.
	nFRM = 0
	for frm in frmList:
		odmForm = ODMdoc.createElement("FormDef")
		odmForm.setAttribute("OID", frm["OID"])
		odmForm.setAttribute("Name", frm["Name"])
		odmForm.setAttribute("Repeating", frm["Repeating"])
		
		igRefList = frm["igrefs"]
		for igRef in igRefList:
			itemGroupRef = ODMdoc.createElement("ItemGroupRef")
			itemGroupRef.setAttribute("ItemGroupOID",igRef["ItemGroupOID"])
			itemGroupRef.setAttribute("OrderNumber", igRef["OrderNumber"])
			itemGroupRef.setAttribute("Mandatory", igRef["Mandatory"])
			odmForm.appendChild(itemGroupRef)
		MDV.appendChild(odmForm)
		
	nIG = 0
	for ig in igList:
		logging.info("Creating ItemGroup Def for %s", ig["OID"])
		dataStructure = ODMdoc.createElement('ItemGroupDef')
		dataStructure.setAttribute("OID", ig["OID"])
		dataStructure.setAttribute("Name", ig["Name"])
		dataStructure.setAttribute("Purpose", ig["Purpose"])
		dataStructure.setAttribute("Repeating", "Yes")
		description = ODMdoc.createElement('Description')
		transText = ODMdoc.createElement("TranslatedText")
		ltext = ODMdoc.createTextNode(ig["Label"])
		transText.appendChild(ltext)
		description.appendChild(transText)
		dataStructure.appendChild(description)
		
		irefList = ig["irefs"]
		iorder = 0
		for iref in irefList:
			itemRef = ODMdoc.createElement('ItemRef')
			itemRef.setAttribute("ItemOID", iref["ItemOID"])
			itemRef.setAttribute("OrderNumber", str(iorder))
			if "MethodOID" in iref:
				itemRef.setAttribute("MethodOID", iref["MethodOID"])
			libCore = iref["mdrCore"]
			if (libCore == "R/C"):
				itemRef.setAttribute("Mandatory", "Yes")
			elif libCore == "O":
				itemRef.setAttribute("Mandatory", "No")
			elif libCore == "HR":
				itemRef.setAttribute("Mandatory", "Yes")
			
			itemRef.setAttribute("mdr:Core", iref["mdrCore"])
			itemRef.setAttribute("xmlns:mdr", mdrnsURI)
			logging.info("ItemRef[%s]", iref["ItemOID"])
			dataStructure.appendChild(itemRef)
			iorder += 1
		MDV.appendChild(dataStructure)
		
		nIG = nIG + 1

	for idef in idefList:
		logging.info("Creating ItemDef[%s]", idef["OID"])
		itemDef = ODMdoc.createElement('ItemDef')
		itemDef.setAttribute("OID", idef["OID"])
		itemDef.setAttribute("Name", idef["Name"])
		if (idef["DataType"] == "Char"):
			itemDef.setAttribute("DataType", "text")
			itemDef.setAttribute("Length", "50")
		elif(idef["DataType"] == "Num"):
			itemDef.setAttribute("DataType", "float")
		else:
			itemDef.setAttribute("DataType", idef["DataType"])
			if idef["DataType"] == "text":
				itemDef.setAttribute("Length", "8")
			elif idef["DataType"] == "integer":
				itemDef.setAttribute("Length", "8")
			elif idef["DataType"] == "float":
				itemDef.setAttribute("Length", "8")
				itemDef.setAttribute("SignificantDigits", "3")


		#itemDef.setAttribute("Comment", idef["definition"])
		if "prompt" in idef:
			itemDef.setAttribute("mdr:Prompt", idef["prompt"])
		itemDef.setAttribute("mdr:SimpleType", idef["DataType"])
		itemDef.setAttribute("xmlns:mdr", mdrnsURI)
		description = ODMdoc.createElement('Description')
		transText = ODMdoc.createElement("TranslatedText")
		ltext = ODMdoc.createTextNode(idef["label"])
		transText.appendChild(ltext)
		description.appendChild(transText)
		itemDef.appendChild(description)
		
		#Now create QuestionText, Completion Instructions, ImplementationNotes
		if "questionText" in idef:
			questionText = ODMdoc.createElement("Question")
			transText = ODMdoc.createElement("TranslatedText")
			qtext = ODMdoc.createTextNode(idef["questionText"])
			transText.appendChild(qtext)
			questionText.appendChild(transText)
			itemDef.appendChild(questionText)

		# when the bcMatatdata includes multiple CDVals use the default as the primary.
		# ToDo: will there ever be more than 2?
		if "CodeListOID" in idef:
			clRefList = idef["CodeListOID"]
			CodeListRef = ODMdoc.createElement('CodeListRef')
			CodeListRef.setAttribute("CodeListOID", clRefList)
			itemDef.appendChild(CodeListRef)
			
		if "alias" in idef:
			aliasList = idef["alias"]
			for itarget in range(0,len(aliasList)):
				aliasInfo = aliasList[itarget]
				Alias = ODMdoc.createElement("Alias")
				Alias.setAttribute("Context","sdtm:Mapping:"+ str(itarget))
				Alias.setAttribute("Name",aliasInfo["title"])
				itemDef.appendChild(Alias)
			
		if "completionInstructions" in idef:
			completionInstructions = ODMdoc.createElementNS(mdrnsURI, "mdr:CompletionInstructions")
			transText = ODMdoc.createElement("TranslatedText")
			citext = ODMdoc.createTextNode(idef["completionInstructions"])
			transText.appendChild(citext)
			completionInstructions.appendChild(transText)
			itemDef.appendChild(completionInstructions)
		
		if "implementationNotes" in idef:
			implementationNotes = ODMdoc.createElement("mdrImplementationNotes")
			transText = ODMdoc.createElement("TranslatedText")
			iNtext = ODMdoc.createTextNode(idef["implementationNotes"])
			transText.appendChild(iNtext)
			implementationNotes.appendChild(transText)
			itemDef.appendChild(implementationNotes)	
		
		MDV.appendChild(itemDef)
	
	for cl in codelists:
		clOID = cl["OID"]
		clHref = clOID[3:]
		clCCode = ""
		if "C-code" in cl:
			clCCode = cl["C-code"]
		if "Dictionary" in cl:
			clName = cl["Dictionary"]
			CodeListDef = ODMdoc.createElement('CodeList')
			CodeListDef.setAttribute("OID", clOID)
			CodeListDef.setAttribute("Name", clName)
			CodeListDef.setAttribute("DataType", "text")
			ExternalCodelist = ODMdoc.createElement("ExternalCodeList")
			ExternalCodelist.setAttribute("Dictionary", "MedDRA")
			ExternalCodelist.setAttribute("Version", "Most Recent")
			CodeListDef.appendChild(ExternalCodelist)
			MDV.appendChild(CodeListDef)
			continue
		clName = cl["Name"]
		clType = cl["DataType"]
		CodeListDef = ODMdoc.createElement('CodeList')
		CodeListDef.setAttribute("OID", clOID)
		CodeListDef.setAttribute("Name", clName)
		CodeListDef.setAttribute("DataType", clType)
		if "bcsubset" in cl and cl["bcsubset"]:
			print("Codelist " + clOID + " has a subset.")
			print(cl)
			if "enum" in cl:
				clItems = cl["enum"]
				for enumItem in clItems:
					EnumeratedItem = ODMdoc.createElement("EnumeratedItem")
					EnumeratedItem.setAttribute("CodedValue", enumItem["codeValue"])
					if "C-code" in enumItem:
						Alias = ODMdoc.createElement("Alias")
						Alias.setAttribute("Context", "nci:ExtCodeID")
						Alias.setAttribute("Name", enumItem["C-code"])
						EnumeratedItem.appendChild(Alias)
					CodeListDef.appendChild(EnumeratedItem)
		else:
			ExternalCodelist = ODMdoc.createElement("ExternalCodeList")
			ExternalCodelist.setAttribute("Dictionary", "CDISC CT")
			ExternalCodelist.setAttribute("Version", "Most Recent")
			ExternalCodelist.setAttribute("href",clHref)
			CodeListDef.appendChild(ExternalCodelist)


		if len(clCCode) > 0:
			Alias = ODMdoc.createElement("Alias")
			Alias.setAttribute("Context", "nci:ExtCodeID")
			Alias.setAttribute("Name", clCCode)
			CodeListDef.appendChild(Alias)
		MDV.appendChild(CodeListDef)

	nm = 0
	for mthd in methods:
		methodDef = ODMdoc.createElement('MethodDef')
		methodDef.setAttribute("OID", mthd["OID"])
		methodDef.setAttribute("Name", mthd["Name"])
		methodDef.setAttribute("Type", mthd["Type"])
		description = ODMdoc.createElement("Description")
		transText = ODMdoc.createElement("TranslatedText")
		ltext = ODMdoc.createTextNode(mthd["description"])
		transText.appendChild(ltext)
		description.appendChild(transText)
		methodDef.appendChild(description)
		MDV.appendChild(methodDef)
		nm = nm + 1
	
	
	
	StudyTop.appendChild(MDV)
	odmStudy.appendChild(StudyTop)
	ODMdoc.appendChild(odmStudy)
	fn = domain +  "-ODM-360-" + prodVers + ".xml"
	print("Look for output in ", fn)
	print(ODMdoc)
	outfile = open(fn, "w", encoding="utf8")
	ODMdoc.writexml(outfile, addindent='    ', newl='\n')
	#ODMdoc.writexml(outfile)
	outfile.close()
	print("Look for output in ", fn)
	
def createODMAttribs(prodVers: str) ->dict:
	# build dict with creationDT, FileOID, FileType, Granularity
	
	cdt = datetime.datetime.now()
	creationDT = cdt.isoformat()
	odmRootAttribs = {}
	odmRootAttribs['CreationDateTime'] = creationDT
	odmRootAttribs['FileOID'] = '[CDISC LIBRARY- ' + prodVers + ']'
	odmRootAttribs['FileType'] = 'Snapshot'
	
	return odmRootAttribs

def genericItemDef(varName:str, bcVar:dict) ->dict:
	idef = {}
	idef["OID"] = "C360.IT." + varName
	idef["Name"] = varName
	idef["DataType"] = "text"
	if "cdType" in bcVar:
		idef["DataType"] = bcVar["cdType"]
	elif "CDVal" in bcVar:
		idef["DataType"] = bcVar["CDVal"]
	idef["label"] = varName + " generic definition. "
	return idef

def genericItemRef(varName:str) -> dict:
	iref = {}
	iref["ItemOID"] = "C360.IT." + varName
	iref["Mandatory"] = "No"
	iref["mdrCore"] = "O"
	return iref

def getCLOID(clibInfo:dict) -> str:
	clList = clibInfo["clibCodelist"]
	clInfo = clList[0]
	return clInfo["href"]

def cdval2ItemList(cdVal:str) -> list:
	itemList = []
	if "subset" in cdVal:
		print("processing subset")
		subsetItems = cdVal["subset"].split(";")
		for item in subsetItems:
			clitemDef = {}
			if "(" in item:
				itemInfo = item.split("(")
				clitemDef["codeValue"] = itemInfo[0].strip(" ")
				ccodepart = itemInfo[1].rstrip(" ")
				s = len(ccodepart) -1
				clitemDef["C-code"] = ccodepart[1:s]
				itemList.append(clitemDef)
			else:
				clitemDef["codeValue"] = item.strip(" ")
				itemList.append(clitemDef)
		return itemList
	if "value" in cdVal:
		print("processing single Value")
		item = cdVal["value"]
		print(item)
		clitemDef = {}
		if "(" in item:
			itemInfo = item.split("(")
			clitemDef["codeValue"] = itemInfo[0].rstrip(" ").lstrip(" ")
			ccodepart = itemInfo[1].rstrip(" ")
			s = len(ccodepart) - 1
			clitemDef["C-code"] = ccodepart[1:s]
			itemList.append(clitemDef)

		return itemList


	return itemList

def cloid2Ccode(clHref:str) -> str:
	clrefParts = clHref.split("/")
	nparts = len(clrefParts)
	return clrefParts[nparts-1]