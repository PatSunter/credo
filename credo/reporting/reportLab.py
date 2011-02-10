import os
import math
from reportlab.rl_config import defaultPageSize
from reportlab.lib.styles import getSampleStyleSheet
import reportlab.platypus as platypus
import reportLabUtils as rl
from reportlab.lib.units import inch
from reportlab.graphics import renderSVG
from reportlab.graphics import renderPDF
from reportlab.lib import colors
import PIL
import credo.modelsuite as msuite

PAGE_WIDTH=defaultPageSize[0]
PAGE_HEIGHT=defaultPageSize[1]
styles = getSampleStyleSheet()
HeaderStyle = styles["Heading1"]
H2Style = styles["Heading2"]
H3Style = styles["Heading3"]
H4Style = styles["Heading4"]
ParaStyle = styles["Normal"]
BodyText = styles["BodyText"]
PreStyle = styles["Code"] 

def getColorTextStr(tcStatus):
    if tcStatus.statusStr == 'Pass':
        color = 'green'
    else:
        color = 'red'
    return '<font color="%s">%s</font>' % (color, tcStatus)

def addTestCompElements(sciBTest):
    elements = []
    elements.append(rl.header("Single Run Test Components", sep=0.1,
        style=H2Style))
    for runI, srTCs in enumerate(sciBTest.testComps):
        elements.append(rl.header("Run %d" % runI, sep=0.1, style=H3Style))
        for srName, srTC in srTCs.iteritems():
            elements.extend(testCompElement(srName, srTC))
    return elements        

def testCompElement(tcName, srTC):
    elements = []
    resultStr = getColorTextStr(srTC.tcStatus)
    elements.append(rl.header("'%s' (%s): %s" % \
            (tcName, srTC.tcType, resultStr),
        sep=0.1, style=H4Style))
    elements.append(rl.header("%s" % (srTC.tcStatus.detailMsg),
        sep=0.1, style=ParaStyle))
    #result = platypus.KeepTogether(elements)
    result = elements
    return result

def modelVariantsTable(mSuite):
    elements = []
    elements.append(rl.header("Model Variants", sep=0.1,
        style=H3Style))
    data = [[] for runI in range(len(mSuite.runs)+1)]
    data[0].append("Run")
    for mVarName in mSuite.modelVariants.iterkeys():
        data[0].append(mVarName)
    valIter = msuite.getParamValuesIter(mSuite.modelVariants, mSuite.iterGen)
    for ii, values in enumerate(valIter):
        data[ii+1].append(ii)
        data[ii+1].extend(list(values))
    table = platypus.Table(data)    
    tStyle = platypus.TableStyle(
        [('BOX', (0,0), (-1,-1), 2, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
        ('TEXTCOLOR', (0,0), (-1,0), colors.blue)]
        )
    table.setStyle(tStyle)
    elements.append(table)
    result = elements
    return result

def modelImagesDisplay(mSuite, imgPerRow=1):
    imageInfos = mSuite.modelImagesToDisplay
    elements = []
    if mSuite.iterGen is not None:
        inIter = msuite.getVariantIndicesIter(mSuite.modelVariants,
            mSuite.iterGen)
        varNameDicts = msuite.getVariantNameDicts(mSuite.modelVariants, inIter)
    for runI, imagesPerRun in enumerate(imageInfos):
        elements.append(rl.header("Run %d: %s" % (runI, mSuite.runs[runI].name),
            sep=0.0, style=H3Style))
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
            imgText = platypus.Paragraph(hdrText, style=H4Style)
            imgFName = os.path.join(mSuite.runs[runI].outputPath,
                    'window.%.5d.png' % imgInfo[0])
            # Save a cropped thumbnail to save space
            img = PIL.Image.open(imgFName)
            initWidth, initHeight = img.size
            ratio = initHeight / float(initWidth)
            # Calc size for thumbnail
            tWidth = int(initWidth * (1/float(imgPerRow)))
            tHeight = int(math.floor(tWidth * ratio))
            img.thumbnail((tWidth, tHeight), PIL.Image.ANTIALIAS)
            img.save(imgFName + ".thumbnail", "PNG")
            imgEl = platypus.Image(imgFName + ".thumbnail")
            # Set display size on page
            newWidth = int(math.floor((PAGE_WIDTH*.9) / float(imgPerRow)))
            newHeight = int(math.floor(newWidth * ratio))
            imgEl.drawWidth = newWidth
            imgEl.drawHeight = newHeight
            data[rowI].append([imgText, imgEl])
            if (ii+1) % imgPerRow == 0: rowI += 1
            #elements.append(imgEl)
        table = platypus.Table(data)    
        elements.append(table)
    #result = [platypus.KeepTogether(elements)]
    result = elements
    return result

def makeSuiteReport(mSuite, outName, imgPerRow=3):
    #content
    title = "Suite Report"
    specDict = {
        "outputPathBase" : mSuite.outputPathBase}
    #Build doc layout
    elements = []
    elements.append(rl.header(title))
    elements.append(rl.header("Specification", sep=0.1, style=H2Style))
    elements.append(rl.table(specDict))
    if mSuite.iterGen is not None:
        elements.extend(modelVariantsTable(mSuite))
    # Display requested images
    elements.append(rl.header("Analysis Images", sep=0.1, style=H2Style))
    if mSuite.analysisImages is not None:    
        for imgFile in mSuite.analysisImages:
            elements.extend(rl.image(os.path.join(mSuite.outputPathBase,
                imgFile), width=400))
    if mSuite.modelImagesToDisplay is not None:
        elements.append(rl.header("Model Run Images", sep=0.1, style=H2Style))
        elements.extend(modelImagesDisplay(mSuite, imgPerRow=imgPerRow))
    rl.makePDF(elements, title, outName)
    print "Saved PDF report at %s." % outName

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
    elements.append(rl.header(title))
    elements.append(rl.header("Overall Result: %s" % resultStr, sep=0.1, 
        style=H2Style))
    elements.append(rl.header("Description", sep=0.1, style=H2Style))
    elements.append(rl.header(description, sep=0.1, style=ParaStyle))
    elements.append(rl.header("Specification", sep=0.1, style=H2Style))
    elements.append(rl.table(specDict))
    tcElements = addTestCompElements(sciBTest)
    elements.extend(tcElements)
    # Display requested images
    elements.append(rl.header("Analysis Images", sep=0.1, style=H2Style))
    if sciBTest.mSuite.analysisImages is not None:    
        for imgFile in sciBTest.mSuite.analysisImages:
            elements.extend(rl.image(os.path.join(sciBTest.outputPathBase,
                imgFile), width=400))
    if sciBTest.mSuite.modelImagesToDisplay is not None:
        elements.append(rl.header("Model Run Images", sep=0.1, style=H2Style))
        elements.extend(modelImagesDisplay(sciBTest.mSuite, imgPerRow=imgPerRow))
    rl.makePDF(elements, title, outName)
    print "Saved PDF report at %s." % outName
