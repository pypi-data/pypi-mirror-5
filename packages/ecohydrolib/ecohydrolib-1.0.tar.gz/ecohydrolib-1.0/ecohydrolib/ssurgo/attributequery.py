"""@package ecohydrolib.ssurgo.attributequery
    
@brief Make tabular queries against USDA Soil Data Mart SOAP web service interface
@note Requires python-httplib2 to be installed, else requests to soil data mart may timeout

This software is provided free of charge under the New BSD License. Please see
the following license information:

Copyright (c) 2013, University of North Carolina at Chapel Hill
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * Neither the name of the University of North Carolina at Chapel Hill nor the
      names of its contributors may be used to endorse or promote products
      derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE UNIVERSITY OF NORTH CAROLINA AT CHAPEL HILL
BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR 
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT 
LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


@author Brian Miles <brian_miles@unc.edu>
"""
import cStringIO
import xml.sax

import numpy as np
from lxml import etree
from pysimplesoap.client import SoapClient

from saxhandlers import SSURGOMUKEYQueryHandler

attributeList = ['avgKsat', 'avgClay', 'avgSilt', 'avgSand', 'avgPorosity','pmgroupname','texture','tecdesc']
attributeListNumeric = ['avgKsat', 'avgClay', 'avgSilt', 'avgSand', 'avgPorosity']

def strListToString(strList):
    """ Converts a Python list of string values into a string containing quoted, 
        comma separated representation of the list.
        
        @param strList List of strings
        
        @return String containing quoted, comma separated representation of the list
    """
    numStr = len(strList)
    assert(numStr > 0)
    
    output = cStringIO.StringIO()
    for i in range(numStr - 1):
        output.write("'%s'," % (strList[i],))
    output.write("'%s'" % (strList[numStr-1],))
    
    returnStr = output.getvalue()
    output.close()
    return returnStr

def computeWeightedAverageKsatClaySandSilt(soilAttrTuple):
    """ Computes weighted average for Ksat, %clay/silt/sand for a SSURGO mukey based on values
        for each component in the mukey; weights based on component.comppct_r.
    
        @param soilAttrTuple Tuple returned from getParentMatKsatTexturePercentClaySiltSandForComponentsInMUKEYs
    
        @return Tuple containing: (1) a list containing column names; (2) a list of lists containing averaged soil properties for each mukey
    """
    data = list()
    representativeComponentDict = dict()
    idx = 0
    
    # Convert numbers as text to numbers
    for row in soilAttrTuple[1]:
        #print row
        mukey = int(row[0])
        comppct_r = int(row[2])
        try:
            maxRepComp = representativeComponentDict[mukey][1]
            if maxRepComp < comppct_r:
                representativeComponentDict[mukey] = (idx, comppct_r)
        except KeyError:
            representativeComponentDict[mukey] = (idx, comppct_r)
        try:
            hzdept_r = float(row[7])
        except ValueError:
            hzdept_r = -1
        try:
            ksat_r = float(row[8])
        except ValueError:
            ksat_r = -1
        try:
            claytotal_r = float(row[9])
        except ValueError:
            claytotal_r = -1
        try:
            silttotal_r = float(row[10])
        except ValueError:
            silttotal_r = -1
        try:
            sandtotal_r = float(row[11])
        except ValueError:
            sandtotal_r = -1
        try:
            wsatiated_r = float(row[12]) # a.k.a. porosity
        except ValueError:
            wsatiated_r = -1
    
        data.append([mukey, row[1], comppct_r, row[3], row[4], row[5], row[6], hzdept_r, ksat_r, claytotal_r, silttotal_r, sandtotal_r, wsatiated_r])
        idx = idx + 1

    mukeyCol = [row[0] for row in data]
    comppctCol = [row[2] for row in data]
    ksatCol = [row[8] for row in data]
    clayCol = [row[9] for row in data]
    siltCol = [row[10] for row in data]
    sandCol = [row[11] for row in data]
    porosityCol = [row[12] for row in data]

    # Put values into Numpy 2-D array    
    npdata = np.array([mukeyCol, comppctCol, ksatCol, clayCol, siltCol, sandCol, porosityCol]).transpose()
    #print np.shape(npdata)
    # Remove duplicate rows 
    #   (which will arise because there can be multiple parent material groups for a given component)
    npdata = np.array([np.array(x) for x in set(tuple(x) for x in npdata)])
    #print np.shape(npdata)
    # Register NoData values
    npdata = np.ma.masked_where(npdata == -1, npdata)

    # Calculate weighted average using component.comppct_r as weights
    avgSoilAttr = list()
    mukeySet = set(mukeyCol)
    for mukey in mukeySet:
        mySubSet = npdata[npdata[:,0] == mukey]
        myComppct = mySubSet[:,1]
        myKsat = mySubSet[:,2]
        myClay = mySubSet[:,3]
        mySilt = mySubSet[:,4]
        mySand = mySubSet[:,5]
        myPorosity =  mySubSet[:,6]
        # Calculate weighted averages, ignoring NoData values
        avgKsat = np.ma.average(myKsat, weights=myComppct)
        avgClay = np.ma.average(myClay, weights=myComppct)
        avgSilt = np.ma.average(mySilt, weights=myComppct)
        avgSand = np.ma.average(mySand, weights=myComppct)
        avgPorosity = np.ma.average(myPorosity, weights=myComppct)
        
        # Get modal value for qualitative values (pmgroupname, texture, tecdesc)
        maxRepIdx = representativeComponentDict[mukey][0]
        pmgroupname = data[maxRepIdx][3]
        texture = data[maxRepIdx][4]
        texdesc = data[maxRepIdx][5]
        
        avgSoilAttr.append([mukey, avgKsat, avgClay, avgSilt, avgSand, avgPorosity, pmgroupname, texture, texdesc])
    avgSoilHeaders = list(attributeList)
    avgSoilHeaders.insert(0, 'mukey')
    
    return (avgSoilHeaders, avgSoilAttr)

def joinSSURGOAttributesToFeaturesByMUKEY(gmlFile, typeName, ssurgoAttributes):
    """ Join SSURGO tabular attributes to MapunitPoly or MapunitPolyExtended features based on
        MUKEY. Will write GML file and shapefile for features, and raster layers for each column
        vallue (see below).
    
        @param gmlFile A file handle associated with a SSURGO MapunitPoly or MapunitPolyExtended
        @param typeName String of either 'MapunitPoly' or 'MapunitPolyExtended'
        @param ssurgoAttributes Tuple containing two lists: (1) list of column names; (2) list of
        column values.  Assumes the following column names and order:
        ['mukey', 'avgKsat', 'avgClay', 'avgSilt', 'avgSand', 'avgPorosity']
    
        @return String representing the GML file with attributes joined   
    """
    assert(typeName == 'MapunitPoly' or typeName == 'MapunitPolyExtended')
    
    # Index attributes by MUKEY
    attributeDict = dict()
    idx = 0
    for row in ssurgoAttributes[1]:
        myMukey = row[0]
        attributeDict[myMukey] = idx
        idx = idx + 1
    
    tree = etree.parse(gmlFile)
    # Find all MUKEY elements
    # /wfs:FeatureCollection/gml:featureMember/ms:MapunitPolyExtended/ms:MUKEY
    # /wfs:FeatureCollection/gml:featureMember/ms:MapunitPoly/ms:MUKEY
    mukeyElems = tree.xpath("/wfs:FeatureCollection/gml:featureMember/ms:%s/ms:MUKEY" % (typeName,),
                        namespaces={'wfs': 'http://www.opengis.net/wfs',
                                    'gml': 'http://www.opengis.net/gml',
                                    'ms': 'http://mapserver.gis.umn.edu/mapserver'})
    nsMap = {'ms': 'http://mapserver.gis.umn.edu/mapserver'}
    for mukeyElem in mukeyElems:
        mukey = int(mukeyElem.text)
        parent = mukeyElem.getparent()
        # Locate insertion point (i.e. before ms:SHAPE element)
        shapeElem = parent.find('ms:SHAPE',
                                namespaces=nsMap) 
        shapeElemIdx = parent.index(shapeElem)
        insertIdx = shapeElemIdx - 1
        
        try:
            mukeyIdx = attributeDict[mukey]
        except KeyError:
            continue
        currAttrIdx = 1
        for attr in ssurgoAttributes[0][1:]:
            attrElem = etree.Element(attr)
            attrElem.text = str(ssurgoAttributes[1][mukeyIdx][currAttrIdx])
            parent.insert(insertIdx, attrElem)
            currAttrIdx = currAttrIdx + 1
            
    return etree.tostring(tree)

def getParentMatKsatTexturePercentClaySiltSandForComponentsInMUKEYs(mukeyList):
    """ Query USDA soil datamart tabular service for ksat, texture, % clay, % silt, % sand for all
        components in the specified map units.
    
        @param mukeyList List of strings representing the MUKEY of each map unit for which we would 
        like to query attributes.
    
        @return Tuple containing an ordered set (oset.oset) representing column names, and a list, 
        each element containing a list of column values for each row in the SSURGO query result for each map unit
    """ 

    client = SoapClient(wsdl="http://sdmdataaccess.nrcs.usda.gov/Tabular/SDMTabularService.asmx?WSDL",trace=False)

    # Query to get component %, ksat_r, texture, texture description, parent material, horizon name, horizon depth,
    # %clay, %silt, %sand, and porosity (as wsatiated.r, volumetric SWC at or near 0 bar tension) for all components in an MUKEY
    # Will select first non-organic horizon (i.e. horizon names that do not start with O, L, or F)
    QUERY_PROTO = """
SELECT c.mukey, c.cokey, c.comppct_r, p.pmgroupname, tg.texture, tg.texdesc, 
ch.hzname, ch.hzdept_r, ch.ksat_r, ch.claytotal_r, ch.silttotal_r, ch.sandtotal_r, ch.wsatiated_r
FROM component c
LEFT JOIN copmgrp p ON c.cokey=p.cokey AND p.rvindicator='yes'
INNER JOIN chorizon ch ON c.cokey=ch.cokey 
AND ch.hzdept_r=(SELECT TOP(1) hzdept_r FROM chorizon WHERE cokey=c.cokey AND (hzname NOT LIKE 'O' + '%%') and (hzname NOT LIKE 'L' + '%%') and (hzname NOT LIKE 'F' + '%%') ORDER BY hzdept_r ASC)
LEFT JOIN chtexturegrp tg ON ch.chkey=tg.chkey AND tg.rvindicator='yes' AND tg.texture<>'variable' AND tg.texture<>'VAR'
WHERE c.mukey IN (%s) ORDER BY c.cokey"""
    
    mukeyStr = strListToString(mukeyList)
    
    query = QUERY_PROTO % mukeyStr
    #print query
    
    result = client.RunQuery(query)
    resultXmlStr = result['RunQueryResult'].as_xml()

    #debugOut = open('SSURGOAttributesForFeatures.xml', 'w')
    #debugOut.write(resultXmlStr)
    #debugOut.close()

    # Parse results
    handler = SSURGOMUKEYQueryHandler()
    
    xml.sax.parseString(resultXmlStr, handler)

    return (handler.columnNames,handler.results)
    
