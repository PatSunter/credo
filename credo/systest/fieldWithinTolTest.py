from xml.etree import ElementTree as etree

from credo.systest.api import TestComponent, CREDO_PASS, CREDO_FAIL
import credo.analysis.fields as fields

class FieldWithinTolTest(TestComponent):
    """Checks whether, for a particular set of fields, the error
    between each field and an (analytic or reference) solution
    is below a specificed tolerance.

    This relies largely on functionality of:

    * :mod:`credo.analysis.fields` to specify the comparison operations
    * :mod:`credo.io.stgcvg` to analyse the "convergence" files containing
      comparison information produced by these operations.

    Other than those that are directly saved as attributes documented below,
    the constructor arguments of interest are:

    * useReference: determines whether the fields are compared against
      a reference, or analytic solution. See 
      :meth:`credo.analysis.fields.FieldComparisonList.useReference`
    * referencePath: See   
      :meth:`credo.analysis.fields.FieldComparisonList.referencePath`
    * referencePath: See   
      :meth:`credo.analysis.fields.FieldComparisonList.testTimestep`

    .. attribute:: fieldsToTest 

       A list of strings containing the names of fields that should be tested-
       i.e. those that will be compared with an expected solution. If left
       as `None` in constructor, this means the fieldsToTest list will be 
       expected to be defined in the StGermain model XML files themselves.
    
    .. attribute:: defFieldTol

       The default allowed tolerance for global normalised error when comparing
       Fields with their expected values.

    .. attribute:: fieldTols

       A dictionary, mapping particular field names to particular tolerances
       to use, overriding the default. E.g. {"VelocityField":1e-4} means
       the tolerance used for the VelocityField will be 1e-4.

    .. attribute:: fComps

        A :class:`credo.analysis.fields.FieldComparisonList` used as an
        operator to attach to ModelRuns to be tested, and do the actual
        comparison between fields.

    .. attribute:: fieldResults

       Initially {}, after the test is completed will store a dictionary
       mapping each field name to a Bool saying whether or not it was within
       the required tolerance.

    .. attribute:: fieldErrors

       Initially {}, after the test is completed will store a dictionary
       mapping each field name to a float representing the global normalised
       error in the comparison.
    """  

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
        """Implements base class
        :meth:`credo.systest.api.TestComponent.attachOps`."""
        if self.fieldsToTest == None:
            self.fComps.readFromStgXML(modelRun.modelInputFiles)
        else:
            for fieldName in self.fieldsToTest:
                self.fComps.add(fields.FieldComparisonOp(fieldName))
        modelRun.analysisOps['fieldComparisons'] = self.fComps

    def getTolForField(self, fieldName):
        """Utility func: given fieldName, returns the tolerance to use for
        testing that field (may be given by :attr:`.defFieldTol`, or
        been over-ridden in :attr:`.fieldTols`)."""
        if (self.fieldTols is not None) and fieldName in self.fieldTols:
            fieldTol = self.fieldTols[fieldName]
        else:
            fieldTol = self.defFieldTol
        return fieldTol

    def check(self, resultsSet):
        """Implements base class
        :meth:`credo.systest.api.TestComponent.check`."""
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
                        " tol %g of %s solution\n"\
                        % (fComp.name, fCompRes.dofErrors, fieldTol,
                        self.fComps.getCmpSrcString())
                    overallResult = False    

            if False not in self.fieldResults[fComp.name]:
                statusMsg += "Field comp '%s' error within tol %g of %s"\
                    " solution for all runs.\n"\
                    % (fComp.name, fieldTol, self.fComps.getCmpSrcString())

        print statusMsg
        if overallResult == False:
            self.tcStatus = CREDO_FAIL(statusMsg)
        else:
            self.tcStatus = CREDO_PASS(statusMsg)
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
