import os
from subprocess import *
from lxml import etree
import uwa


STG_ROOT_TAG = 'StGermainData'
STG_NS = 'http://www.vpac.org/StGermain/XML_IO_Handler/Jun2003'
_STG_NS_ETREE = '{%s}' % STG_NS

STG_STRUCT_TAG = "struct"
STG_LIST_TAG = "list"
STG_PARAM_TAG = "param"
STG_MERGE_ATTRIB = "mergeType"
STG_MERGE_TYPES = ['append','merge','replace']

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
    """Gets the value of a parameter from a StGermain XML model file that's a
    child of the given elNode, with the given paramName.
    The value is cast according to the castFunc, which should be a standard
    Python casting function, e.g. 'int', 'double' or 'bool'."""
    paramElt = getParamNode(elNode, paramName)
    if paramElt is not None:
        # Strip any spaces around the parameter name first.
        return castFunc(paramElt.text.strip())
    else:
        return None

def getParamNode(elNode, paramName):
    """Returns the element node (in lxml form) of a particular Param parameter
    that's a child of the given elNode with given paramName.
    If a node with the given name not found, returns none."""
    # The default schema for written files (eg flattened files) is to use
    # "element" and set a type attribute, rather than "param" directly.
    eltNode = _getElementNode(elNode, STG_PARAM_TAG, paramName)
    if eltNode is not None: return eltNode
    for paramNode in elNode.iterchildren(tag=_STG_NS_ETREE+'param'):
        if paramNode.attrib['name'] == paramName:
            return paramNode
            break
    return None

def getStructNode(elNode, structName):
    """Returns the element node (in lxml form) of a particular struct element
    that's a child of the given elNode with given structName.
    If a node with the given name not found, returns none."""
    eltNode = _getElementNode(elNode, STG_STRUCT_TAG, structName)
    if eltNode is not None: return eltNode
    for structNode in elNode.iterchildren(tag=_STG_NS_ETREE+'struct'):
        if structNode.attrib['name'] == structName:
            return structNode
            break
    return None

def getListNode(elNode, listName):
    """Returns the element node (in lxml form) of a particular list element
    that's a child of the given elNode with given listName.
    If a node with the given name not found, returns none."""
    eltNode = _getElementNode(elNode, STG_LIST_TAG, listName)
    if eltNode is not None: return eltNode
    for listNode in elNode.iterchildren(tag=_STG_NS_ETREE+'list'):
        if listNode.attrib['name'] == listName:
            return listNode
            break
    return None

def _getElementNode(elNode, elType, elName):
    """Returns the element node (in lxml form) of a particular element
    that's a child of the given elNode with given elName.
    If a node with the given name not found, returns none.
    (Not designed to be used directly, but by getList etc.)"""
    
    for eltNode in elNode.iterchildren(tag=_STG_NS_ETREE+'element'):
        if eltNode.attrib['type'] == elType and \
                eltNode.attrib['name'] == elName:
            return eltNode
            break
    return None        

##########
# For writing a new XML doc, using the eTree lib

def setMergeType(xmlNode, mergeType):
    if mergeType is not None:
        if mergeType not in STG_MERGE_TYPES:
            raise ValueError("The mergeType provided, '%s', is not one of"\
                " the StGermain Model XML allowed merge types (%s)"\
                % (mergeType, STG_MERGE_TYPES))
        xmlNode.attrib[STG_MERGE_ATTRIB] = mergeType

def writeParam(parentNode, paramName, paramVal, mt=None):
    paramEl=etree.SubElement(parentNode, STG_PARAM_TAG, name=paramName)
    setMergeType(paramEl, mt)
    paramEl.text = str(paramVal)
    return paramEl

def writeParamSet(parentNode, paramsDict, mt=None):
    for paramName, paramVal in paramsDict.iteritems():
        writeParam(parentNode, paramName, paramVal, mt)

def writeParamList(parentNode, listName, paramVals, mt=None):
    '''Write a Stg XML List structure, made up purely of (unnamed) parameters'''
    listElt = etree.SubElement(parentNode, STG_LIST_TAG, name=listName) 
    setMergeType(listElt, mt)
    for paramVal in paramVals:
        etree.SubElement(listElt, STG_PARAM_TAG).text = str(paramVal) 
    return listElt    

def mergeComponent(rootNode, compName, compType):
    '''Write XML to merge a given component to the components list - and
     return new comp elt'''
    assert rootNode.tag == STG_ROOT_TAG
    compList = etree.SubElement(rootNode, STG_STRUCT_TAG, name="components",\
        mergeType="merge") 
    compElt = etree.SubElement(compList, STG_STRUCT_TAG, name=compName)
    writeParam(compElt, "Type", compType)
    return compElt
