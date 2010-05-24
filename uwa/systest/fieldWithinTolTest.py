from lxml import etree

from uwa.systest.api import TestComponent, UWA_PASS, UWA_FAIL
import uwa.analysis.fields as fields

class FieldWithinTolTest(TestComponent):
    def __init__(self, fieldsToTest=None,
            defFieldTol=0.01,
            fieldTols=None,
            useReference=False,
            referencePath=None,
            testTimestep=0
            ):
        TestComponent.__init__(self, "fieldWithinTol")
        self.fieldsToTest = fieldsToTest
        self.defFieldTol = defFieldTol
        self.fieldTols = fieldTols
        self.fComps = fields.FieldComparisonList()
        self.fComps.useReference = useReference
        self.fComps.referencePath = referencePath
        self.fComps.testTimestep = testTimestep

    def attachOps(self, modelRun):
        if self.fieldsToTest == None:
            self.fComps.readFromStgXML(modelRun.modelInputFiles)
        else:
            for fieldName in self.fieldsToTest:
                self.fComps.add(fields.FieldComparisonOp(fieldName))
        modelRun.analysis['fieldComparisons'] = self.fComps

    def getTolForField(self, fieldName):
        if (self.fieldTols is not None) and fieldName in self.fieldTols:
            fieldTol = self.fieldTols[fieldName]
        else:
            fieldTol = self.defFieldTol
        return fieldTol

    def check(self, resultsSet):
        fieldResults = {}
        statusMsg = ""
        numRuns = len(resultsSet)
        for fComp in self.fComps.fields.itervalues():
            fieldTol = self.getTolForField(fComp.name)
            for runI, mResult in enumerate(resultsSet):
                fCompRes = fComp.getResult(mResult)
                fieldResults[fComp.name] = fCompRes.withinTol(fieldTol)    
        
                if not fieldResults[fComp.name]:
                    if numRuns > 1:
                        statusMsg += "For run %d out of %d: " % runI, numRuns
                    statusMsg += "Field comp '%s' error(s) of %s not within"\
                        " tol %g" % (fComp.name, fCompRes.dofErrors, fieldTol)
                    break

            if fieldResults[fComp.name]:
                statusMsg += "Field comp '%s' error within tol %g for all"\
                    " runs.\n" % (fComp.name, fieldTol)

        print statusMsg
        if False in fieldResults.values():
            result = False
            self.tcStatus = UWA_FAIL(statusMsg)
        else:
            result = True
            self.tcStatus = UWA_PASS(statusMsg)
        return result

    def writeXMLCustomSpec(self, specNode):
        etree.SubElement(specNode, 'fromXML', value=str(self.fComps.fromXML))
        etree.SubElement(specNode, 'testTimestep',
            value=str(self.fComps.testTimestep))
        etree.SubElement(specNode, 'useReference',
            value=str(self.fComps.useReference))
        if self.fComps.useReference:
            etree.SubElement(specNode, 'referencePath',
                value=self.fComps.referencePath)
        fListNode = etree.SubElement(specNode, 'fields')
        for fName in self.fComps.fields.keys():
            fNode = etree.SubElement(fListNode, 'field', name=fName,
                tol=str(self.getTolForField(fName)))

    def writeXMLCustomResult(self, resNode):
        #TODO
        pass
