from lxml import etree

from uwa.systest.api import TestComponent
import uwa.analysis.fields as fields

class FieldWithinTolTest(TestComponent):
    def __init__(self, fieldsToTest=None,
            defFieldTol=0.01,
            fieldTols=None,
            useReference=False,
            referencePath=None,
            testTimestep=0
            ):
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
        for fComp in self.fComps.fields.itervalues():
            fieldTol = self.getTolForField(fComp.name)
            for runI, mResult in enumerate(resultsSet):
                fCompRes = fComp.getResult(mResult)
                fieldResults[fComp.name] = fCompRes.withinTol(fieldTol)    
        
                if not fieldResults[fComp.name]:
                    if len(resultsSet) > 0:
                        print "For run %d out of %d" % runI, len(resultsSet)
                    print "Field comp '%s' error(s) of %s not within tol %f"\
                        % (fComp.name, fCompRes.dofErrors, fieldTol)
                    break

            if fieldResults[fComp.name]:
                print "Field comp '%s' error within tol %f for all runs."\
                    % (fComp.name, fieldTol)

        if False in fieldResults: result = False
        else: result = True
        return result

    def writeInfoXML(self, parentNode):
        ftNode = self.createBaseXMLNode(parentNode, 'fieldWithinTol')
        ftNode.attrib['fromXML']=str(self.fComps.fromXML)
        fListNode = etree.SubElement(ftNode, 'fields')
        for fName in self.fComps.fields.keys():
            fNode = etree.SubElement(fListNode, 'field', name=fName)
