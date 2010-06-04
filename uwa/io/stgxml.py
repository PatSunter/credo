import os
from subprocess import *
from lxml import etree
import uwa

stgNSText = '{http://www.vpac.org/StGermain/XML_IO_Handler/Jun2003}'

stgRootTag = "StGermainData"
structTag = "struct"
listTag = "list"
paramTag = "param"
stgMergeTypes = ['append','merge','replace']

def createFlattenedXML(inputFiles):
    '''Flatten a list of provided XML files, using the StGermain
     FlattenXML tool'''
    flattenExe=uwa.getVerifyStgExePath('FlattenXML')

    try:
        p = Popen([flattenExe]+inputFiles, stdout=PIPE, stderr=PIPE)
        (stdout, stderr) = p.communicate()
        # The 2nd clause necessary because FlattenXML doesn't return 
        # proper error codes (ie always returns 0) up to 1.4.2 release
        if p.returncode != 0 or stderr != "":
            raise OSError("Error: Command to create flattened file, '%s' on"
                " input files %s, failed, with error msg:\n%s" \
                % (flattenExe,inputFiles,stderr))
    except OSError, e:
        raise OSError("Unexpected failure to execute Flatten command '%s'"\
            " on input files %s. Error msg was:\n%s"\
            % (flattenExe, inputFiles,str(e)))

    ffile='output.xml'
    return ffile

#########
# For getting stuff out of an existing XML doc

def getParamValue(elNode, paramName, castFunc):
    paramElt = getParam(elNode, paramName)
    if paramElt is not None:
        return castFunc(paramElt.text)
    else:
        return None

def getParam(elNode, paramName):
    for elt in elNode.iterchildren(tag=stgNSText+'element'):
        if elt.attrib['type'] == paramTag and elt.attrib['name'] == paramName:
            return elt
            break
    return None

def getStruct(elNode, structName):
    for elt in elNode.iterchildren(tag=stgNSText+'element'):
        if elt.attrib['type'] == structTag and elt.attrib['name'] == structName:
            return elt
            break
    return None

def getList(elNode, listName):
    for elt in elNode.iterchildren(tag=stgNSText+'element'):
        if elt.attrib['type'] == listTag and elt.attrib['name'] == listName:
            return elt
            break
    return None

##########
# For writing a new XML doc, using the eTree lib

def setMergeType(xmlNode, mergeType):
    if mergeType is not None:
        assert mergeType in stgMergeTypes
        xmlNode.attrib['mergeType']=mergeType

def writeParam(parentNode, paramName, paramVal, mt=None):
    paramEl=etree.SubElement(parentNode, paramTag, name=paramName)
    setMergeType(paramEl, mt)
    paramEl.text = str(paramVal)
    return paramEl

def writeParamSet(parentNode, paramsDict, mt=None):
    for paramName, paramVal in paramsDict.iteritems():
        writeParam(parentNode, paramName, paramVal, mt)

def writeParamList(parentNode, listName, paramVals, mt=None):
    '''Write a Stg XML List structure, made up purely of (unnamed) parameters'''
    listElt = etree.SubElement(parentNode, listTag, name=listName) 
    setMergeType(listElt, mt)
    for paramVal in paramVals:
        etree.SubElement(listElt, paramTag).text = str(paramVal) 
    return listElt    

def mergeComponent(rootNode, compName, compType):
    '''Write XML to merge a given component to the components list - and
     return new comp elt'''
    assert rootNode.tag == stgRootTag
    compList = etree.SubElement(rootNode, structTag, name="components",\
        mergeType="merge") 
    compElt = etree.SubElement(compList, structTag, name=compName)
    writeParam(compElt, "Type", compType)
    return compElt
