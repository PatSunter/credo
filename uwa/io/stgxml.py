import os
from subprocess import *
from lxml import etree
import uwa


STG_ROOT_TAG = 'StGermainData'
STG_NS = 'http://www.vpac.org/StGermain/XML_IO_Handler/Jun2003'
_STG_NS_LXML = '{%s}' % STG_NS

STG_STRUCT_TAG = "struct"
STG_LIST_TAG = "list"
STG_PARAM_TAG = "param"
STG_ELEMENT_TAG = "element"
_stgElementBaseTags = [STG_STRUCT_TAG, STG_LIST_TAG, STG_PARAM_TAG]
STG_MERGE_ATTRIB = "mergeType"
STG_MERGE_TYPES = ['append','merge','replace']
STG_IMPORT_TAG = "import"
STG_PLUGINS_TAG = "plugins"
STG_COMPONENTS_TAG = "components"
STG_TOOLBOX_TAG = "toolbox"
_stgSpecialListTags = [STG_IMPORT_TAG, STG_PLUGINS_TAG]
_stgSpecialStructTags = [STG_COMPONENTS_TAG, STG_ROOT_TAG]
_stgSpecialParamTags = [STG_TOOLBOX_TAG]

############
# Utility functions

def addNsPrefix(tagName):
    """Simple utility func to add the Namespace prefix that LXML adds to element
    tag names when it parses in from a file"""
    return _STG_NS_LXML+tagName

def removeNsPrefix(tagName):
    """Simple utility func to remove the Namespace prefix that LXML adds to
    element tag names when it parses in from a file"""
    if tagName.startswith(_STG_NS_LXML):
        return tagName[len(_STG_NS_LXML):]

###################
# Key function for navigating a hierarchy when strSpec is given in StGermain
# command-line style

def navigateStrSpecHierarchy(currNode, strSpec, insertMode=False):
    """Navigate a document, based on a remaining StGermain command-line style
    element specification.
    Returns currNode, nodeName of the final entry in the hierarchy"""
    # Parse the string, checking if it specifies to recurse into a sub-struct or
    # list.

    if strSpec == "":
        raise ValueError("Can't operate on an empty strSpec string")

    structSepPrefix, structSep, structRem = strSpec.partition(".")
    listSepPrefix, listSep, listFirstRem = structSepPrefix.partition("[")

    # The list is handled slightly different to structs: since list items are
    # un-named, an immediate list spec (eg [5]) with no prefix means we're done.
    if listSep == '[':
        # Check and handle the list separator first, since the code above
        # made sure that this must occur before any structSeps

        # First re-do the partition, to get all remainder
        listStartName, listStartSep, listStartRem = strSpec.partition('[')
        listContents, listEndSep, listEndRem = listStartRem.partition(']')
        if listEndSep != ']':
            raise ValueError("Navigating section \"%s\" specified: badly"\
                " formed list found, not closed correctly with '%s'."
                % (strSpec, "]") )
    
        listNode = _getListNodeAtCurrent(currNode, listStartName, strSpec)
        if listNode == None:
            # TODO - insert mode
            raise ValueError("Navigating section \"%s\" specified: list"\
                " \"%s\" doesn't exist at this level of XML file."\
                % (strSpec, listName) )

        if listEndRem == "":
            # We are done, because there's only one list spec at current context
            # remaining in the string
            return listNode, listStartSep+listStartRem
        else:
            # Navigate into the list contents
            listItemNode = _getListItemFromStrSpec(listNode,
                '['+listContents+']')

            # Check the remaining contents appropriate
            if listEndRem[0] == '.':
                # Consume the . for a dictionary at next section
                listEndRem = listEndRem[1:]
            elif listEndRem[0] != '[':
                raise ValueError("Navigating section \"%s\" specified:"\
                    " List not followed by either a '%s' or '%s', error."\
                    % (strSpec, '[', '.'))

            #recurse again on the remainder, since there's stuff left to handle
            return navigateStrSpecHierarchy(listItemNode, listEndRem)
    elif structSep == '.':
        structName = structSepPrefix
        # There is no list separator, but a struct to recurse into.
        structNode = getStructNode(currNode, structName)
        if structNode == None:
            if insertMode:
                structNode = insertStructNode(currNode, structName)
            else:
                raise ValueError("Navigating section \"%s\" specified: struct"\
                    " \"%s\" doesn't exist at this level of XML file."\
                    % (strSpec, structName) )
        # Recursively process the rest of the specification
        return navigateStrSpecHierarchy(structNode, structRem)
    else:
        # We are at the correct hierarchy level - just return.
        return currNode, strSpec


def getItemFromStrSpec_CurrentCtx(currCtxNode, nodeSpecStr):
    """Gets the node at a current context.
    If context is a struct, treats nodeSpecStr as a named element.
    If context is a list, nodeSpecStr must be a list specifier."""
    currCtxNodeType = getElementType(currCtxNode)
    if currCtxNodeType == STG_STRUCT_TAG:
        eltNode = _getNamedElementNode(currCtxNode, nodeSpecStr)
    elif currCtxNodeType == STG_LIST_TAG:
        eltNode = _getListItemFromStrSpec(currCtxNode, nodeSpecStr)
    else:
        raise ValueError("Context node with tag %s is of incorrect type %s"\
            % (currCtxNode.tag, currCtxNodeType))
    return eltNode        

def _getListItemFromStrSpec(currListNode, listItemStr):
    """ Where listItemStr is in the form [4], or []"""
    if listItemStr[0] != '[':
        raise ValueError("\"%s\" not a well specified list item:"\
            " not opened correctly with '%s'."
            % (listItemStr, "[") )
    listContents, listEndSep, listEndRem = listItemStr[1:].partition(']')
    if listEndSep != ']':
        raise ValueError("\"%s\" not a well specified list item:"\
            " not closed correctly with '%s'."
            % (listItemStr, "]") )
    elif listEndRem != "":
        raise ValueError("Navigating section \"%s\" specified: badly"\
            " formed list found, trailing characters '%s' after list"\
            " closed." % (listItemStr, listEndRem))

    listIndex = _getListIndex(listContents)
    # TODO - modify later for insertion
    assert listIndex != None
    if not listIndex < len(currListNode):
        raise ValueError("Parsing listItemStr '%s', asked for list index %d,"\
            " but list has only %d items"\
            % (listItemStr, listIndex, len(currListNode)))
        
    # (Using the etree concise format here)
    listItemNode = currListNode[listIndex]
    return listItemNode

def _getListIndex(listIndexStr):
    if listIndexStr == "":
        listIndex = None
    else:        
        if not listIndexStr.isdigit():
            raise ValueError("list index '%s' isn't a set of digits"\
                % (listIndexStr))
        listIndex = int(listIndexStr)
    return listIndex

############################
# For getting stuff out of an existing XML doc

def getNodeFromStrSpec(parentNode, strSpec):
    """From a given specification of a node in a StGermain model file (eg
    plugins[0].Context), return the element to operate on."""

    resultNode, lastSpecStr = navigateStrSpecHierarchy(parentNode, strSpec)

    # We just need to return the element with the remaining spec string at the
    # current context
    # Remember it could be either a name (at a struct level), or an index (at a
    # list level).
    # It can also be of any any element type:-
    # thus if the calling function expects a param, list or
    # dict specifically, will need to check for that.
    elementNode = getItemFromStrSpec_CurrentCtx(resultNode, lastSpecStr)
    if elementNode == None:
        raise ValueError("Navigating str spec \"%s\": last element"\
            " \"%s\" doesn't exist at correct level of XML file."\
            % (strSpec, lastSpecStr) )
    return elementNode 

def getElementType(elementNode):
    """Checks the "type" of a StGermain data node element. 
    Here, we deal with 3 possibilities:
    The param, list, struct node tag format.
    The elmement tag format, where type is an attribute.
    The special elements import, plugins -> list, components -> dict."""
    
    # The _STG_NS_LXML prefixes included below since ETree prefixes these to
    # tag names to represent the namespace used when parsing in files.

    tag = elementNode.tag

    if tag in _stgElementBaseTags:
        return tag
    elif tag in map(addNsPrefix, _stgElementBaseTags):
        return removeNsPrefix(tag)
    elif tag == STG_ELEMENT_TAG or tag == addNsPrefix(STG_ELEMENT_TAG):
        try:
            typeAttr = elementNode.attrib['type']
        except KeyError:
            raise ValueError("Given node with tag '%s' doesn't specify"\
                " its type correctly." % (elementNode.tag))

        if typeAttr in _stgElementBaseTags:
            return typeAttr
        else:
            raise ValueError("Given node with tag '%s', type attr '%s' is"\
                " not a StGermainData element of known type."\
                % (elementNode.tag, typeAttr))
    elif tag in _stgSpecialParamTags \
            or tag in map(addNsPrefix, _stgSpecialParamTags):
        return STG_PARAM_TAG
    elif tag in _stgSpecialListTags \
            or tag in map(addNsPrefix, _stgSpecialListTags):
        return STG_LIST_TAG
    elif tag in _stgSpecialStructTags \
            or tag in map(addNsPrefix, _stgSpecialStructTags):
        return STG_STRUCT_TAG
    else:
        raise ValueError("Given node with tag '%s' is not a StGermainData"
            " element of known type." % (elementNode.tag))

def _getListNodeAtCurrent(currNode, listName, strSpec):
    """Get the list named at the current XML level. Note that if the list name
    is '', then assumes current level is a list"""
    if listName == "":
        # This case is allowed - suppose we are in a recursive loop, dealing
        # with a list entry within a list - then there would be no prefix,
        # so just check we're already within a list
        listNode = currNode
        if STG_LIST_TAG != getElementType(listNode):
            raise ValueError("Navigating section \"%s\" specified: implies"\
                    " current section is a list, but is actually a %s element."\
                    % (strSpec, getElementType(listNode)))
    else:
        listNode = getListNode(currNode, listName)
    return listNode

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
    eltNode = _getNamedElementNode_elTag(elNode, paramName, elType=STG_PARAM_TAG)
    if eltNode is not None: return eltNode
    for paramNode in elNode.iterchildren(tag=addNsPrefix('param')):
        if paramNode.attrib['name'] == paramName:
            return paramNode
    for specialTag in _stgSpecialParamTags: 
        if paramName == specialTag:
            resNodes = list(elNode.iterchildren(tag=addNsPrefix(specialTag)))
            if resNodes is not []: return resNodes[0]
    return None

def getStructNode(elNode, structName):
    """Returns the element node (in lxml form) of a particular struct element
    that's a child of the given elNode with given structName.
    If a node with the given name not found, returns none."""
    eltNode = _getNamedElementNode_elTag(elNode, structName, elType=STG_STRUCT_TAG)
    if eltNode is not None: return eltNode
    for structNode in elNode.iterchildren(tag=addNsPrefix('struct')):
        if structNode.attrib['name'] == structName:
            return structNode
    for specialTag in _stgSpecialStructTags: 
        if structName == specialTag:
            resNodes = list(elNode.iterchildren(tag=addNsPrefix(specialTag)))
            if resNodes is not []: return resNodes[0]
    return None

def getListNode(elNode, listName):
    """Returns the element node (in lxml form) of a particular list element
    that's a child of the given elNode with given listName.
    If a node with the given name not found, returns none."""
    eltNode = _getNamedElementNode_elTag(elNode, listName, elType=STG_LIST_TAG)
    if eltNode is not None: return eltNode
    for listNode in elNode.iterchildren(tag=addNsPrefix('list')):
        if listNode.attrib['name'] == listName:
            return listNode
    for specialTag in _stgSpecialListTags: 
        if listName == specialTag:
            resNodes = list(elNode.iterchildren(tag=addNsPrefix(specialTag)))
            if resNodes is not []: return resNodes[0]
    return None

def _getNamedElementNode(ctxNode, elName, elType=None):
    """Returns the element node (in lxml form) of a particular element
    that's a child of the given ctxNode with given elName.
    If a node with the given name not found, returns none.
    If elType is specified, will only return nodes of the given type.
    (Not designed to be used directly, but by getList etc.)
    Searches in both the element tag format (used by output files), and
    the param, list, struct format - and also for 'special' model elements such
    as plugins, imports and components."""
    eltNode = _getNamedElementNode_elTag(ctxNode, elName)
    if eltNode is not None: return eltNode
    # now check for the 'special' element tags
    for eltNode in ctxNode.iterchildren():
        # in this case, e.g. the list with asked for name 'import' will have
        # tag 'import'
        if eltNode.tag == addNsPrefix(elName):
            if eltNode.tag in map(addNsPrefix, _stgSpecialParamTags):
                return eltNode
            if eltNode.tag in map(addNsPrefix, _stgSpecialListTags):
                return eltNode
            elif eltNode.tag in map(addNsPrefix, _stgSpecialStructTags):
                return eltNode
    # now check the old param, list, struct format
    for eltNode in ctxNode.iterchildren():
        if eltNode.tag in map(addNsPrefix, _stgElementBaseTags):
            if elName == eltNode.attrib['name']:
                return eltNode
    return None        

def _getNamedElementNode_elTag(elNode, elName, elType=None):
    """Returns the element node (in lxml form) of a particular element
    that's a child of the given elNode with given elName.
    If a node with the given name not found, returns none.
    If elType is specified, will only return nodes of the given type.
    (Not designed to be used directly, but by getList etc.)
    Searches in the element tag format."""
    
    for eltNode in elNode.iterchildren(tag=addNsPrefix('element')):
        if eltNode.attrib['name'] == elName:
            if elType == None or eltNode.attrib['type'] == elType:
                return eltNode
    return None

#############################
# For manipulating/updating an existing XML doc, using the eTree package

def createNewStgDataDoc():
    """Create a new empty StGermain model XML file (can be merged with other
    model files)."""
    nsMap = {None: STG_NS}
    root = etree.Element(STG_ROOT_TAG, nsmap=nsMap)
    xmlDoc = etree.ElementTree(root)
    return xmlDoc, root

def setMergeType(xmlNode, mergeType):
    if mergeType is not None:
        if mergeType not in STG_MERGE_TYPES:
            raise ValueError("The mergeType provided, '%s', is not one of"\
                " the StGermain Model XML allowed merge types (%s)"\
                % (mergeType, STG_MERGE_TYPES))
        xmlNode.attrib[STG_MERGE_ATTRIB] = mergeType

# TODO: really needed??
def insertNamedElementNode(parentNode, elementName, createType):
    elementNode = etree.SubElement(parentNode, createType, name=elementName)
    setMergeType(paramEl, "replace")
    return elementNode

def writeParam(parentNode, paramName, paramVal, mt=None):
    paramEl = etree.SubElement(parentNode, STG_PARAM_TAG, name=paramName)
    setMergeType(paramEl, mt)
    paramEl.text = str(paramVal)
    return paramEl

def writeParamSet(parentNode, paramsDict, mt=None):
    # TODO - check parent node is a struct
    for paramName, paramVal in paramsDict.iteritems():
        writeParam(parentNode, paramName, paramVal, mt)

def writeParamList(parentNode, listName, paramVals, mt=None):
    '''Write a Stg XML List structure, made up purely of (unnamed) parameters'''
    listElt = etree.SubElement(parentNode, STG_LIST_TAG, name=listName) 
    setMergeType(listElt, mt)
    for paramVal in paramVals:
        etree.SubElement(listElt, STG_PARAM_TAG).text = str(paramVal) 
    return listElt    

def writeMergeComponent(rootNode, compName, compType):
    '''Write XML to merge a given component to the components list - and
     return new comp elt'''
    assert rootNode.tag == STG_ROOT_TAG
    compList = etree.SubElement(rootNode, STG_STRUCT_TAG, name="components",\
        mergeType="merge") 
    compElt = etree.SubElement(compList, STG_STRUCT_TAG, name=compName)
    writeParam(compElt, "Type", compType)
    return compElt

# Write out using StGermain command-line specification format
def writeValueUsingStrSpec(rootNode, strSpec, value):
    pass
    # if flattened XML:
    # check str spec exists in flattened XML first

    # Get value from analysis XML (thus avoid creation of new unnec)
    # Set the value
    # This will be smart enough to know the type of variable used, and set
    #  appropriately.
    #   

#def insertNodeAt
    # navigate hierarchy - replace mode
    # insert node name at remainder, of appropriate type
    #  if node is param, only allow: Bool, int, double
    #  if node is list, only allow Python lists
    #  if node is struct, only allow Python dicts
    #  Qtn: do we allow recursive of these?

############################################
# For actual file I/O
def writeStgDataDocToFile(xmlDoc, filename):
    """Write a given StGermain xmlDoc to the file given by filename"""
    outFile = open(filename, 'w')
    xmlDoc.write(outFile, pretty_print=True)
    outFile.close()


def createFlattenedXML(inputFiles, cmdLineOverrides=""):
    '''Flatten a list of provided XML files and optionally also
    cmdLineOverrides (string), using the StGermain FlattenXML tool'''
    flattenExe=uwa.getVerifyStgExePath('FlattenXML')

    try:
        p = Popen([flattenExe]+inputFiles+cmdLineOverrides.split(), stdout=PIPE, stderr=PIPE)
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
