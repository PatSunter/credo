##  Copyright (C), 2010, Monash University
##  Copyright (C), 2010, Victorian Partnership for Advanced Computing (VPAC)
##  
##  This file is part of the CREDO library.
##  Developed as part of the Simulation, Analysis, Modelling program of 
##  AuScope Limited, and funded by the Australian Federal Government's
##  National Collaborative Research Infrastructure Strategy (NCRIS) program.
##
##  This library is free software; you can redistribute it and/or
##  modify it under the terms of the GNU Lesser General Public
##  License as published by the Free Software Foundation; either
##  version 2.1 of the License, or (at your option) any later version.
##
##  This library is distributed in the hope that it will be useful,
##  but WITHOUT ANY WARRANTY; without even the implied warranty of
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
##  Lesser General Public License for more details.
##
##  You should have received a copy of the GNU Lesser General Public
##  License along with this library; if not, write to the Free Software
##  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
##  MA  02110-1301  USA

"""Core API of the :mod:`credo.systest` module.

This defines the two key classes of the model, :class:`.SysTest` and 
:class:`.TestComponent`, from which actual examples of System tests
or Test components need to inherit.
"""

import os
import inspect
from datetime import timedelta
from xml.etree import ElementTree as etree
import credo.modelrun as mrun
import credo.io.stgxml
import credo.io.stgpath

class SysTestResult:
    """Class to represent an CREDO system test result.

    .. attribute:: detailMsg

       detailed message of what happened during the test.

    .. attribute:: statusStr

       One-word status string summarising test result (eg 'Pass').
    
    .. attribute:: _absRecordFile

       The absolute path of where the system test was saved to.
    """   

    detailMsg = None
    statusStr = None
    _absRecordFile = None

    def __str__(self):
        return self.statusStr
    
    def printDetailMsg(self):
        if self.detailMsg:
            print self.detailMsg

    def setRecordFile(self, recordFile):
        """Save the record file: as an absolute path."""
        self._absRecordFile = os.path.abspath(recordFile)
    
    def getRecordFile(self):
        return self._absRecordFile


class CREDO_PASS(SysTestResult):
    '''Simple class to represent an CREDO pass'''
    statusStr = 'Pass'
    def __init__(self, passMsg):
        assert type(passMsg) == str
        self.detailMsg = passMsg

class CREDO_FAIL(SysTestResult):
    '''Simple class to represent an CREDO failure'''
    statusStr = 'Fail'
    def __init__(self, failMsg):
        assert type(failMsg) == str
        self.detailMsg = failMsg
        
class CREDO_ERROR(SysTestResult):
    '''Simple class to represent an CREDO error'''
    statusStr = 'Error'
    def __init__(self, errorMsg):
        assert type(errorMsg) == str
        self.detailMsg = errorMsg

def getStdTestNameBasic(testTypeStr, inputFiles):
    """Basic part of the test name. Useful for restart runs etc."""
    if type(inputFiles) != list:
        raise TypeError("Function requires the inputFiles argument to be "
            " a list of strings - not a %s." % type(inputFiles))

    testNameBasic, ext = os.path.splitext(os.path.basename(inputFiles[0]))
    testNameBasic += "-%s" % (testTypeStr[0].lower()+testTypeStr[1:])
    return testNameBasic

def getStdTestName(testTypeStr, inputFiles, nproc, paramOverrides,
        solverOpts, nameSuffix):
    """Utility function, to get a standard name for system tests given
    key parameters of the tests. If nameSuffix is given a string, it will
    be used as the suffix after processor number, instead of one based on
    any parameter over-rides used."""
    testName = getStdTestNameBasic(testTypeStr, inputFiles)
    testName += "-np%s" % nproc
    if nameSuffix is not None:
        testName += "-%s" % (nameSuffix)
    elif paramOverrides is not None:
        # Otherwise, if no specific suffix to use set, then create one
        #  based on paramOverrides, to avoid collisions where possible
        #  between custom runs and default ones.
        # TODO: move this stuff into a library for managing Stg Command
        # line dict format.
        paramOs = paramOverrides
        paramOsStr = ""
        paramKeys = paramOverrides.keys()
        paramKeys.sort()
        for paramName in paramKeys:
            paramVal = paramOverrides[paramName]
            paramNameLast = paramName.split('.')[-1]
            paramValCanon = str(paramVal).replace(".","_")
            paramOsStr += "-%s-%s" % (paramNameLast, paramValCanon)
        testName += paramOsStr 
    return testName


class SysTest:
    '''A class for managing SysTests in CREDO. This is an abstract base
    class: you must sub-class it to create actual system test types.

    The SysTest is designed to interact with the 
    :class:`~credo.systest.systestrunner.SysTestRunner` class, primarily by
    creating a :class:`~credo.modelsuite.ModelSuite` on demand to run a set
    of ModelRuns required to do the test. It will then do a check that
    the results pass an expected metric:- generally by applying one or more
    :class:`~credo.systest.api.TestComponent` classes.
    
    Constructor keywords not in member attribute list:
    
    * nameSuffix: if specified, this defines the suffix that
      will be added to the test's name, output path, 
      and log path (where the test's result and stderr/out will be saved
      respectively) - Overriding the default one based on params used.

    .. attribute:: testType

       records the "type" of the system test, as a string (e.g. "Analytic",
       or "SciBenchmark") - for printing purposes.
    
    .. attribute:: inputFiles

       StGermain XML files that define the Model to be tested.

    .. attribute:: testName

       The name of this test, generally auto-generated from other properties.
       
    .. attribute:: outputPathBase

       The "base" output path to store results of the test in. Results from
       individual Model Runs performed as part of running the test may also
       be stored in that directory, or in subdirectories of it.
    
    .. attribute:: testStatus

       Status of the test. Initially `None`, once the test has been run
       the :class:`.SysTestResult` generated will be saved here.

    .. attribute:: testComponents

       A list of any :class:`.TestComponent` classes used as part of 
       performing the test.
    
    .. attribute:: nproc

       Number of processors to be used for the test. See 
       :attr:`credo.modelrun.ModelRun.nproc`.

    .. attribute:: paramOverrides

       Any model parameter overrides to be passed to ModelRuns performed
       as part of running the test - see
       :attr:`credo.modelrun.ModelRun.paramOverrides`. Thus allow 
       customisation of the test properties.

    .. attribute:: solverOpts

       Solver options to be used for any models making up this test.
       See :attr:`credo.modelrun.ModelRun.solverOpts`

    .. attribute:: resIndicesToTest
    
       If this is set to other than None, then only these indices will
       be passed to TestComponents to check as part of the 
       :attr:`~.getStatus` function.
    
    .. attribute:: timeout

       if set to a positive integer, this will be used as a maximum time
       (in seconds) the test is allowed to run for - if it runs over this
       the result of the test will be set to an Error.
       If timeout is None, 0 or negative, no timeout will be applied.
    '''

    def __init__(self, inputFiles, outputPathBase,
            nproc, paramOverrides, solverOpts, testType, nameSuffix=None,
            timeout=None):
        self.testType = testType
        # Be forgiving of user passing a single string rather than a list,
        # and correct for this.
        if isinstance(inputFiles, str):
            inputFiles = [inputFiles]
        self.inputFiles = inputFiles
        self.testName = getStdTestName(testType+"Test", inputFiles,
            nproc, paramOverrides, solverOpts, nameSuffix)
        credo.io.stgpath.checkAllXMLInputFilesExist(self.inputFiles)
        self.outputPathBase = outputPathBase
        self.testStatus = None
        self.testComponents = {}
        self.nproc = nproc 
        self.paramOverrides = paramOverrides
        if self.paramOverrides == None:
            self.paramOverrides = {}
        self.solverOpts = solverOpts
        # TODO: a bit of a hack currently ... need to think about the best
        # way to handle relative paths for sysTests and ModelRuns
        # -- PatrickSunter, 20 Jul 2010
        self.runPath = None
        self.resIndicesToTest = None
        self.timeout = timeout

    def setup(self):
        '''For the setup phase of tests.
        Since not all tests need a setup phase, the default behaviour is to
        do nothing.'''
        pass

    def genSuite(self):
        """Virtual method: must return a :class:`credo.modelsuite.ModelSuite`
        containing all models that need to be run to perform the test."""
        raise NotImplementedError("Error, base class")

    def checkResultValid(self, resultsSet):
        """Check that the given result set is "valid", i.e. exists, has 
        the right number of model results, and model results have necessary
        analysis ops associated with them to allow aspects of test to
        evaluate properly."""

    def setResIndicesToTest(self, resultIndices):
        """Sets which result indices should be checked."""
        for ii in resultIndices:
            if type(ii) is not int:
                raise TypeError("All result Indices must be integers.")
            elif ii < 0:
                raise ValueError("All result Indices must be positive.")
        self.resIndicesToTest = resultIndices

    def getResultsSubset(self, resultsSet):
        if self.resIndicesToTest is None:
            subSet = resultsSet
        else:
            subSet = []
            for ii in self.resIndicesToTest:
                if ii >= len(resultsSet):
                    raise ValueError("Error, a result index to test is"\
                        " greater than the number of results in the suite.")
                subSet.append(resultsSet[ii])
        return subSet

    def getStatus(self, resultsSet):
        """After a suite of runs created by :meth:".genSuite"
        has been run, when this method is passed the results of the suite
        (as a list of :class:`credo.modelresult.ModelResult`), it must decide
        and return the status of the test (as a :class:`.SysTestResult`).

        It also needs to save this status to :meth:`.testStatus`.

        By default, this simply gets each :class:`~.TestComponent` registered
        for the system test do check its status, all must pass for a total
        pass.

        .. note:: if using this default method, then sub-classes need to
           have defined `failMsg` and `passMsg` attributes to use.
        """
        # If using this defaul
        if not (hasattr(self, 'passMsg') and hasattr(self, 'failMsg')):
            raise AttributeError("Please define 'passMsg' and 'failMsg'"\
                " attributes of your SysTest class to use the defualt"\
                " getStatus method.")

        # In case the test is designed to only operate on a sub-set of 
        #  the results, update here.
        resultsSet = self.getResultsSubset(resultsSet)
        self.checkResultValid(resultsSet)
        allPassed = True
        for tComp in self.testComponents.itervalues():
            result = tComp.check(resultsSet)
            if not result:
                allPassed = False
                testStatus = CREDO_FAIL(self.failMsg)
        if allPassed:
            testStatus = CREDO_PASS(self.passMsg)
        self.testStatus = testStatus
        return testStatus
    
    # TODO: here is where it could be useful to have a method to get all
    #  test components to do additional optional analysis, e.g. plotting
    #  of graphs.

    def setErrorStatus(self, errorMsg):
        """Utility function for if a model run fails as part of the test,
        this function can be called to automatically set the test status."""
        testStatus = CREDO_ERROR(errorMsg)
        self.testStatus = testStatus
        return testStatus

    def setTimeout(self, seconds=0, minutes=0, hours=0, days=0):
        """Sets the :attr:`~.timeout` parameter, used to determine how long
        the test is allowed to run for."""
        assert seconds >= 0 and minutes >=0 and days >= 0
        self.timeout = seconds + minutes*60 + hours*60*60 + days*60*60*24

    def defaultSysTestFilename(self):
        """Return the default system test XML record filename, based on
        properties of the systest (such as :attr:`.testName`)."""
        return 'SysTest-'+self.testName+'.xml'

    def _createDefaultModelRun(self, modelName, outputPath):
        """Create and return a :class:`credo.modelrun.ModelRun` with the
        default options as specified for this System Test.
        (Thus is a useful helper function for sub-classes, so they can
        use this and not keep up to date with changes in
        the ModelRun interface.)"""
        return mrun.ModelRun(modelName,
            self.inputFiles, outputPath,
            nproc=self.nproc, paramOverrides=self.paramOverrides,
            solverOpts=self.solverOpts)

    def writePreRunXML(self, outputPath="", filename="", prettyPrint=True):
        """Write the SysTest XML with as much information before the run as
        is possible. This includes general info about the test, and detailed
        specificiation of appropriate parameters and test components.
        
        :param outputPath: (opt) path the XML should be saved to.
        :param filename: (opt) filename within that path that should be used.
        :param prettyPrint: whether to indent the XML for better
          human-readability (pretty-printing).
        :returns: the name of the file written to.
        """
        baseNode = self._createXMLBaseNode()
        self._writeXMLDescription(baseNode)
        self._writeXMLSpecification(baseNode)
        self._writeXMLTestComponentPreRuns(baseNode)
        xmlDoc = etree.ElementTree(baseNode)
        outFileName = self._writeXMLDocToFile(xmlDoc, outputPath, filename)
        return outFileName
        
    def updateXMLWithResult(self, resultsSet, outputPath="", filename="", prettyPrint=True):
        """Given resultsSet, a set of model results (list of 
        :class:`~credo.modelresult.ModelResult`), updates a Sys Test XML with
        the results of the test.
        If the XML file has the standard name, as defined by
        :meth:`.defaultSysTestFilename`, then it should be found automatically.

        Other arguments and return value same as for 
        :meth:`.writePreRunXML`.
        """
        baseNode, xmlDoc = self._getXMLBaseNodeFromFile(outputPath, filename)
        baseNode.attrib['status'] = str(self.testStatus)
        self._writeXMLResult(baseNode)
        if resultsSet:
            # We only do the below if there are actual results to write - for
            # an error run there may not be.
            self._updateXMLTestComponentResults(baseNode, resultsSet)
        outFileName = self._writeXMLDocToFile(xmlDoc, outputPath, filename)
        return outFileName

    def _createXMLBaseNode(self):
        """Create the base XML node for a Sys Test XML, in xml.etree format,
        and return it."""
        baseNode = etree.Element('StgSysTest')
        baseNode.attrib['type'] = self.testType
        baseNode.attrib['name'] = self.testName
        return baseNode

    def _resolveXMLOutputPathFilename(self, outputPath="", filename=""):   
        if filename == "":
            filename = self.defaultSysTestFilename()
        if outputPath == "":
            outputPath=self.outputPathBase
        outputPath+=os.sep
        return outputPath, filename

    def _writeXMLDocToFile(self, xmlDoc, outputPath, filename, prettyPrint=True):
        """Write the information in xmlDoc (in xml.etree format) to the filename
        given by outputPath and filename."""
        outputPath, filename = self._resolveXMLOutputPathFilename(
            outputPath, filename)
        if not os.path.exists(outputPath):
            os.makedirs(outputPath)
        outFilePath = os.path.join(outputPath, filename)
        outFile = open(outFilePath, 'w')
        credo.io.stgxml.writeXMLDoc(xmlDoc, outFile, prettyPrint)
        outFile.close()
        return outFilePath

    def _getXMLBaseNodeFromFile(self, outputPath="", filename=""):
        """Open the XML file in outputPath and given by filename (if these
        are empty strings, defaults are used), and return the base node
        from this file (in xml.etree format)."""
        outputPath, filename = self._resolveXMLOutputPathFilename(
            outputPath, filename)
        outFile = open(os.path.join(outputPath, filename), 'r+')
        parser = etree.XMLParser()
        # Note: we haven't removed blank spaces from the output
        # (xml.etree doesn't have an automatic option for this),
        # but that shouldn't pose a problem as no whitespace should
        # interfere with meaningful element text.
        xmlDoc = etree.parse(outFile, parser)
        baseNode = xmlDoc.getroot()
        return baseNode, xmlDoc

    def _writeXMLDescription(self, baseNode):
        """Writes the description of a test into an XML sub-node."""
        descNode = etree.SubElement(baseNode, 'description')
        descNode.text = self.description

    def _writeXMLSpecification(self, baseNode):
        """Function to write the test specification to baseNode (xml.etree)."""
        specNode = etree.SubElement(baseNode, 'testSpecification')
        
        ipListNode = etree.SubElement(specNode, 'inputFiles')
        for xmlFilename in self.inputFiles:
            fileNode = etree.SubElement(ipListNode, 'inputFile')
            fileNode.text = xmlFilename
        etree.SubElement(specNode, 'outputPathBase').text = self.outputPathBase

        nProcNode = etree.SubElement(specNode, "nproc")
        nProcNode.text = str(self.nproc)

        etree.SubElement(specNode, "timeout").text = \
            str(timedelta(seconds=self.timeout))

        mrun.writeParamOverridesInfoXML(self.paramOverrides, specNode)
        mrun.writeSolverOptsInfoXML(self.solverOpts, specNode)
        try:
            self._writeXMLCustomSpec(specNode)
        except AttributeError, ae:
            raise NotImplementedError("Please implement a "\
                " _writeXMLCustomSpec()"\
                " method for your SysTest subclass: %s" % ae )
            raise ae
    
    def _writeXMLCustomSpec(self, specNode):
        """Function to write the custom specification for a particular test
        type. Virtual method, to be implemented by sub-classes."""
        raise NotImplementedError("Abstract base class.")

    def _writeXMLTestComponentPreRuns(self, baseNode):
        """Write necessary info for all test components used by this 
        system test before a run (eg their specification info."""
        tcListNode = etree.SubElement(baseNode, 'testComponents')
        for tcName, testComponent in self.testComponents.iteritems():
            testComponent.writePreRunXML(tcListNode, tcName)

    def _updateXMLTestComponentResults(self, baseNode, resultsSet):
        """Update the XML info about each test component after a run
        (ie result info.)"""
        tcListNode = baseNode.find('testComponents')
        tcCompsAndXMLs = zip(self.testComponents.iterkeys(),
            self.testComponents.itervalues(),
            tcListNode.getchildren())
        for tcName, testComponent, testCompXMLNode in tcCompsAndXMLs:
            assert tcName == testCompXMLNode.attrib['name']
            assert testComponent.tcType == testCompXMLNode.attrib['type']
            testComponent.updateXMLWithResult(testCompXMLNode, resultsSet)

    def _writeXMLResult(self, baseNode):
        """Write the status of a test to the XML doc."""
        resNode = etree.SubElement(baseNode, 'testResult')
        resNode.attrib['status'] = str(self.testStatus)
        statusMsgNode = etree.SubElement(resNode, 'statusMsg')
        statusMsgNode.text = self.testStatus.detailMsg


class SysTestSuite:
    """Class that aggregates  a set of :class:`~credo.systest.api.SysTest`.

    For examples of how to use, see the CREDO documentation, especially
    :ref:`credo-examples-run-systest-direct`.

    TODO: document projectName and suiteName and nproc

    .. attribute:: sysTests

       List of system tests that should be run and reported upon. Generally
       shouldn't be accessed directly, recommend using :meth:`.addStdTest`
       to add to this list, and other methods to run and report on it.
    
    .. attribute:: subSuites

       List of subSuites (defaults to none) associated with this suite.
       Associating sub-suites allows a nested hierarchy of system tests.
    """

    def __init__(self, projectName, suiteName, sysTests=None,
            subSuites=None, nproc=1):
        self.projectName = projectName
        self.suiteName = suiteName
        if sysTests == None:
            self.sysTests = []
        else:    
            if not isinstance(sysTests, list):
                raise TypeError("Error, if the sysTests keyword is"
                    " provided it must be a list of SysTest.")
            self.sysTests = sysTests
        if subSuites == None:
            self.subSuites = []
        else:    
            if not isinstance(subSuites, list):
                raise TypeError("Error, if the subSuites keyword is"
                    " provided it must be a list of SysTestSuites.")
            self.subSuites = subSuites
        self.nproc = nproc    
    
    def addStdTest(self, testClass, inputFiles, **testOpts):
        """Instantiate and add a "standard" system test type to the list
        of System tests to be run. (The "standard" refers to the user needing
        to have access to the module containing the system test type to be
        added, usually from a `from credo.systest import *` statement.

        :param testClass: Python class of the System test to be added. This
          needs to be a sub-class of :class:`~credo.systest.api.SysTest`.
        :param inputFiles: model input files to be passed through to the 
          System test when instantiated.
        :param `**testOpts`: any other keyword arguments the user wishes to
          passed through to the System test when it's instantiated.
          Can be used to customise a test."""

        if not inspect.isclass(testClass):
            raise TypeError("The testClass argument must be a type that's"\
                " a subclass of the CREDO SysTest type. Arg passed in, '%s',"\
                " of type '%s', is not a Python Class." \
                % (testClass, type(testClass)))
        if not issubclass(testClass, SysTest):
            raise TypeError("The testClass argument must be a type that's"\
                " a subclass of the CREDO SysTest type. Type passed in, '%s',"\
                " not a subclass of SysTest." \
                % (testClass))
        callingFile = inspect.stack()[1][1]
        callingPath = os.path.dirname(callingFile)
        # If just given a single input file as a string, convert
        #  to a list (containing that single file).
        if isinstance(inputFiles, str): inputFiles = [inputFiles]
        credo.io.stgpath.convertLocalXMLFilesToAbsPaths(inputFiles, callingPath)
        credo.io.stgpath.checkAllXMLInputFilesExist(inputFiles)
        if 'nproc' not in testOpts:
            testOpts['nproc']=self.nproc
        outputPath = self._getStdOutputPath(testClass, inputFiles, testOpts)
        newSysTest = testClass(inputFiles, outputPath, **testOpts)
        # TODO: line below needs updating, see SysTest constructor comment
        newSysTest.runPath = callingPath
        self.sysTests.append(newSysTest)

    def addSubSuite(self, subSuite):
        """Adds a single sub-suite to the list of sub-suites."""
        if not isinstance(subSuite, SysTestSuite):
            raise TypeError("subSuite must be an instance of type"\
                " SysTestSuite.")
        self.subSuites.append(subSuite)
    
    def addSubSuites(self, subSuites):
        """Adds a set of sub-suites to the list of sub-suites."""
        for subSuite in subSuites:
            self.addSubSuite(subSuite)
    
    def newSubSuite(self, *subSuiteRegArgs, **subSuiteKWArgs):
        """Shortcut to create a new sub-suite, add it to the existing suite,
        and return reference to the newly created sub-suite."""
        subSuite = SysTestSuite(*subSuiteRegArgs, **subSuiteKWArgs)
        self.addSubSuite(subSuite)
        return subSuite

    def setAllTimeouts(self, seconds=0, minutes=0, applyToSubSuites=True):
        """Utility function to set all the timeouts for all system tests
        associated with the suite to a certain value."""
        for sysTest in self.sysTests:
            sysTest.setTimeout(seconds, minutes)
        
        for subSuite in self.subSuites:
            subSuite.setAllTimeouts(seconds, minutes, applyToSubSuites)

    def _getStdOutputPath(self, testClass, inputFiles, testOpts):
        """Get the standard name for the test's output path. Attempts to
        avoid naming collisions where reasonable."""

        classStr = str(testClass).split('.')[-1]
        #TODO: resolve fact this already likely has "test" at end, unlike test
        # type string.

        # Grab any custom options we need
        nproc = testOpts['nproc']
        nameSuffix = testOpts['nameSuffix'] if 'nameSuffix' in testOpts\
            else None
        paramOverrides = testOpts['paramOverrides']\
            if 'paramOverrides' in testOpts else None
        solverOpts = testOpts['solverOpts'] if 'solverOpts' in testOpts\
            else None

        testName = getStdTestName(classStr, inputFiles, nproc, 
            paramOverrides, solverOpts, nameSuffix)
        outputPath = os.path.join('output', testName)
        return outputPath
        

class TestComponent:
    '''A class for TestComponents that make up an CREDO System test/benchmark.
    Generally they will form part a list contained by a 
    :class:`.SysTest`.

    This is an abstract base class, individual test components must subclass
    from this interface.
    
    .. attribute:: tcStatus
    
       Status of this test component. Initially None, will be updated after
       the test component is evaluated to a :class:`.SysTestResult`.
       
    .. attribute:: tcType
    
       Type of the test component, as a (single world descriptive) string.'''

    def __init__(self, tcType):
        self.tcStatus = None
        self.tcType = tcType

    def attachOps(self, modelRun):
        '''Provided a modelRun (:class:`credo.modelrun.ModelRun`)
        attaches any necessary analysis operations
        to that run in order to produce the results needed for the test.
        (see :attr:`credo.modelrun.ModelRun.analysis`).'''
        raise NotImplementedError("Abstract base class.")

    def check(self, resultsSet):
        '''A function to check a set of results - returns True if the Test
        passes, False if not. Also updates the :attr:`.tcStatus` attribute.'''
        raise NotImplementedError("Abstract base class.")

    def writePreRunXML(self, parentNode, name):
        '''Function to write out info about the test component to an XML file,
        as a sub-tree of parentNode.'''
        tcNode = self._createBaseXMLNode(parentNode, name)
        self._writeXMLSpecification(tcNode)
    
    def _createBaseXMLNode(self, parentNode, name):
        '''Utility function when writing out info, should be called by 
        sub-classes at start of writeInfoXML definitions to follow
        convention of naming of XML node.'''
        tcNode = etree.SubElement(parentNode, 'testComponent')
        tcNode.attrib['name'] = name
        tcNode.attrib['type'] = self.tcType
        return tcNode
    
    def _writeXMLSpecification(self, tcNode):
        specNode = etree.SubElement(tcNode, 'specification')
        #Not currently any specification for all testComponents ... though may
        # be a fromXML param in future for example.
        self._writeXMLCustomSpec(specNode)
    
    def _writeXMLCustomSpec(self, specNode):
        raise NotImplementedError("Abstract base class.")

    def updateXMLWithResult(self, tcNode, resultsSet):
        """Updates a given XML node with the result of the test component,
        based on resultsSet."""
        tcNode.attrib['status'] = str(self.tcStatus)
        self._writeXMLResult(tcNode, resultsSet)
    
    def _writeXMLResult(self, tcNode, resultsSet):
        resNode = etree.SubElement(tcNode, 'result')
        resNode.attrib['status'] = str(self.tcStatus)
        statusMsgNode = etree.SubElement(resNode, 'statusMsg')
        statusMsgNode.text = self.tcStatus.detailMsg
        self._writeXMLCustomResult(resNode, resultsSet)
    
    def _writeXMLCustomResult(self, resNode, resultsSet):
        raise NotImplementedError("Abstract base class.")
