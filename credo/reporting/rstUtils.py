"""Utils/primitives useful in constructing an RST report doc."""
import textwrap

#Multiple header lines
# in Sphinx: ['#', '*', '=', '-', '^', '"']
rstHeaderChars = ['*', '=', '-', '^', '"', '+']

#Arbitrary preferred width of page view
PAGE_WIDTH = 800

rolesList = ['green', 'red']

def getRolesStr():
    #Currently just for custom colours.
    rolesStr = ""
    for role in rolesList:
        rolesStr += ".. role:: %s\n\n" % role
    return rolesStr

def dedentAll(s):
    sList = [line.lstrip() for line in s.split('\n')]
    return '\n'.join(sList)

def reIndent(s, numSpaces, keepInitSpaces = True):
    """Re-Indent a string with given number of numSpaces preceding each line.
    if keepInitSpaces is true, whitespace at start of initial lines is kept
    in output and added to numSpaces."""
    s2 = s.split('\n')
    sList = []
    for line in s2:
        if line == '':
            sList.append('')
        else:
            if not keepInitSpaces:
                line = line.lstrip()
            sList.append(' ' * numSpaces + line)
    s3 = '\n'.join(sList)
    return s3

def getHeaderStr(headerText, level):
    """Get a string suitable for an RST header."""
    uLine = rstHeaderChars[level-1] * len(headerText)
    headerStr = "%s\n%s\n\n" % (headerText, uLine)
    return headerStr

def getParaStr(paraText):
    paraStr = dedentAll(paraText)
    paraStr = textwrap.fill(paraStr, 75)
    return paraStr + "\n\n"

def getRegList(specDict):
    resStr = ""
    for key, val in specDict.iteritems():
        resStr += " * %s: %s\n" % (key, val)
    resStr += "\n"
    return resStr

def regImage(imgFile, scale=None, width=None, height=None):
    resStr = ".. image:: %s\n" % imgFile
    if scale is not None:
        resStr += "   :scale: %d %%\n" % scale
    if width is not None:
        resStr += "   :width: %d px\n" % width
    if height is not None:
        resStr += "   :height: %d px\n" % height
    resStr += "\n"
    return resStr

def listTable(tableData):
    resultStr = ".. list-table::\n\n"
    for dataLine in tableData:
        for elI, dataEl in enumerate(dataLine):
            if elI == 0:
                prefix1stStr = ' ' * 3 + '* - '
            else:
                prefix1stStr = ' ' * 3 + '  - '
            elementStr = "\n".join(dataEl)
            elementStr = reIndent(elementStr, len(prefix1stStr))
            #Now correct for special precursors
            elementStr = prefix1stStr + elementStr[len(prefix1stStr):]    
            resultStr += elementStr
    return resultStr

def makeRST(elements, title, outName):
    outDoc = open(outName, "w")
    rolesStr = getRolesStr()
    outDoc.write(rolesStr)
    for lineStr in elements:
        outDoc.write(lineStr)
    outDoc.close()
