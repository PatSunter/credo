import os, math
import PIL
import rstUtils as rstu
import credo.modelsuite as msuite

def getColorTextStr(tcStatus):
    #TODO: do I need to ensure there is a 'red' role at beginning now?
    if tcStatus.statusStr == 'Pass':
        color = 'green'
    else:
        color = 'red'
    return ':%s:`%s`' % (color, tcStatus)

def addTestCompElements(sciBTest):
    level = 3
    elements = []
    elements.append(rstu.getHeaderStr("Single Run Test Components", level))
    for runI, srTCs in enumerate(sciBTest.testComps):
        elements.append(rstu.getHeaderStr("Run %d" % runI, level+1))
        for srName, srTC in srTCs.iteritems():
            elements.extend(testCompElement(srName, srTC))
    return elements

def testCompElement(tcName, srTC):
    level = 5
    elements = []
    resultStr = getColorTextStr(srTC.tcStatus)
    elements.append(rstu.getHeaderStr("'%s' (%s): %s" % \
            (tcName, srTC.tcType, resultStr), level))
    elements.append(rstu.getParaStr(srTC.tcStatus.detailMsg))
    result = elements
    return result    

def modelVariantsTable(mSuite):
    #TODO
    return []
    
def modelImagesDisplay(mSuite, imgPerRow=1):
    level = 3
    imageInfos = mSuite.modelImagesToDisplay
    elements = []
    if mSuite.iterGen is not None:
        inIter = msuite.getVariantIndicesIter(mSuite.modelVariants,
            mSuite.iterGen)
        varNameDicts = msuite.getVariantNameDicts(mSuite.modelVariants, inIter)
    for runI, imagesPerRun in enumerate(imageInfos):
        mRun = mSuite.runs[runI]
        elements.append(rstu.getHeaderStr("Run %d: %s" % (runI,
            mSuite.runs[runI].name), level))
        #if mSuite.iterGen is not None:
        #    elements.append(rl.header("%s" % varNameDicts[runI],
        #        style=ParaStyle))
        # Put the images in a table
        nRows = int(math.ceil(len(imagesPerRun)/float(imgPerRow)))
        data = [[] for rowI in range(nRows)]
        rowI = 0
        for ii, imgInfo in enumerate(imagesPerRun):
            hdrText = "Timestep %d:" % (imgInfo[0])
            if imgInfo[1] != "": hdrText += " (%s)" % imgInfo[1]
            imgText = "**%s**\n" % hdrText
            imgFName = os.path.join(os.path.relpath(mRun.outputPath,
                mSuite.outputPathBase), 'window.%.5d.png' % imgInfo[0])
            imgFName = os.path.join(mRun.outputPath, 
                'window.%.5d.png' % imgInfo[0])
            relFName = os.path.relpath(imgFName, mSuite.outputPathBase)
            img = PIL.Image.open(imgFName)
            initWidth, initHeight = img.size
            ratio = initHeight / float(initWidth)
            # Set display size on page
            newWidth = int(math.floor((rstu.PAGE_WIDTH*.9) / float(imgPerRow)))
            newHeight = int(math.floor(newWidth * ratio))
            imgEl = rstu.regImage(relFName, width=newWidth, height=newHeight)
            data[rowI].append([imgText, imgEl])
            if (ii+1) % imgPerRow == 0: rowI += 1
        table = rstu.listTable(data)    
        elements.append(table)
    result = elements
    return result

def makeSciBenchReport(sciBTest, outName, imgPerRow=3):
    #content
    title = "%s Report" % sciBTest.testName
    description = sciBTest.description
    resultStr = getColorTextStr(sciBTest.testStatus)
    specDict = {
        "basePath" : sciBTest.basePath,
        "outputPathBase" : sciBTest.outputPathBase,
        "nproc" : sciBTest.nproc }

    #Build doc layout
    elements = []
    level = 1
    elements.append(rstu.getHeaderStr(title, level))
    level += 1
    elements.append(rstu.getHeaderStr("Overall Result: %s" % resultStr, level))
    level += 1
    elements.append(rstu.getHeaderStr("Description", level))
    elements.append(rstu.getParaStr(description))
    elements.append(rstu.getHeaderStr("Specification", level))
    elements.append(rstu.getRegList(specDict))
    tcElements = addTestCompElements(sciBTest)
    elements.extend(tcElements)
    # Display requested images
    elements.append(rstu.getHeaderStr("Analysis Images", level))
    if sciBTest.mSuite.analysisImages is not None:    
        for imgFile in sciBTest.mSuite.analysisImages:
            elements.extend(rstu.regImage(imgFile, scale=80))
    if sciBTest.mSuite.modelImagesToDisplay is not None:
        elements.append(rstu.getHeaderStr("Model Run Images", 3))
        elements.extend(modelImagesDisplay(sciBTest.mSuite,
            imgPerRow=imgPerRow))
    rstu.makeRST(elements, title, outName)
    print "Saved RST report at %s." % outName

