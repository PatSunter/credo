from xml.etree import ElementTree as etree

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
        self.fieldResults = {}
        self.fieldErrors = {}

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
        self.fieldResults = {}
        self.fieldErrors = {}
        statusMsg = ""
        numRuns = len(resultsSet)
        overallResult = True
        for fComp in self.fComps.fields.itervalues():
            fieldTol = self.getTolForField(fComp.name)
            self.fieldResults[fComp.name] = []
            self.fieldErrors[fComp.name] = []
            for runI, mResult in enumerate(resultsSet):
                fCompRes = fComp.getResult(mResult)
                fieldResult = fCompRes.withinTol(fieldTol)
                self.fieldResults[fComp.name].append(fieldResult)
                self.fieldErrors[fComp.name].append(fCompRes.dofErrors)
                if not fieldResult:
                    if numRuns > 1:
                        statusMsg += "For run %d out of %d: " % (runI, numRuns)
                    statusMsg += "Field comp '%s' error(s) of %s not within"\
                        " tol %g of %s solution"\
                        % (fComp.name, fCompRes.dofErrors, fieldTol,
                        self.fComps.getCmpSrcString())
                    overallResult = False    

            if False not in self.fieldResults[fComp.name]:
                statusMsg += "Field comp '%s' error within tol %g of %s"\
                    " solution for all runs.\n"\
                    % (fComp.name, fieldTol, self.fComps.getCmpSrcString())

        print statusMsg
        if overallResult == False:
            self.tcStatus = UWA_FAIL(statusMsg)
        else:
            self.tcStatus = UWA_PASS(statusMsg)
        return overallResult

    def _writeXMLCustomSpec(self, specNode):
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

    def _writeXMLCustomResult(self, resNode, resultsSet):
        frNode = etree.SubElement(resNode, 'fieldResultDetails')
        for fName, fComp in self.fComps.fields.iteritems():
            fieldTol = self.getTolForField(fName)
            fieldNode = etree.SubElement(frNode, "field", name=fName)
            for runI, fieldRes in enumerate(self.fieldResults[fName]):
                runNode = etree.SubElement(fieldNode, "run")
                runNode.attrib['number'] = str(runI+1)
                runNode.attrib['allDofsWithinTol'] = str(fieldRes)
                #TODO run name? and overall result?
                desNode = etree.SubElement(runNode, "dofErrors")
                for dofI, dofError in enumerate(self.fieldErrors[fName][runI]):
                    deNode = etree.SubElement(desNode, "dofError")
                    deNode.attrib["num"] = str(dofI)
                    deNode.attrib["error"] = "%6e" % dofError
                    deNode.attrib["withinTol"] = str(dofError <= fieldTol) 
