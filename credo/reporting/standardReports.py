import os, math
# TODO: work out if the PIL really needed here.
import PIL
import credo.modelsuite as msuite

def getColorStatusStr(tcStatus, rGen):
    if tcStatus.statusStr == 'Pass':
        color = 'green'
    else:
        color = 'red'
    colorStr = rGen.getColorTextStr(tcStatus, color)
    ':%s:`%s`' % (color, tcStatus)
    return colorStr

def addTestCompElements(sciBTest, rGen, level):
    elements = []
    elements.append(rGen.getHeaderEl("Single Run Test Components", level))
    for runI, srTCs in enumerate(sciBTest.testComps):
        elements.append(rGen.getHeaderEl("Run %d" % runI, level+1))
        for srName, srTC in srTCs.iteritems():
            elements.extend(testCompElement(srName, srTC, level+2, rGen))
    return elements

def testCompElement(tcName, srTC, level, rGen):
    elements = []
    resultStr = getColorStatusStr(srTC.tcStatus, rGen)
    elements.append(rGen.getHeaderEl("'%s' (%s): %s" % \
            (tcName, srTC.tcType, resultStr), level))
    elements.append(rGen.getParaEl(srTC.tcStatus.detailMsg, level))
    result = elements
    return result

def modelVariantsTable(mSuite):
    #TODO
    return []
    
def modelImagesDisplay(mSuite, rGen, level, imgPerRow=1):
    imageInfos = mSuite.modelImagesToDisplay
    elements = []
    if mSuite.iterGen is not None:
        inIter = msuite.getVariantIndicesIter(mSuite.modelVariants,
            mSuite.iterGen)
        varNameDicts = msuite.getVariantNameDicts(mSuite.modelVariants, inIter)
    for runI, imagesPerRun in enumerate(imageInfos):
        mRun = mSuite.runs[runI]
        elements.append(rGen.getHeaderEl("Run %d: %s" % (runI,
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
            imgFName = os.path.join(mRun.outputPath,
                'window.%.5d.png' % imgInfo[0])
            # Set possible thumbnail size - can reduce file size if many
            #  images are being used.
            tScale = 1/float(imgPerRow) * 100
            # Set display size on page
            img = PIL.Image.open(imgFName)
            initWidth, initHeight = img.size
            ratio = initHeight / float(initWidth)
            newWidth = int(math.floor((rGen.PAGE_WIDTH*.9) / float(imgPerRow)))
            newHeight = int(math.floor(newWidth * ratio))
            data[rowI].append(rGen.getImageEls(imgFName, width=newWidth,
                height=newHeight, tScale=tScale, hdrText=hdrText))
            if (ii+1) % imgPerRow == 0: rowI += 1
        table = rGen.getTableEl(data)
        elements.append(table)
    result = elements
    return result

def makeSciBenchReport(sciBTest, rGen, outName, imgPerRow=3):
    """Make a science benchmark report.
    :param sciBTest: a science benchmark test to create report of.
    :param rGen: a report generator instatiation.
    :param outName: name of file to save generated report as.
    :param imgPerRow: how many images to use per row."""
    #content
    title = "%s Report" % sciBTest.testName
    description = sciBTest.description
    resultStr = getColorStatusStr(sciBTest.testStatus, rGen)
    specDict = {
        "basePath" : sciBTest.basePath,
        "outputPathBase" : sciBTest.outputPathBase,
        "nproc" : sciBTest.nproc }

    #Build doc layout
    elements = []
    level = 1
    elements.append(rGen.getHeaderEl(title, level))
    level += 1
    elements.append(rGen.getHeaderEl("Overall Result: %s" % resultStr, level))
    elements.append(rGen.getHeaderEl("Description", level))
    elements.append(rGen.getParaEl(description, level))
    elements.append(rGen.getHeaderEl("Specification", level))
    elements.extend(rGen.getDefListEls(specDict))
    tcElements = addTestCompElements(sciBTest, rGen, level)
    elements.extend(tcElements)
    # Display requested images
    elements.append(rGen.getHeaderEl("Analysis Images", level))
    if sciBTest.mSuite.analysisImages is not None:    
        for imgFile in sciBTest.mSuite.analysisImages:
            elements.extend(rGen.getImageEls(os.path.join(
                sciBTest.outputPathBase, imgFile), width=rGen.PAGE_WIDTH * .8))
    if sciBTest.mSuite.modelImagesToDisplay is not None:
        elements.append(rGen.getHeaderEl("Model Run Images", level))
        elements.extend(modelImagesDisplay(sciBTest.mSuite, rGen, level+1,
            imgPerRow=imgPerRow))
    rGen.makeDoc(elements, title, outName)
    print "Saved report at %s (%s type)." % (outName, rGen.rType)
