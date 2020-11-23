<?xml version="1.0"?>
<xsl:stylesheet version="1.0" 
	 xmlns:odm="http://www.cdisc.org/ns/odm/v1.3"
	 xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
	 xmlns:xlink="http://www.w3c.org/1999/xlink">

	<xsl:output method="xml" version="1.1" encoding="UTF-8" indent="yes"/>

	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<!-- File:         crf.xsl                                                                                  -->
	<!-- Date:         23-June-2006                                                                             -->
	<!-- Version:      1.0.0                                                                                    -->
	<!-- Author:       Dave Iberson-Hurst(Assero) with the kind assistance of Anthony Friebel (SAS)             -->
	<!-- Date: 4-March-2010                                                                                     -->
	<!-- Author:       Jozef Aerts (XML4Pharma) adapted and extended for ODM 1.3                                -->
	<!-- Date: 17-Sep-2019                                                                                     -->
	<!-- Author:       Sam Hume(CDISC) adapted and extended for CDISC 360                                       -->
	<!-- Organization: Clinical Data Interchange Standards Consortium (CDISC)                                   -->
	<!-- Description:  This style sheet allows for the metadata held within an ODM file to be visualised. The   -->
	<!--               visualisation permits the CRF structures used to collect the data to be viewed along     -->
	<!--               with the associated SDTM annotations.                                                    -->
    <!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->

	<!-- the language for which the study design should be displayed can be passed as a parameter to the stylesheet 
		default is the english language -->
	<xsl:param name="LANGUAGE">en</xsl:param>

	<xsl:variable name="FullWidth">1000</xsl:variable>
	<xsl:variable name="FillWidth">100%</xsl:variable>
	<xsl:variable name="Indent1">20</xsl:variable>
	<xsl:variable name="Indent2">40</xsl:variable>
	<xsl:variable name="Indent3">60</xsl:variable>
	<xsl:variable name="Indent4">80</xsl:variable>
	<xsl:variable name="FormClass">form</xsl:variable>
	<xsl:variable name="StudyClass">study</xsl:variable>
			
	<!--
		Template: The main template.
		Purpose:  Builds the entire HTML page.
	-->
	<xsl:template match="/">
	
		<html>
			<!-- Create the HTML Header, include any style information we need -->
			<head>
				<style type="text/css">
					p {text-align:left;font-size:8pt;font-family: verdana, arial, helvetica, sans-serif;}
					p.small {font-size:6pt;}
					p.annotation1 {text-align:center; font-size:8pt}
					p.annotation2 {text-align:left; font-size:8pt}
					p.audit {font-size:7pt; color:red}
					p.event {text-align:left; font-size:8pt}
					p.study {text-align:center; font-size:14pt}
					p.form {text-align:center; font-size:14pt}
					p.group {text-align:center; font-size:12pt}
					p.head {text-align:left; font-weight:bold; font-size:16pt;}
					p.infob {font-weight:bold; font-size:8pt;}
					p.info {font-size:8pt;}
					
					a.small {font-family: verdana, arial, helvetica, sans-serif; font-size: 8pt; font-style: normal; line-height: normal; font-weight: normal; text-align: left; color:5a5aef}
					
					@page {size: 11.69in 8.27in;}
				}
					
				</style>
				<title>Rendering of ODM Metadata. XSLT Stylesheet (R1.0.0)</title>
			</head>
			
			<!-- Now generate the CRFs within the ODM file. List the studies and then detail each one. -->
			<body>
				<a name='top'/>
				<xsl:call-template name="ListStudies"/>
				<xsl:for-each select="/odm:ODM/odm:Study">
					<xsl:call-template name="Study">
						<xsl:with-param name="StudyTree" select="."/>	
					</xsl:call-template>	
				</xsl:for-each>
			</body>
		</html>
	</xsl:template>			

	<!--
		Template: ListStudies
		Purpose:  Lists all the studies within an ODM file.
	-->
	<xsl:template name="ListStudies">
		<table border='0' cellspacing='0' cellpadding='2'>
			<xsl:attribute name="width">
				<xsl:value-of select="$FullWidth"/>		
			</xsl:attribute>
			<tr>
				<td>
					<xsl:call-template name="ListHeading">
						<xsl:with-param name="Width" select="$FullWidth"/>
						<xsl:with-param name="Title">Studies</xsl:with-param>
					</xsl:call-template>
					<table width='100%' border='0' cellspacing='0' cellpadding='2'>
						<tr>
							<td width='150'><p class='infob'>Name</p></td>
							<td><p class='infob'>OID</p></td>
						</tr>
						<xsl:for-each select="/odm:ODM/odm:Study">
							<tr>
								<td valign='top'><p class='info'><xsl:value-of select="./odm:GlobalVariables/odm:StudyName"/></p></td>
							 	<td valign='top'>
									<p class='info'>
							  			<a>
											<xsl:attribute name="href">#<xsl:value-of select="@OID"/></xsl:attribute>
											<xsl:value-of select="@OID"/>
										</a>
									</p>
						 		</td>
					 		</tr>
						</xsl:for-each>
					</table><br/> 
				</td>
			</tr>
		</table>
	</xsl:template>			
	
	<!--
		Template: Study
		Purpose:  Lists and displays all the metadata for a given study.
	-->
	<xsl:template name="Study">
		<xsl:param name="StudyTree"/>
		
		<!-- Display the study & protocol information.	-->
		<table border='0' cellspacing='0' cellpadding='2'>
			<xsl:attribute name="width">
				<xsl:value-of select="$FullWidth"/>		
			</xsl:attribute>
			<tr>
				<td> 
					<xsl:attribute name="width">
						<xsl:value-of select="$Indent1"/>		
					</xsl:attribute>
				</td>
				<td>
					<xsl:call-template name="InstanceHeading">
						<xsl:with-param name="AnchorName" select="@OID"/>
						<xsl:with-param name="Class" select="$StudyClass"/>
						<xsl:with-param name="Name" select="concat ('Study: ', $StudyTree/odm:GlobalVariables/odm:StudyName)"/>
						<xsl:with-param name="OID" select="@OID"/>
						<xsl:with-param name="Repeating" select="@Repeating"/>
						<xsl:with-param name="Width" select="$FillWidth"/>
						<xsl:with-param name="Link">top</xsl:with-param>
						<xsl:with-param name="LinkText">Top</xsl:with-param>
					</xsl:call-template>
					<xsl:call-template name="StudyInfo">
						<xsl:with-param name="Width" select="$FillWidth"/>
						<xsl:with-param name="StudyTree" select="$StudyTree"/>
					</xsl:call-template>
				</td>
			</tr>					
		</table>
		<br/>
		
		<!-- 
		     Now list each of the MetaData Versions present in the ODM file. 
		     This just lists the name and OID for each MetaDataVersion present. 
		-->
		<xsl:call-template name="ListMetaData">
			<xsl:with-param name="StudyTree" select="$StudyTree"/>
		</xsl:call-template>
		
		<!-- 
		     Now display each of the MetaData Versions present. This loops for each 
		     MetaDataVersion and builds the tree of StudyEvents, Forms, ItemGroups and Items.
		-->
		<xsl:for-each select="$StudyTree/odm:MetaDataVersion">
			<table border='0' cellspacing='0' cellpadding='2'>
				<xsl:attribute name="width">
					<xsl:value-of select="$FullWidth"/>		
				</xsl:attribute>
				<tr>
					<td> 
						<xsl:attribute name="width">
							<xsl:value-of select="$Indent3"/>		
						</xsl:attribute>
					</td>
					<td>
						<xsl:call-template name="InstanceHeading">
							<xsl:with-param name="AnchorName" select="concat($StudyTree/@OID, '_', @OID)"/>
							<xsl:with-param name="Class" select="$FormClass"/>
							<xsl:with-param name="Name" select="concat ('MetaData: ', @Name)"/>
							<xsl:with-param name="OID" select="@OID"/>
							<xsl:with-param name="Repeating" select="@Repeating"/>
							<xsl:with-param name="Width" select="$FillWidth"/>
							<xsl:with-param name="Link" select="$StudyTree/@OID"/>
							<xsl:with-param name="LinkText">Study</xsl:with-param>
						</xsl:call-template>
					</td>
				</tr>
			</table>
			<table border='0' cellspacing='0' cellpadding='2'>
				<xsl:attribute name="width">
					<xsl:value-of select="$FullWidth"/>		
				</xsl:attribute>
				<tr>
					<td> 
						<xsl:attribute name="width">
							<xsl:value-of select="$Indent4"/>		
						</xsl:attribute>
					</td>
					<td>
						<xsl:call-template name="MetaDataVersion">
							<xsl:with-param name="MDV_Tree" select="."/>
							<xsl:with-param name="Key" select="concat($StudyTree/@OID, '_', @OID)"/>
						</xsl:call-template>
					</td>
				</tr>
			</table>
		</xsl:for-each>
	</xsl:template>			

	<!--
		Template: ListMetaData
		Purpose:  Lists all the metadata for a given study.
	-->
	<xsl:template name="ListMetaData">
		<xsl:param name="StudyTree"/>
		<table border='0' cellspacing='0' cellpadding='2'>
			<xsl:attribute name="width">
				<xsl:value-of select="$FullWidth"/>		
			</xsl:attribute>
			<tr>
				<td> 
					<xsl:attribute name="width">
						<xsl:value-of select="$Indent2"/>		
					</xsl:attribute>
				</td>
				<td>
					<xsl:call-template name="ListHeading">
						<xsl:with-param name="Width" select="$FillWidth"/>
						<xsl:with-param name="Title">MetaData</xsl:with-param>
					</xsl:call-template>
					<table width='100%' border='0' cellspacing='0' cellpadding='2'>
						<tr>
							<td width='150'><p class='infob'>Name</p></td>
							<td><p class='infob'>OID</p></td>
						</tr>
						<xsl:for-each select="$StudyTree/odm:MetaDataVersion">
							<tr>
							<td valign='top'><p class='info'><xsl:value-of select="@Name"/></p></td>
							 	<td valign='top'>
									<p class='info'>
							  			<a>
											<xsl:attribute name="href">#<xsl:value-of select="concat($StudyTree/@OID, '_', @OID)"/></xsl:attribute>
											<xsl:value-of select="@OID"/>
										</a>
									</p>
						 		</td>
					 		</tr>
						</xsl:for-each>
					</table><br/> 
				</td>
			</tr>
		</table>
	</xsl:template>			
		
	<!--
		Template: StudyInfo
		Purpose:  Lists basic study information.
	-->
	<xsl:template name="StudyInfo">
		<xsl:param name="Width"/>
		<xsl:param name="StudyTree"/>
		<table border='0' cellspacing='0' cellpadding='2'>
			<xsl:attribute name="width">
				<xsl:value-of select="$Width"/>		
			</xsl:attribute>
			<tr>
				<td width='150'><p class='infob'><b>Name</b></p></td>
				<td><p class='info'><xsl:value-of select="$StudyTree/odm:GlobalVariables/odm:StudyName"/></p></td>
			</tr>
			<tr>
				<td><p class='infob'><b>Description</b></p></td>
				<td><p class='info'><xsl:value-of select="$StudyTree/odm:GlobalVariables/odm:StudyDescription"/></p></td>
			</tr>
			<tr>
				<td><p class='infob'><b>Protocol Name</b></p></td>
				<td><p class='info'><xsl:value-of select="$StudyTree/odm:GlobalVariables/odm:ProtocolName"/></p></td>
			</tr>					
		</table>
		<br/>
	</xsl:template>
				
	<!--
		Template: MetaDataVersion
		Purpose:  Displays each metadata version, the Events, the Forms, ItemGroups and Items
	-->
	<xsl:template name="MetaDataVersion">		 
		<xsl:param name="MDV_Tree"/>
		<xsl:param name="Key"/>
		<xsl:variable name="MDV_OID" select="@OID"/>
		
		<!-- Display each of the events in turn, listing the set of forms for each event. -->
		<!-- commented out by J.Aerts 
		<xsl:call-template name="ListHeading">
			<xsl:with-param name="Width" select="$FillWidth"/>
			<xsl:with-param name="Title">Study Events and Forms</xsl:with-param>
		</xsl:call-template>
		<table width='100%' border='0' cellspacing='0' cellpadding='2'>
			<tr>
				<td><p class='infob'>Identifier</p></td>
				<td><p class='infob'>Mandatory</p></td>
				<td><p class='infob'>Forms</p></td>
			</tr>
			<xsl:for-each select="$MDV_Tree/odm:Protocol/odm:StudyEventRef">
				<xsl:variable name="SE_OID" select="@StudyEventOID"/>
			  	<xsl:variable name="SE_Man" select="@Mandatory"/>
				<tr>
				 	<td valign='top'><p class='info'><xsl:value-of select="$SE_OID"/></p></td>
				 	<td valign='top'><p class='info'><xsl:value-of select="$SE_Man"/></p></td>
				 	<td valign='top'>
						<p class='info'>
					  	<xsl:for-each select="$MDV_Tree/odm:StudyEventDef">
							<xsl:variable name="SED_OID" select="@OID"/>
						 	<xsl:if test="$SED_OID=$SE_OID">
								<xsl:for-each select="odm:FormRef">
							  		<xsl:variable name="F_OID" select="@FormOID"/>
							  		<xsl:variable name="FormKey" select="concat($Key, '.', $F_OID)"/>
							  		<a>
										<xsl:attribute name="href">#<xsl:value-of select="$FormKey"/></xsl:attribute>
										<xsl:value-of select="$F_OID"/>
									</a>
									<br/>
								</xsl:for-each>
						 	</xsl:if>
					  	</xsl:for-each>
						</p>
				 	</td>
			  	</tr>
			</xsl:for-each>
		</table>  
		-->
		
		<!-- table redesigned by J.Aerts to account for skip conditions -->
		<table width='100%' border='0' cellspacing='0' cellpadding='2'>
			<!-- table header -->
			<tr>
				<td><p class='infob'>Identifier</p></td>
				<td><p class='infob'>Mandatory</p></td>
				<td><p class="infob">Skip Study Event condition</p></td>
				<td><p class='infob'>Forms</p></td>
				<td><p class="infob">Skip Form condition</p></td>
			</tr>
			<xsl:for-each select="$MDV_Tree/odm:Protocol/odm:StudyEventRef">
				<xsl:variable name="SE_OID" select="@StudyEventOID"/>
			  	<xsl:variable name="SE_Man" select="@Mandatory"/>
			  	<xsl:variable name="SE_SkipCondition" select="@CollectionExceptionConditionOID"/>
			  	<xsl:variable name="Form_Count" select="count(../../odm:StudyEventDef[@OID=$SE_OID]/odm:FormRef)"/>
			  	<!--xsl:message>Form_Count for StudyEvent with OID = <xsl:value-of select="$SE_OID"/> = <xsl:value-of select="$Form_Count"/></xsl:message-->
			  	<xsl:for-each select="../../odm:StudyEventDef[@OID=$SE_OID]/odm:FormRef">
			  		<xsl:variable name="F_OID" select="@FormOID"/>
					<xsl:variable name="FormKey" select="concat($Key, '_', $F_OID)"/>
			  		<tr>
			  			<td rowspan="$Form_Count"><xsl:if test="position() = 1"><p class="info"><xsl:value-of select="$SE_OID"/></p></xsl:if></td>
			  			<td rowspan="$Form_Count"><xsl:if test="position() = 1"><p class="info"><xsl:value-of select="$SE_Man"/></p></xsl:if></td>
			  			<td rowspan="$Form_Count">
			  				<xsl:if test="position() = 1">
			  					<p class="info">
			  						<font color="blue"><xsl:call-template name="GetSkipCondition">
			  							<xsl:with-param name="METADATAVERSIONOID" select="$MDV_OID"/>
			  							<xsl:with-param name="STUDYOID" select="$MDV_Tree/../@OID"/>
			  							<xsl:with-param name="CONDITIONOID" select="$SE_SkipCondition"/>
			  						</xsl:call-template></font>
			  					</p>
			  				</xsl:if>
			  			</td>
			  			<td><p class="info">
			  				<a><xsl:attribute name="href">#<xsl:value-of select="$FormKey"/></xsl:attribute><xsl:value-of select="$F_OID"/></a>
			  			</p></td>
			  			<td><p class="info">
			  				<font color="blue">
			  				<xsl:call-template name="GetSkipCondition">
			  					<xsl:with-param name="METADATAVERSIONOID" select="$MDV_OID"/>
			  					<xsl:with-param name="STUDYOID" select="$MDV_Tree/../@OID"/>
			  					<xsl:with-param name="CONDITIONOID" select="@CollectionExceptionConditionOID"/>
			  				</xsl:call-template>
			  				</font>
			  			</p></td>
			  		</tr>
			  	</xsl:for-each>
			</xsl:for-each>			
		</table>
		
		<br/>
	 
		<!-- Display the forms. Each form is composed of a set of groups. -->
		<!--xsl:for-each select="$MDV_Tree/odm:FormDef"-->
		<xsl:for-each select="$MDV_Tree/odm:FormDef">
			<xsl:variable name="FD_OID" select="@OID"/>
			<!--xsl:variable name="FD_Name" select="@Name"/-->
			<!-- i18n by J.Aerts -->
			<xsl:variable name="FD_Name">
				<xsl:choose>
					<xsl:when test="./odm:Description">
						<xsl:choose>
							<xsl:when test="./odm:Description/odm:TranslatedText[@xml:lang=$LANGUAGE]">
								<xsl:value-of select="./odm:Description/odm:TranslatedText[@xml:lang=$LANGUAGE]"/>
							</xsl:when>
							<xsl:when test="./odm:Description/odm:TranslatedText[starts-with($LANGUAGE,@xml:lang)]">
								<xsl:value-of select="./odm:Description/odm:TranslatedText[starts-with($LANGUAGE,@xml:lang)]"/>
							</xsl:when>
							<xsl:otherwise><xsl:value-of select="./odm:Description/odm:TranslatedText[not(@xml:lang)]"/></xsl:otherwise>
						</xsl:choose>
					</xsl:when>
					<xsl:otherwise><xsl:value-of select="@OID"/></xsl:otherwise>
				</xsl:choose>
			</xsl:variable>
			<!--table width='100%' border='1' cellspacing='0' cellpadding='5'-->
			<xsl:element name="table">
				<xsl:attribute name="width">100%</xsl:attribute>
				<xsl:attribute name="border">1</xsl:attribute>
				<xsl:attribute name="cellspacing">0</xsl:attribute>
				<xsl:attribute name="cellpadding">5</xsl:attribute>
				<xsl:attribute name="summary">Form <xsl:value-of select="$FD_OID"/></xsl:attribute>
				<xsl:variable name="Class">form</xsl:variable>
	  			<xsl:variable name="FormKey" select="concat($Key, '_', $FD_OID)"/>
				<tr>
					<td>
						<xsl:call-template name="InstanceHeading">
							<xsl:with-param name="AnchorName" select="$FormKey"/>
							<xsl:with-param name="Class" select="$Class"/>
							<xsl:with-param name="Name" select="concat ('Form: ', $FD_Name)"/>
							<xsl:with-param name="OID" select="$FD_OID"/>
							<xsl:with-param name="Repeating" select="@Repeating"/>
							<xsl:with-param name="Width" select="$FillWidth"/>
							<xsl:with-param name="Link" select="$Key"/>
							<xsl:with-param name="LinkText">MetaData</xsl:with-param>
						</xsl:call-template>
					</td>
				</tr>
				<tr>
					<td>
						<xsl:for-each select="odm:ItemGroupRef">
							<xsl:variable name="IGR_OID" select="@ItemGroupOID"/>
							<xsl:variable name="CONDITIONOID" select="@CollectionExceptionConditionOID"/>
							<table width='100%' border='0' cellspacing='0' cellpadding='2'>
								<tr>
									<td>
										<table width='100%' border='1' cellspacing='0' cellpadding='2'>
											<xsl:for-each select="$MDV_Tree/odm:ItemGroupDef">
												<xsl:variable name="IGD_OID" select="@OID"/>
												<xsl:variable name="IGD_Name" select="@Name"/>
												<xsl:if test="$IGR_OID=$IGD_OID">
													<xsl:call-template name="ItemGroup">
														<xsl:with-param name="MDV_Tree" select="$MDV_Tree"/>
														<!-- J.Aerts for ODM 1.3 -->
														<xsl:with-param name="CONDITIONOID" select="$CONDITIONOID"/>
													</xsl:call-template>	
												</xsl:if>
											</xsl:for-each>
										</table>
									</td>
								</tr>
							</table>
							<br/>
						</xsl:for-each>
					</td>
				</tr>
			</xsl:element>
		 	<!--/table-->
		 	<br/>
		</xsl:for-each>
	</xsl:template>
	
	<!--
		Template: ItemGroup
		Purpose:  Displays an individual ItemGroup
	-->
	<xsl:template name="ItemGroup">
		<xsl:param name="MDV_Tree"/>
		<xsl:param name="CONDITIONOID"></xsl:param>
		<tr valign='top'>
			<td valign='top'>
				<p class='group'>
					<!-- i18n by Jozef Aerts -->
					<b>Group: 
						<xsl:choose>
							<xsl:when test="./odm:Description">
								<xsl:choose>
									<xsl:when test="./odm:Description/odm:TranslatedText[@xml:lang=$LANGUAGE]">
										<xsl:value-of select="./odm:Description/odm:TranslatedText[@xml:lang=$LANGUAGE]"/>
									</xsl:when>
									<xsl:when test="./odm:Description/odm:TranslatedText[starts-with($LANGUAGE,@xml:lang)]">
										<xsl:value-of select="./odm:Description/odm:TranslatedText[starts-with($LANGUAGE,@xml:lang)]"/>
									</xsl:when>
									<xsl:otherwise>
										<xsl:value-of select="./odm:Description/odm:TranslatedText[not(@xml:lang)]"/>
									</xsl:otherwise>
								</xsl:choose>
							</xsl:when>
							<xsl:otherwise>
								<xsl:value-of select="@Name"/>
							</xsl:otherwise>
						</xsl:choose>
					</b>
				</p>
				<p class='annotation1'>
					<i>OID=<xsl:value-of select="@OID"/>, Repeating=<xsl:value-of select="@Repeating"/></i>
				</p>
				<!-- J.Aerts, and only when there is a skip condition -->
				<xsl:if test="$CONDITIONOID != ''">
					<p class='annotation1'>
						<font color="blue">
						<i><b>Skip condition: </b><xsl:call-template name="GetSkipCondition">
							<xsl:with-param name="CONDITIONOID" select="$CONDITIONOID"/>
							<xsl:with-param name="METADATAVERSIONOID" select="$MDV_Tree/*[1]/../@OID"/>
							<xsl:with-param name="STUDYOID" select="$MDV_Tree/*[1]/../../@OID"/>
						</xsl:call-template>
						</i></font>
					</p>
				</xsl:if>
			</td>
		</tr>
		<tr valign='top'>
			<td valign='top'>
				<table border='0'>
				   <xsl:for-each select="odm:ItemRef">
						<xsl:variable name="IR_OID" select="@ItemOID"/>
						<!-- J.Aerts for ODM 1.3-->
						<xsl:variable name="CONDITIONOIDITEMREF" select="@CollectionExceptionConditionOID"/>
						<xsl:variable name="METHODOIDITEMREF" select="@MethodOID"/>
						<xsl:message>METHODOIDITEMREF = <xsl:value-of select="$METHODOIDITEMREF"/></xsl:message>
						<xsl:for-each select="$MDV_Tree/odm:ItemDef">
							<xsl:variable name="ID_OID" select="@OID"/>
							<xsl:if test="$IR_OID=$ID_OID">
								<tr valign='top'>
					   				<td width='400' valign='top'>
					   					<p>
											<xsl:call-template name="QuestionText">
												<xsl:with-param name="OID" select="$ID_OID"/>
											</xsl:call-template>
											<br/>
											<font color='red'><xsl:call-template name="SDTMAnnotation"/></font>
											<!-- J.Aerts for Alias elements -->
											<xsl:if test="odm:Alias"><!-- there is at least 1 Alias given -->
												<xsl:for-each select="odm:Alias">
													<xsl:call-template name="AliasTemplate">
														<xsl:with-param name="ALIAS" select="."/>
													</xsl:call-template>
												</xsl:for-each>
											</xsl:if>
										</p>
									</td>
									<td valign='top' width="250"> <!-- width attribute added by J.Aerts -->
					   					<p>
											<xsl:call-template name="DataField">
												<xsl:with-param name="MDV_Tree" select="$MDV_Tree"/>
											</xsl:call-template><br/>
										</p>
									</td>
									<!-- J.Aerts for ODM 1.3 - and only when there is a skip condition -->
									<xsl:if test="$CONDITIONOIDITEMREF != ''">
										<td valign='top'> 
										<p class='annotation1'>
											<font color="blue"><i><b>Skip condition: </b><xsl:call-template name="GetSkipCondition">
												<xsl:with-param name="CONDITIONOID" select="$CONDITIONOIDITEMREF"/>
												<xsl:with-param name="METADATAVERSIONOID" select="$MDV_Tree/*[1]/../@OID"/>
												<xsl:with-param name="STUDYOID" select="$MDV_Tree/*[1]/../../@OID"/>
											</xsl:call-template>
											</i></font>
										</p>
										</td>
									</xsl:if>
									<!-- J.Aerts for ODM 1.3 - and only when there is a MethodOID -->
									<xsl:if test="$METHODOIDITEMREF != ''">
										<td valign='top'>
										<p class='annotation1'>
											<xsl:message>Calling GetMethod</xsl:message>
											<font color="green"><i><b>Method: </b><xsl:call-template name="GetMethod">
												<xsl:with-param name="METHODOID" select="$METHODOIDITEMREF"/>
												<xsl:with-param name="METADATAVERSIONOID" select="$MDV_Tree/*[1]/../@OID"/>
												<xsl:with-param name="STUDYOID" select="$MDV_Tree/*[1]/../../@OID"/>
											</xsl:call-template></i></font>
										</p>
										</td>
									</xsl:if>
								</tr>
							</xsl:if>
						</xsl:for-each>
					</xsl:for-each>
				</table>
			</td>
		</tr>
	</xsl:template>
	
	<!-- Alias template by J.Aerts -->
	<xsl:template name="AliasTemplate">
		<xsl:param name="ALIAS"></xsl:param>
		<br/><font color="green"><i>Alias: <xsl:value-of select="$ALIAS/@Context"/>: <xsl:value-of select="$ALIAS/@Name"/></i></font>
	</xsl:template>
	
	
	<!--
		Template: QuestionText
		Purpose:  Displays the question text for a given Item.
		Changed by J.Aerts for i18n
	-->
	<xsl:template name="QuestionText">
		<xsl:choose>
		 	<xsl:when test="./odm:Question and ./odm:Question/odm:TranslatedText">
		 		<xsl:choose>
		 			<xsl:when test="./odm:Question/odm:TranslatedText[@xml:lang = $LANGUAGE]">
		 				<xsl:value-of select="./odm:Question/odm:TranslatedText[@xml:lang = $LANGUAGE]"/>
		 			</xsl:when>
		 			<xsl:when test="./odm:Question/odm:TranslatedText[starts-with($LANGUAGE,@xml:lang)]">
		 				<xsl:value-of select="./odm:Question/odm:TranslatedText[starts-with($LANGUAGE,@xml:lang)]"/>
		 			</xsl:when>
		 			<xsl:otherwise><xsl:value-of select="./odm:Question/odm:TranslatedText[not(@xml:lang)]"/></xsl:otherwise>
		 		</xsl:choose>
	 		</xsl:when>
	 		<xsl:otherwise>
		 		<xsl:value-of select="@Name"/>
			</xsl:otherwise>
		</xsl:choose> 
	</xsl:template>
	
	<!--
		Template: SDTMAnnotation
		Purpose:  Determines if SDSVarName attribute exists and sets the annotated variable appropriately.
	-->
	<xsl:template name="SDTMAnnotation">
		<xsl:choose>
			<xsl:when test="./@SDSVarName">
				<xsl:value-of select="@SDSVarName"/>	
			</xsl:when>
			<!-- re-introduce later when 	
			<xsl:otherwise>
		 		<b>@SDSVarName Not Set</b>
			</xsl:otherwise>
			-->
		</xsl:choose>
	</xsl:template>
	
	<!-- 
		Template: GetSkipConditionDescription
		Purpose: returns the human-readable skip condition of the given Condition OID
		for the specific language
	-->
	<xsl:template name="GetSkipCondition">
		<xsl:param name="STUDYOID"></xsl:param>
		<xsl:param name="METADATAVERSIONOID"></xsl:param>
		<xsl:param name="CONDITIONOID"></xsl:param>
		<!--xsl:message>STUDYOID = <xsl:value-of select="$STUDYOID"/></xsl:message>
		<xsl:message>METADATAVERSIONOID = <xsl:value-of select="$METADATAVERSIONOID"/></xsl:message>
		<xsl:message>CONDITIONOID = <xsl:value-of select="$CONDITIONOID"/></xsl:message-->
		<!-- The language parameter $LANGUAGE is set at the top of the stylesheet -->
		<xsl:choose>
			<!-- no ConditionOID: just return blank -->
			<xsl:when test="$CONDITIONOID=''"><xsl:value-of select="''"/></xsl:when>
			<!-- ConditionOID given, look it up -->
			<xsl:otherwise>
				<xsl:variable name="CONDITIONDEF" select="//odm:Study[@OID=$STUDYOID]/odm:MetaDataVersion[@OID=$METADATAVERSIONOID]/odm:ConditionDef[@OID=$CONDITIONOID]"/>
				<!--xsl:message>Children: <xsl:for-each select="$CONDITIONDEF/*"><xsl:value-of select="name()"/></xsl:for-each></xsl:message-->
				<xsl:choose>
					<!-- exact language -->
					<xsl:when test="$CONDITIONDEF/odm:Description/odm:TranslatedText[@xml:lang=$LANGUAGE]">
						<xsl:value-of select="$CONDITIONDEF/odm:Description/odm:TranslatedText[@xml:lang=$LANGUAGE]"/>
					</xsl:when>
					<!-- near-exact language i.e. en-us vs. en -->
					<xsl:when test="$CONDITIONDEF/odm:Description/odm:TranslatedText[starts-with($LANGUAGE,@xml:lang)]">
						<xsl:value-of select="$CONDITIONDEF/odm:Description/odm:TranslatedText[starts-with($LANGUAGE,@xml:lang)]"/>
					</xsl:when>
					<!-- TranslatedText without xml:lang -->
					<xsl:when test="$CONDITIONDEF/odm:Description/odm:TranslatedText[not(@xml:lang)]">
						<xsl:value-of select="$CONDITIONDEF/odm:Description/odm:TranslatedText[not(@xml:lang)]"/>
					</xsl:when>
					<!-- worst case: take the value of the "Name" attribute -->
					<xsl:otherwise><xsl:value-of select="$CONDITIONDEF/*[1]/../@Name"/></xsl:otherwise>
				</xsl:choose>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>
	
	<!-- Template GetMethod 
		Purpose: returns the human-readable skip condition of the given Method OID
		for the specific language
	-->
	<xsl:template name="GetMethod">
		<xsl:param name="STUDYOID"></xsl:param>
		<xsl:param name="METADATAVERSIONOID"></xsl:param>
		<xsl:param name="METHODOID"></xsl:param>
		<xsl:message>$METHODOID = <xsl:value-of select="$METHODOID"/></xsl:message>
		<xsl:choose>
			<!-- no METHODOID: just return blank -->
			<xsl:when test="$METHODOID=''"><xsl:value-of select="''"/></xsl:when>
			<xsl:otherwise>
				<xsl:variable name="METHODDEF" select="//odm:Study[@OID=$STUDYOID]/odm:MetaDataVersion[@OID=$METADATAVERSIONOID]/odm:MethodDef[@OID=$METHODOID]"/>
				<xsl:choose>
					<!-- exact language -->
					<xsl:when test="$METHODDEF/odm:Description/odm:TranslatedText[@xml:lang=$LANGUAGE]">
						<xsl:value-of select="$METHODDEF/odm:Description/odm:TranslatedText[@xml:lang=$LANGUAGE]"/>
					</xsl:when>
					<!-- near-exact language i.e. en-us vs. en -->
					<xsl:when test="$METHODDEF/odm:Description/odm:TranslatedText[starts-with($LANGUAGE,@xml:lang)]">
						<xsl:value-of select="$METHODDEF/odm:Description/odm:TranslatedText[starts-with($LANGUAGE,@xml:lang)]"/>
					</xsl:when>
					<!-- TranslatedText without xml:lang -->
					<xsl:when test="$METHODDEF/odm:Description/odm:TranslatedText[not(@xml:lang)]">
						<xsl:value-of select="$METHODDEF/odm:Description/odm:TranslatedText[not(@xml:lang)]"/>
					</xsl:when>
					<!-- worst case: take the value of the "Name" attribute -->
					<xsl:otherwise><xsl:value-of select="$METHODDEF/*[1]/../@Name"/></xsl:otherwise>
				</xsl:choose>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>
	
	<!--
		Template: DataField
		Purpose:  Constructs a data field for an Item depending on the ItemDef
	-->
	<xsl:template name="DataField">
		<xsl:param name="OID"/>
		<xsl:param name="MDV_Tree"/>
		<xsl:variable name="ID_DT" select="@DataType"/>
		<xsl:choose>
		
			<!-- CodeList -->
			<xsl:when test="./odm:CodeListRef[@CodeListOID]">
			 	<xsl:variable name="ID_CLOID" select="./odm:CodeListRef/@CodeListOID"/>
		 		<xsl:for-each select="$MDV_Tree/odm:CodeList">
		 			<xsl:if test="@OID=$ID_CLOID">
						
						<!-- Drop Down List Version -->
						<!-- Radio button better in that very long TranslatedText content gets wrapped
						     whereas select ones do not. -->
						<!--<select>
			  				<xsl:attribute name="name">
					  			<xsl:value-of select="@OID"/>
			  				</xsl:attribute>
			  				<option>
					  			<xsl:attribute name="value">
							  		_blank			
					  			</xsl:attribute>
								Code List: <xsl:value-of select="@OID"/>
					 		</option>
					 		<xsl:for-each select="./odm:CodeListItem">
								<option>
						  			<xsl:attribute name="value">
								  			<xsl:value-of select="@CodedValue"/>
						  			</xsl:attribute>
									<xsl:value-of select="./odm:Decode/odm:TranslatedText"/>  
						 		</option>
							</xsl:for-each>
						</select>-->
						
						<!-- Radio Button Version -->
						<xsl:for-each select="./odm:CodeListItem">
							<xsl:call-template name="Radio">
								<xsl:with-param name="RadioName" select="../@OID"/>
								<xsl:with-param name="RadioValue" select="@CodedValue"/>
								<!-- changed by J.Aerts for i18n -->
								<!--xsl:with-param name="RadioText" select="./odm:Decode/odm:TranslatedText"/-->
								<xsl:with-param name="RadioText">
									<xsl:value-of select="./odm:Decode/odm:TranslatedText"/>
<!--
									<xsl:choose>
										<xsl:when test="./odm:Decode/odm:TranslatedText[@xml:lang=$LANGUAGE]">
											<xsl:value-of select="./odm:Decode/odm:TranslatedText[@xml:lang=$LANGUAGE]"/>
										</xsl:when>
										<xsl:when test="./odm:Decode/odm:TranslatedText[starts-with($LANGUAGE,@xml:lang)]">
		 									<xsl:value-of select="./odm:Decode/odm:TranslatedText[starts-with($LANGUAGE,@xml:lang)]"/>
		 								</xsl:when>
		 								<xsl:otherwise><xsl:value-of select="./odm:Decode/odm:TranslatedText[not(@xml:lang)]"/></xsl:otherwise>
		 							</xsl:choose>
-->
								</xsl:with-param>
							</xsl:call-template>		
						</xsl:for-each>
						<!-- ODM 1.3 support for EnumeratedItem -->
						<xsl:for-each select="odm:EnumeratedItem">
							<xsl:call-template name="Radio">
								<xsl:with-param name="RadioName" select="@OID"/>
								<xsl:with-param name="RadioValue" select="@CodedValue"/>
								<xsl:with-param name="RadioText" select="@CodedValue"/>
							</xsl:call-template>
						</xsl:for-each>
					</xsl:if>
	 			</xsl:for-each>
	 		</xsl:when>
	 		
	 		<!-- Simple Text Field -->
			<xsl:when test="$ID_DT='text' or $ID_DT = 'string'">
		  		<xsl:choose>
			  		<xsl:when test="./@Length">
				  		<xsl:choose>
					  		<xsl:when test="@Length > 100">
							    <textarea>
							    	<xsl:attribute name="name"><xsl:value-of select="@OID"/></xsl:attribute>
					  				<xsl:attribute name="rows">5</xsl:attribute>
							  		<xsl:attribute name="cols">40</xsl:attribute>
							  		<xsl:text>    </xsl:text>
							  	</textarea>
					  		</xsl:when>
				  			<xsl:otherwise>
					  			<input>
						  			<xsl:attribute name="type">text</xsl:attribute>
					  				<xsl:attribute name="name"><xsl:value-of select="$OID"/></xsl:attribute>
					  				<xsl:choose>
							  			<xsl:when test="@Length > 50">
									  		<xsl:attribute name="size">50</xsl:attribute>
							  			</xsl:when>
						  				<xsl:otherwise>
							  				<xsl:attribute name="size"><xsl:value-of select="@Length"/></xsl:attribute>
						  				</xsl:otherwise>
						  			</xsl:choose>
					  				<xsl:attribute name="maxlength"><xsl:value-of select="@Length"/></xsl:attribute>
			  					</input>
		  					</xsl:otherwise>
				  		</xsl:choose>
			  			</xsl:when>
		  			<xsl:otherwise>
			  			<i>Missing length attribute</i>	
		  			</xsl:otherwise>
	  			</xsl:choose>
			</xsl:when>
	
			<!-- Integer field -->
			<xsl:when test="$ID_DT='integer'">
				<!-- ODM 1.3: Length is not mandatory anymore - we take a default of 8 -->
				<xsl:variable name="LENGTH">
					<xsl:choose>
						<xsl:when test="@Length"><xsl:value-of select="@Length"/></xsl:when>
						<xsl:otherwise>8</xsl:otherwise>
					</xsl:choose>
				</xsl:variable>
			    <input>
					  <xsl:attribute name="type">text</xsl:attribute>
					  <xsl:attribute name="name"><xsl:value-of select="$OID"/></xsl:attribute>
					  <xsl:attribute name="size"><xsl:value-of select="$LENGTH"/></xsl:attribute>
					  <xsl:attribute name="maxlength"><xsl:value-of select="@LENGTH"/></xsl:attribute>
				</input>
		
			</xsl:when>
			
			<!-- Float field -->
			<xsl:when test="$ID_DT='float' or $ID_DT='double'">
				<!-- ODM 1.3: Length and SignificantDigits are not mandatory anymore - we take a default of 8 for Length
					and a default of 2 for SignificantDigits -->
				<xsl:variable name="LENGTH">
					<xsl:choose>
						<xsl:when test="@Length"><xsl:value-of select="@Length"/></xsl:when>
						<xsl:otherwise>8</xsl:otherwise>
					</xsl:choose>
				</xsl:variable>
				<xsl:variable name="SIGNIFICANTDIGITS">
					<xsl:choose>
						<xsl:when test="@SignificantDigits"><xsl:value-of select="@SignificantDigits"/></xsl:when>
						<xsl:otherwise>2</xsl:otherwise>
					</xsl:choose>
				</xsl:variable>
				<input>
					  <xsl:attribute name="type">text</xsl:attribute>
					  <xsl:attribute name="name"><xsl:value-of select="$OID"/>A</xsl:attribute>
					  <xsl:attribute name="size"><xsl:value-of select="$LENGTH"/></xsl:attribute>
					  <xsl:attribute name="maxlength"><xsl:value-of select="$LENGTH"/></xsl:attribute>
			  	</input>
				.
		  	  	<input>
					  <xsl:attribute name="type">text</xsl:attribute>
					  <xsl:attribute name="name"><xsl:value-of select="$OID"/>B</xsl:attribute>
					  <xsl:attribute name="size"><xsl:value-of select="$SIGNIFICANTDIGITS"/></xsl:attribute>
					  <xsl:attribute name="maxlength"><xsl:value-of select="$SIGNIFICANTDIGITS"/></xsl:attribute>
				</input>
			</xsl:when>
		
			<!-- Date field -->	
			<xsl:when test="$ID_DT='date' or $ID_DT='partialDate' or $ID_DT='incompleteDate'">
			  <xsl:call-template name="date"/>
			</xsl:when>
			
			<!-- Time field -->	
			<xsl:when test="$ID_DT='time' or $ID_DT='partialTime' or $ID_DT='incompleteTime'">
			  <xsl:call-template name="Time"/>
			</xsl:when>
			
			<!-- DateTime field -->	
			<xsl:when test="$ID_DT='datetime' or $ID_DT='partialDatetime' or $ID_DT='incompleteDatetime'">
			  <xsl:call-template name="date"/><b> + </b> 
			  <xsl:call-template name="Time"/>
			</xsl:when>
			
			<!-- new types for ODM 1.3 and 1.3.1 -->
			<!-- 'string' is being dealt with as 'text' (see higher up) -->
			<!-- 'double' is being dealt with as 'float' (see higher up) -->
			<!-- 'partialDate' is being dealt with as 'date' (see higher up) -->
			<!-- 'partialTime' is being dealt with as 'date' (see higher up) -->
			<!-- 'partialDatetime' is being dealt with as 'datetime' (see higher up) -->
			<!-- 'incompleteDatetime' is being dealt with as 'datetime' (see higher up) -->
			<!-- 'incompleteDate' is being dealt with as 'date' (see higher up) -->
			<!-- 'incompleteTime' is being dealt with as 'time' (see higher up) -->
			
			<xsl:when test="$ID_DT='boolean'">
				<input type="checkbox" name="@OID"/>
			</xsl:when>
			
			<!-- hexBinary | base64Binary | hexFloat | base64Float -->
			<xsl:when test="$ID_DT='hexBinary' or $ID_DT='base64Binary' or $ID_DT='hexFloat' or $ID_DT='base64Float'">
				<input>
					<xsl:attribute name="type">text</xsl:attribute>
					<xsl:attribute name="name"><xsl:value-of select="$OID"/></xsl:attribute>
			  		<xsl:attribute name="size">25</xsl:attribute>
			  	</input>
			</xsl:when>
			
			<!-- URI -->
			<xsl:when test="$ID_DT='URI'">
				<input>
					<xsl:attribute name="type">text</xsl:attribute>
					<xsl:attribute name="name"><xsl:value-of select="$OID"/></xsl:attribute>
			  		<xsl:attribute name="size">50</xsl:attribute>
			  	</input>
			</xsl:when>
			
			<!-- TODO: intervalDatetime -->
			
			<!-- durationDateTime -->
			<xsl:when test="$ID_DT='durationDatetime'">
				<!-- Years part -->
				<table border='0' cellspacing='0' cellpadding='2'>
					<tr>
						<td><p class="info">Years: </p></td>
						<td><input>
							<xsl:attribute name="type">text</xsl:attribute>
							<xsl:attribute name="name"><xsl:value-of select="$OID"/></xsl:attribute>
							<xsl:attribute name="size">4</xsl:attribute>
						</input></td>
					</tr>
					<tr>
						<td><p class="info">Months: </p></td>
						<td><input>
							<xsl:attribute name="type">text</xsl:attribute>
							<xsl:attribute name="name"><xsl:value-of select="$OID"/></xsl:attribute>
							<xsl:attribute name="size">4</xsl:attribute>
						</input></td>
					</tr>
					<tr>
						<td><p class="info">Days: </p></td>
						<td><input>
							<xsl:attribute name="type">text</xsl:attribute>
							<xsl:attribute name="name"><xsl:value-of select="$OID"/></xsl:attribute>
							<xsl:attribute name="size">4</xsl:attribute>
						</input></td>
					</tr>
					<tr>
						<td><p class="info">Hours: </p></td>
						<td><input>
							<xsl:attribute name="type">text</xsl:attribute>
							<xsl:attribute name="name"><xsl:value-of select="$OID"/></xsl:attribute>
							<xsl:attribute name="size">4</xsl:attribute>
						</input></td>
					</tr>
					<tr>
						<td><p class="info">Minutes: </p></td>
						<td><input>
							<xsl:attribute name="type">text</xsl:attribute>
							<xsl:attribute name="name"><xsl:value-of select="$OID"/></xsl:attribute>
							<xsl:attribute name="size">4</xsl:attribute>
						</input></td>
					</tr>
					<tr>
						<td><p class="info">Seconds: </p></td>
						<td><input>
							<xsl:attribute name="type">text</xsl:attribute>
							<xsl:attribute name="name"><xsl:value-of select="$OID"/></xsl:attribute>
							<xsl:attribute name="size">4</xsl:attribute>
						</input></td>
					</tr>
				</table>
			</xsl:when>
			
			
			<!-- Something we do not handle yet -->
			<xsl:otherwise>
			  <i>Not represented yet</i>
			</xsl:otherwise>
		</xsl:choose>
		
		<!-- If MeasurementUnitRef present, add the units -->
		<xsl:if test="./odm:MeasurementUnitRef[@MeasurementUnitOID]">
			<xsl:for-each select="./odm:MeasurementUnitRef">
			 	<!--
			 		The for-each is not strictly required, but processor fails to set $ID_MUOID
			 		<xsl:variable name="ID_MUOID" select="./odm:MeasurementUnitRef[@MeasurementUnitOID]"/>
			 	-->
			 	<xsl:variable name="ID_MUOID" select="@MeasurementUnitOID"/>  
				<xsl:for-each select="/odm:ODM/odm:Study/odm:BasicDefinitions/odm:MeasurementUnit">
			 		<xsl:if test="@OID=$ID_MUOID">
			 			<!-- i18n by J.Aerts -->
			 			<xsl:choose>
			 				<xsl:when test="./odm:Symbol/odm:TranslatedText[@xml:lang=$LANGUAGE]">
			 					( <xsl:value-of select="./odm:Symbol/odm:TranslatedText[@xml:lang=$LANGUAGE]"/> )
			 				</xsl:when>
			 				<xsl:when test="./odm:Symbol/odm:TranslatedText[starts-with($LANGUAGE,@xml:lang)]">
			 					( <xsl:value-of select="./odm:Symbol/odm:TranslatedText[starts-with($LANGUAGE,@xml:lang)]"/> )
			 				</xsl:when>
			 				<xsl:otherwise>
			 					( <xsl:value-of select="./odm:Symbol/odm:TranslatedText[not(@xml:lang)]"/>
			 				</xsl:otherwise>
			 			</xsl:choose>
					</xsl:if>
		 		</xsl:for-each>
	 		</xsl:for-each>
		</xsl:if>
		
	</xsl:template>

	<!--
		Template: Date
		Purpose:  Builds a date control.
	-->
	<xsl:template name="date">
		<xsl:call-template name="day"/>
		<xsl:call-template name="month"/>
		<xsl:call-template name="year"/>
	</xsl:template>
	
	<!--
		Template: Time
		Purpose:  Builds a time control.
	-->
	<xsl:template name="Time">
		<xsl:call-template name="Hour"/><b>:</b>
		<xsl:call-template name="Minute"/><b>:</b>
		<!-- seconds added by J.Aerts -->
		<xsl:call-template name="Second"/>
	</xsl:template>
	
	<!--
		Template: Day
		Purpose:  Builds a HTML select control for days as part of a date control
	-->
	<xsl:template name="day">
		<select>
			<xsl:attribute name="name">XXX</xsl:attribute>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="1"/>
				<xsl:with-param name="optiontext" select="1"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="2"/>
				<xsl:with-param name="optiontext" select="2"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="3"/>
				<xsl:with-param name="optiontext" select="3"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="4"/>
				<xsl:with-param name="optiontext" select="4"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="5"/>
				<xsl:with-param name="optiontext" select="5"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="6"/>
				<xsl:with-param name="optiontext" select="6"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="7"/>
				<xsl:with-param name="optiontext" select="7"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="8"/>
				<xsl:with-param name="optiontext" select="8"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="9"/>
				<xsl:with-param name="optiontext" select="9"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="10"/>
				<xsl:with-param name="optiontext" select="10"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="11"/>
				<xsl:with-param name="optiontext" select="11"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="12"/>
				<xsl:with-param name="optiontext" select="12"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="13"/>
				<xsl:with-param name="optiontext" select="13"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="14"/>
				<xsl:with-param name="optiontext" select="14"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="15"/>
				<xsl:with-param name="optiontext" select="15"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="16"/>
				<xsl:with-param name="optiontext" select="16"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="17"/>
				<xsl:with-param name="optiontext" select="17"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="18"/>
				<xsl:with-param name="optiontext" select="18"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="19"/>
				<xsl:with-param name="optiontext" select="19"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="20"/>
				<xsl:with-param name="optiontext" select="20"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="21"/>
				<xsl:with-param name="optiontext" select="21"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="22"/>
				<xsl:with-param name="optiontext" select="22"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="23"/>
				<xsl:with-param name="optiontext" select="23"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="24"/>
				<xsl:with-param name="optiontext" select="24"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="25"/>
				<xsl:with-param name="optiontext" select="25"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="26"/>
				<xsl:with-param name="optiontext" select="26"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="27"/>
				<xsl:with-param name="optiontext" select="27"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="28"/>
				<xsl:with-param name="optiontext" select="28"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="29"/>
				<xsl:with-param name="optiontext" select="29"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="30"/>
				<xsl:with-param name="optiontext" select="30"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="31"/>
				<xsl:with-param name="optiontext" select="31"/>
			</xsl:call-template>
		</select>
	</xsl:template>
	
	<!--
		Template: Month
		Purpose:  Builds a HTML select control for months as part of a date control
	-->
	<xsl:template name="month">
		<select>
			<xsl:attribute name="name">M123</xsl:attribute>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="1"/>
				<xsl:with-param name="optiontext" select="'Jan'"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="2"/>
				<xsl:with-param name="optiontext" select="'Feb'"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="3"/>
				<xsl:with-param name="optiontext" select="'Mar'"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="4"/>
				<xsl:with-param name="optiontext" select="'Apr'"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="5"/>
				<xsl:with-param name="optiontext" select="'May'"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="6"/>
				<xsl:with-param name="optiontext" select="'Jun'"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="7"/>
				<xsl:with-param name="optiontext" select="'Jul'"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="8"/>
				<xsl:with-param name="optiontext" select="'Aug'"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="9"/>
				<xsl:with-param name="optiontext" select="'Sep'"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="10"/>
				<xsl:with-param name="optiontext" select="'Oct'"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="11"/>
				<xsl:with-param name="optiontext" select="'Nov'"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="12"/>
				<xsl:with-param name="optiontext" select="'Dec'"/>
			</xsl:call-template>
		</select>
	</xsl:template>
	
	<!--
		Template: Year
		Purpose:  Builds a HTML text control for entering years as part of a date control.
	-->
	<xsl:template name="year">
		<input>
			<xsl:attribute name="type">text</xsl:attribute>
			<xsl:attribute name="name">YYYY</xsl:attribute>
			<xsl:attribute name="size">4</xsl:attribute>
			<xsl:attribute name="maxlength">4</xsl:attribute>
		</input>
	</xsl:template>
	
	<!--
		Template: Hour
		Purpose:  Builds a HTML select control for hours as part of a time control
	-->
	<xsl:template name="Hour">
		<select>
			<xsl:attribute name="name">XXX</xsl:attribute>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="0"/>
				<xsl:with-param name="optiontext">00</xsl:with-param>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="1"/>
				<xsl:with-param name="optiontext">01</xsl:with-param>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="2"/>
				<xsl:with-param name="optiontext">02</xsl:with-param>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="3"/>
				<xsl:with-param name="optiontext">03</xsl:with-param>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="4"/>
				<xsl:with-param name="optiontext">04</xsl:with-param>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="5"/>
				<xsl:with-param name="optiontext">05</xsl:with-param>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="6"/>
				<xsl:with-param name="optiontext">06</xsl:with-param>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="7"/>
				<xsl:with-param name="optiontext">07</xsl:with-param>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="8"/>
				<xsl:with-param name="optiontext">08</xsl:with-param>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="9"/>
				<xsl:with-param name="optiontext">09</xsl:with-param>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="10"/>
				<xsl:with-param name="optiontext" select="10"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="11"/>
				<xsl:with-param name="optiontext" select="11"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="12"/>
				<xsl:with-param name="optiontext" select="12"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="13"/>
				<xsl:with-param name="optiontext" select="13"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="14"/>
				<xsl:with-param name="optiontext" select="14"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="15"/>
				<xsl:with-param name="optiontext" select="15"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="16"/>
				<xsl:with-param name="optiontext" select="16"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="17"/>
				<xsl:with-param name="optiontext" select="17"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="18"/>
				<xsl:with-param name="optiontext" select="18"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="19"/>
				<xsl:with-param name="optiontext" select="19"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="20"/>
				<xsl:with-param name="optiontext" select="20"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="21"/>
				<xsl:with-param name="optiontext" select="21"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="22"/>
				<xsl:with-param name="optiontext" select="22"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="23"/>
				<xsl:with-param name="optiontext" select="23"/>
			</xsl:call-template>
		</select>
	</xsl:template>
	
	<!--
		Template: Minute
		Purpose:  Builds a HTML select control for minutes as part of a time control
	-->
	<xsl:template name="Minute">
		<select>
			<xsl:attribute name="name">XXX</xsl:attribute>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="0"/>
				<xsl:with-param name="optiontext">00</xsl:with-param>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="1"/>
				<xsl:with-param name="optiontext">01</xsl:with-param>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="2"/>
				<xsl:with-param name="optiontext">02</xsl:with-param>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="3"/>
				<xsl:with-param name="optiontext">03</xsl:with-param>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="4"/>
				<xsl:with-param name="optiontext">04</xsl:with-param>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="5"/>
				<xsl:with-param name="optiontext">05</xsl:with-param>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="6"/>
				<xsl:with-param name="optiontext">06</xsl:with-param>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="7"/>
				<xsl:with-param name="optiontext">07</xsl:with-param>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="8"/>
				<xsl:with-param name="optiontext">08</xsl:with-param>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="9"/>
				<xsl:with-param name="optiontext">09</xsl:with-param>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="10"/>
				<xsl:with-param name="optiontext" select="10"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="11"/>
				<xsl:with-param name="optiontext" select="11"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="12"/>
				<xsl:with-param name="optiontext" select="12"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="13"/>
				<xsl:with-param name="optiontext" select="13"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="14"/>
				<xsl:with-param name="optiontext" select="14"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="15"/>
				<xsl:with-param name="optiontext" select="15"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="16"/>
				<xsl:with-param name="optiontext" select="16"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="17"/>
				<xsl:with-param name="optiontext" select="17"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="18"/>
				<xsl:with-param name="optiontext" select="18"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="19"/>
				<xsl:with-param name="optiontext" select="19"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="20"/>
				<xsl:with-param name="optiontext" select="20"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="21"/>
				<xsl:with-param name="optiontext" select="21"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="22"/>
				<xsl:with-param name="optiontext" select="22"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="23"/>
				<xsl:with-param name="optiontext" select="23"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="24"/>
				<xsl:with-param name="optiontext" select="24"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="25"/>
				<xsl:with-param name="optiontext" select="25"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="26"/>
				<xsl:with-param name="optiontext" select="26"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="27"/>
				<xsl:with-param name="optiontext" select="27"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="28"/>
				<xsl:with-param name="optiontext" select="28"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="29"/>
				<xsl:with-param name="optiontext" select="29"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="30"/>
				<xsl:with-param name="optiontext" select="30"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="31"/>
				<xsl:with-param name="optiontext" select="31"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="32"/>
				<xsl:with-param name="optiontext" select="32"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="33"/>
				<xsl:with-param name="optiontext" select="33"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="34"/>
				<xsl:with-param name="optiontext" select="34"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="35"/>
				<xsl:with-param name="optiontext" select="35"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="36"/>
				<xsl:with-param name="optiontext" select="36"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="37"/>
				<xsl:with-param name="optiontext" select="37"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="38"/>
				<xsl:with-param name="optiontext" select="38"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="39"/>
				<xsl:with-param name="optiontext" select="39"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="40"/>
				<xsl:with-param name="optiontext" select="40"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="41"/>
				<xsl:with-param name="optiontext" select="41"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="42"/>
				<xsl:with-param name="optiontext" select="42"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="43"/>
				<xsl:with-param name="optiontext" select="43"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="44"/>
				<xsl:with-param name="optiontext" select="44"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="45"/>
				<xsl:with-param name="optiontext" select="45"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="46"/>
				<xsl:with-param name="optiontext" select="46"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="47"/>
				<xsl:with-param name="optiontext" select="47"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="48"/>
				<xsl:with-param name="optiontext" select="48"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="49"/>
				<xsl:with-param name="optiontext" select="49"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="50"/>
				<xsl:with-param name="optiontext" select="50"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="51"/>
				<xsl:with-param name="optiontext" select="51"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="52"/>
				<xsl:with-param name="optiontext" select="52"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="53"/>
				<xsl:with-param name="optiontext" select="53"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="54"/>
				<xsl:with-param name="optiontext" select="54"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="55"/>
				<xsl:with-param name="optiontext" select="55"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="56"/>
				<xsl:with-param name="optiontext" select="56"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="57"/>
				<xsl:with-param name="optiontext" select="57"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="58"/>
				<xsl:with-param name="optiontext" select="58"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="59"/>
				<xsl:with-param name="optiontext" select="59"/>
			</xsl:call-template>
		</select>
	</xsl:template>
	
	<!--
		Template: Second
		Purpose:  Builds a HTML select control for seconds as part of a time control
	-->
	
	<xsl:template name="Second">
		<select>
			<xsl:attribute name="name">XXX</xsl:attribute>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="0"/>
				<xsl:with-param name="optiontext">00</xsl:with-param>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="1"/>
				<xsl:with-param name="optiontext">01</xsl:with-param>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="2"/>
				<xsl:with-param name="optiontext">02</xsl:with-param>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="3"/>
				<xsl:with-param name="optiontext">03</xsl:with-param>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="4"/>
				<xsl:with-param name="optiontext">04</xsl:with-param>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="5"/>
				<xsl:with-param name="optiontext">05</xsl:with-param>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="6"/>
				<xsl:with-param name="optiontext">06</xsl:with-param>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="7"/>
				<xsl:with-param name="optiontext">07</xsl:with-param>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="8"/>
				<xsl:with-param name="optiontext">08</xsl:with-param>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="9"/>
				<xsl:with-param name="optiontext">09</xsl:with-param>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="10"/>
				<xsl:with-param name="optiontext" select="10"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="11"/>
				<xsl:with-param name="optiontext" select="11"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="12"/>
				<xsl:with-param name="optiontext" select="12"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="13"/>
				<xsl:with-param name="optiontext" select="13"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="14"/>
				<xsl:with-param name="optiontext" select="14"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="15"/>
				<xsl:with-param name="optiontext" select="15"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="16"/>
				<xsl:with-param name="optiontext" select="16"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="17"/>
				<xsl:with-param name="optiontext" select="17"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="18"/>
				<xsl:with-param name="optiontext" select="18"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="19"/>
				<xsl:with-param name="optiontext" select="19"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="20"/>
				<xsl:with-param name="optiontext" select="20"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="21"/>
				<xsl:with-param name="optiontext" select="21"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="22"/>
				<xsl:with-param name="optiontext" select="22"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="23"/>
				<xsl:with-param name="optiontext" select="23"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="24"/>
				<xsl:with-param name="optiontext" select="24"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="25"/>
				<xsl:with-param name="optiontext" select="25"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="26"/>
				<xsl:with-param name="optiontext" select="26"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="27"/>
				<xsl:with-param name="optiontext" select="27"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="28"/>
				<xsl:with-param name="optiontext" select="28"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="29"/>
				<xsl:with-param name="optiontext" select="29"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="30"/>
				<xsl:with-param name="optiontext" select="30"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="31"/>
				<xsl:with-param name="optiontext" select="31"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="32"/>
				<xsl:with-param name="optiontext" select="32"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="33"/>
				<xsl:with-param name="optiontext" select="33"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="34"/>
				<xsl:with-param name="optiontext" select="34"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="35"/>
				<xsl:with-param name="optiontext" select="35"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="36"/>
				<xsl:with-param name="optiontext" select="36"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="37"/>
				<xsl:with-param name="optiontext" select="37"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="38"/>
				<xsl:with-param name="optiontext" select="38"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="39"/>
				<xsl:with-param name="optiontext" select="39"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="40"/>
				<xsl:with-param name="optiontext" select="40"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="41"/>
				<xsl:with-param name="optiontext" select="41"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="42"/>
				<xsl:with-param name="optiontext" select="42"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="43"/>
				<xsl:with-param name="optiontext" select="43"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="44"/>
				<xsl:with-param name="optiontext" select="44"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="45"/>
				<xsl:with-param name="optiontext" select="45"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="46"/>
				<xsl:with-param name="optiontext" select="46"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="47"/>
				<xsl:with-param name="optiontext" select="47"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="48"/>
				<xsl:with-param name="optiontext" select="48"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="49"/>
				<xsl:with-param name="optiontext" select="49"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="50"/>
				<xsl:with-param name="optiontext" select="50"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="51"/>
				<xsl:with-param name="optiontext" select="51"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="52"/>
				<xsl:with-param name="optiontext" select="52"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="53"/>
				<xsl:with-param name="optiontext" select="53"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="54"/>
				<xsl:with-param name="optiontext" select="54"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="55"/>
				<xsl:with-param name="optiontext" select="55"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="56"/>
				<xsl:with-param name="optiontext" select="56"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="57"/>
				<xsl:with-param name="optiontext" select="57"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="58"/>
				<xsl:with-param name="optiontext" select="58"/>
			</xsl:call-template>
			<xsl:call-template name="option">
				<xsl:with-param name="optionvalue" select="59"/>
				<xsl:with-param name="optiontext" select="59"/>
			</xsl:call-template>
		</select>
	</xsl:template>
	
	<!--
		Template: Option
		Purpose:  Builds an HTML option element for a select input.
	-->
	<xsl:template name="option">
		<xsl:param name="optionvalue"/>
		<xsl:param name="optiontext"/>
		<option>
			<xsl:attribute name="value">
				<xsl:value-of select="$optionvalue"/>
			</xsl:attribute>
			<xsl:value-of select="$optiontext"/>
		</option>
	</xsl:template>
	
	<!--
		Template: Radio
		Purpose:  Builds an HTML radio button element for a select input.
	-->
	<xsl:template name="Radio">
		<xsl:param name="RadioName"/>
		<xsl:param name="RadioValue"/>
		<xsl:param name="RadioText"/>
		<input type='radio'>
			<xsl:attribute name="name">
				<xsl:value-of select="$RadioName"/>
			</xsl:attribute>
			<xsl:attribute name="value">
				<xsl:value-of select="$RadioValue"/>
			</xsl:attribute>
			<!--xsl:value-of select="$RadioText"/--><!--br/-->
	 	</input><xsl:value-of select="$RadioText"/><br/>
	</xsl:template>

	<!--
		Template: TopLink
		Purpose:  Adds a link to the top of the page.
	-->
	<xsl:template name="TopLink">
		<xsl:param name="Link"/>
		<xsl:param name="LinkText"/>
		<td width='5%'>
			<a>
				<xsl:attribute name="href">#<xsl:value-of select="$Link"/></xsl:attribute>
				<p class='annotation'><xsl:value-of select="$LinkText"/></p>	
			</a>									
		</td>
	</xsl:template>

	<!--
		Template: ListHeading
		Purpose:  Builds a general heading.
	-->
	<xsl:template name="ListHeading">
		<xsl:param name="Width"/>
		<xsl:param name="Title"/>
		<table border='1' cellspacing='0' cellpadding='5'>
			<xsl:attribute name="width">
				<xsl:value-of select="$Width"/>		
			</xsl:attribute>
			<tr>
				<td><p class='head'><xsl:value-of select="$Title"/></p></td>
			</tr>
		</table><br/>
	</xsl:template>
	
	<!--
		Template: InstanceHeading
		Purpose:  Builds a title bar, consisting of a link to the top of the page, the item 
		          title text and a second link to the top. Also the OID is output plus the
		          repeating attribute.
	-->
	<xsl:template name="InstanceHeading">
		<xsl:param name="AnchorName"/>
		<xsl:param name="Class"/>
		<xsl:param name="Name"/>
		<xsl:param name="OID"/>
		<xsl:param name="Repeating"/>
		<xsl:param name="Width"/>
		<xsl:param name="Link"/>
		<xsl:param name="LinkText"/>
		<!-- ODM 1.3.1: skip condition -->
		<!-- IS ON THE 'REF' !
		<xsl:param name="SkipConditionOID"/>
		<xsl:param name="SkipContitionText"/>
		<xsl:param name="SkipConditionFormalExpression"/> -->
		<table border='1' cellspacing='0' cellpadding='5'>
			<xsl:attribute name="width">
				<xsl:value-of select="$Width"/>		
			</xsl:attribute>
			<tr><td>
				<!-- J.Aerts: <a name="..."/> should not contain any childs nor text content -->
				<a>
					<xsl:attribute name="name">
						<xsl:value-of select="$AnchorName"/>
					</xsl:attribute>
				</a>
				<table width='100%' border='0' cellspacing='0' cellpadding='2'>
					<tr>
						<xsl:call-template name="TopLink">
							<xsl:with-param name="Link" select="$Link"/>
							<xsl:with-param name="LinkText" select="$LinkText"/>
						</xsl:call-template>
						<td width='90%'>
							<p>
								<xsl:attribute name="class">
									<xsl:value-of select="$Class"/>
								</xsl:attribute>
								<b><xsl:value-of select="$Name"/></b>
							</p>
							<p class='annotation1'>
								<i>OID=<xsl:value-of select="$OID"/>	
								<xsl:choose>
									<xsl:when test="$Repeating=Yes">
										Repeating=<xsl:value-of select="$Repeating"/>
									</xsl:when>
								 	<xsl:when test="$Repeating=No">
										Repeating=<xsl:value-of select="$Repeating"/>
									</xsl:when>
								</xsl:choose>
								</i>
							</p>
						</td>
						<!-- for ODM 1.3.1: skip condition -->
						<!--
						<xsl:if test="$SkipConditionOID != ''">
							<td>Skip when: <br/>
							<xsl:if test="$SkipContitionText != ''"><xsl:value-of select="$SkipContitionText"/><br/></xsl:if>
							<xsl:if test="$SkipConditionFormalExpression != ''">Skip expression: <br/></xsl:if>
							Condition OID: <xsl:value-of select="$SkipConditionOID"/>
							</td>
						</xsl:if>
						-->
						<!-- link to top-->
						<xsl:call-template name="TopLink">
							<xsl:with-param name="Link" select="$Link"/>
							<xsl:with-param name="LinkText" select="$LinkText"/>
						</xsl:call-template>
					</tr>
				</table>
				<!--/a-->
			</td></tr>
		</table><br/>
	</xsl:template>
	
</xsl:stylesheet>