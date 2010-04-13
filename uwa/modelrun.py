from lxml import etree
import uwa.modelresult
from uwa import stgxml

class ModelRun:
	'''A class to keep records about a StgDomain/Underworld Model Run, \
	including access to the underlying XML of the actual model'''
	def __init__(self, name, modelInputFiles, outputPath, logPath="./log", nproc=1):
		self.name = name
		self.modelInputFiles = modelInputFiles
		self.outputPath = outputPath
		self.logPath = logPath
		self.jobParams = JobParams( nproc ) 
		# TODO: should the below actually be compulsory?
		self.simParams = None
		self.fieldTests = FieldTestsInfo()
		self.cpFields = []
		self.analysisXML = None

class JobParams:
	def __init__( self, nproc ):
		self.nproc = int(nproc)

	def writeInfoXML( self, parentNode ):
		'''Writes information about this class into an existing, open XML doc node, in a child list'''
		jpNode = etree.SubElement( parentNode, 'jobParams' )
		etree.SubElement( jpNode, 'nproc' ).text = str(self.nproc)

class SimParams:
	'''A class to keep records about the simulation parameters used for a StgDomain/Underworld
	Model Run, such as number of timesteps to run for'''

	stgXMLMappings = { \
		'nsteps':"maxTimeSteps", \
		'stoptime':"stopTime", \
		'cpevery':"checkpointEvery", \
		'dumpevery':"dumpEvery" }

	types = { \
		'nsteps':int, \
		'stoptime':float, \
		'cpevery':int, \
		'dumpevery':int }

	def __init__( self, nsteps=None, stoptime=None, cpevery=1, dumpevery=1 ):
		self.nsteps = nsteps
		self.stoptime = stoptime
		self.cpevery = int(cpevery)
		self.dumpevery = int(dumpevery)

	def checkValidParams( self ):
		check = (self.nsteps is not None) or (self.stoptime is not None)
		return check

	def writeInfoXML( self, parentNode ):
		'''Writes information about this class into an existing, open XML doc node, in a child list'''
		spNode = etree.SubElement( parentNode, 'simParams' )
		for param in self.stgXMLMappings:
			assert( param in self.__dict__ )
			etree.SubElement( spNode, param ).text = str(self.__dict__[param])
	
	def writeStgDataXML( self, xmlNode ):
		'''Writes the parameters of this class as parameters in a StGermain XML file'''
		for param, stgParamName in self.stgXMLMappings.iteritems():
			assert( param in self.__dict__ )
			paramVal = self.__dict__[param]
			if paramVal is not None:
				stgxml.writeParam( xmlNode, stgParamName, paramVal, mt='replace' )

	def readFromStgXML( self, inputFilesList ):		
		ffile=stgxml.createFlattenedXML(inputFilesList)

		# Necessary, because the parser will prefix this to tag names
		xmlDoc = etree.parse( ffile )
		stgRoot = xmlDoc.getroot()
		stgNSText = stgxml.stgNSText

		for param, stgXMLName in self.stgXMLMappings.iteritems():
			# some of these may be none, but that should be ok, will check below
			self.__dict__[param] = stgxml.getParamValue( stgRoot, stgXMLName, self.types[param] )

		assert( self.checkValidParams() )
		os.remove(ffile)


class FieldTest:
	'''Class for maintaining info about a single field test'''
	def __init__( self, fieldName, tol=None ):
		self.name = fieldName
		self.tol = tol

	def writeInfoXML( self, parentNode ):
		return etree.SubElement( parentNode, 'field', name=self.name, tol=str(self.tol) )


class FieldTestsInfo:
	'''Class for maintaining and managing a list of field tests, including IO from StGermain XML files'''

	stgFieldTestComponentType = 'FieldTest'
	stgFieldTestComponentName = 'uwaFieldTester'
	stgFieldTestSpecName = 'pluginData'
	stgFieldTestListName = 'NumericFields'
	stgRefFieldListName = 'ReferenceFields'

	def __init__( self, fieldsList={} ):
		self.fields = fieldsList
		self.fromXML = False
		self.useReference = False
		self.referencePath = None
		self.testTimestep = 0

	def add( self, fieldTest ):
		self.fields[fieldTest.name] = fieldTest	

	def setAllTols( self, fieldTol ):
		for fieldTest in self.fields.values():
			fieldTest.tol = fieldTol

	def writeInfoXML( self, parentNode ):
		'''Writes information about this class into an existing, open XML doc node, in a child element'''

		if len(self.fields) == 0: return

		ftNode = etree.SubElement( parentNode, 'fieldTestsInfo' )
		ftNode.attrib['fromXML']=str(self.fromXML)
		ftNode.attrib['useReference']=str(self.useReference)
		ftNode.attrib['referencePath']=str(self.referencePath)
		ftNode.attrib['testTimestep']=str(self.testTimestep)
		fListNode = etree.SubElement( parentNode, 'fields' )
		for fTest in self.fields.values():
			fTest.writeInfoXML( fListNode )

	def writeStgDataXML( self, rootNode ):
		'''Writes the necessary StGermain XML to enable these specified fields to be tested'''

		assert( self.fromXML == False )

		# If there are no fields to test, don't bother writing any StGermain XML config
		if len(self.fields) == 0: return

		# Append the component to component list
		compElt = stgxml.mergeComponent( rootNode, self.stgFieldTestComponentName, \
			self.stgFieldTestComponentType )

		# Create the plugin data
		pluginDataElt = etree.SubElement( rootNode, stgxml.structTag, name=self.stgFieldTestSpecName, \
			mergeType="replace" )
		xmlFieldTestsList = self.fields.keys()
		# This is necessary due to unusual format of this list in the FieldTest plugin:
		# <FieldName> <# of analytic func> - both as straight params
		ii=0
		for index in range(1,len(self.fields)*2,2):
			xmlFieldTestsList.insert( index, str(ii) )
			ii+=1
		stgxml.writeParamList( pluginDataElt, self.stgFieldTestListName, xmlFieldTestsList )
		if self.useReference:
			stgxml.writeParamSet( pluginDataElt, {\
				'referenceSolutionFilePath':self.referencePath,\
				'useReferenceSolutionFromFile':self.useReference })
			stgxml.writeParamList( pluginDataElt, self.stgRefFieldListName, self.fields.keys() )

		stgxml.writeParamSet( pluginDataElt, {\
			'IntegrationSwarm':'gaussSwarm',\
			'ConstantMesh':'constantMesh',\
			'testTimestep':self.testTimestep,\
			'ElementMesh':'linearMesh',\
			'normaliseByAnalyticSolution':'True',\
			'context':'context',\
			'appendToAnalysisFile':'True'})
	
	def readFromStgXML( self, inputFilesList ):
		'''Read in the list of fields that have already been specified to be tested from a set of StGermain
		input files. Useful when e.g. working with an Analytic Solution plugin'''
		self.fromXML = True

		# create a flattened file
		ffile=stgxml.createFlattenedXML(inputFilesList)

		# Necessary, because the parser will prefix this this to tag names
		stgNSText = stgxml.stgNSText

		xmlDoc = etree.parse( ffile )
		stgRoot = xmlDoc.getroot()

		# Go and grab necessary info from XML file
		fieldTestDataEl = stgxml.getStruct( stgRoot, self.stgFieldTestSpecName )
		fieldTestListEl = stgxml.getList( fieldTestDataEl, self.stgFieldTestListName )

		fieldTestEls = fieldTestListEl.getchildren()
		# As per the current spec, the field names are followed by an index 
		# of analytic solution
		ii = 0
		while ii < len(fieldTestEls):
			fieldName = fieldTestEls[ii].text
			self.fields[fieldName] = FieldTest(fieldName)
			# Skip the index
			ii+=1
			ii+=1

		os.remove(ffile)


def writeModelRunXML( modelRun, outputPath="", filename="", update=False, prettyPrint=True ):
	assert isinstance( modelRun, ModelRun )
	if filename == "":
		filename = defaultModelRunFilename(modelRun.name)
	if outputPath == "":
		outputPath=modelRun.outputPath
	outputPath+=os.sep	

	# create XML document
	root = etree.Element( 'StgModelRun' )
	xmlDoc = etree.ElementTree( root )
	# Write key entries:
	# Model description (grab from XML file perhaps)
	name = etree.SubElement( root, 'name' )
	name.text = modelRun.name
	filesList = etree.SubElement( root, 'modelInputFiles' )
	for xmlFilename in modelRun.modelInputFiles:
		modFile = etree.SubElement( filesList, 'inputFile' )
		modFile.text = xmlFilename
	etree.SubElement( root, 'outputPath' ).text = modelRun.outputPath
	modelRun.jobParams.writeInfoXML( root )
	if not modelRun.simParams:
		simParams = SimParams(0)
		simParams.readFromStgXML(modelRun.modelInputFiles)
		simParams.writeInfoXML(root)
	else:	
		modelRun.simParams.writeInfoXML(root)

	modelRun.fieldTests.writeInfoXML(root)

	# TODO : write info on cpFields?

	# Write the file
	if not os.path.exists(outputPath):
		os.makedirs(outputPath)
	outFile = open( outputPath+filename, 'w' )
	xmlDoc.write( outFile, pretty_print=prettyPrint )
	outFile.close()
	return outputPath+filename

def defaultModelRunFilename(modelName):	
	return 'ModelRun-'+modelName+'.xml'

def analysisXMLGen( modelRun, filename="analysis.xml" ):
	# create XML document
	nsMap = { None: "http://www.vpac.org/StGermain/XML_IO_Handler/Jun2003" }
	root = etree.Element( stgxml.stgRootTag, nsmap=nsMap )
	xmlDoc = etree.ElementTree( root )
	# Write key entries:
	stgxml.writeParam(root, 'outputPath', modelRun.outputPath, mt='replace')
	if modelRun.simParams:
		modelRun.simParams.writeStgDataXML( root )
	if not modelRun.fieldTests.fromXML:
		modelRun.fieldTests.writeStgDataXML( root )
	# This is so we can checkpoint fields list: defined in FieldVariable.c
	if len(modelRun.cpFields):
		stgxml.writeParamList( root, 'FieldVariablesToCheckpoint', modelRun.cpFields, mt='replace' )

	# Write the file
	outFile = open( filename, 'w' )
	xmlDoc.write( outFile, pretty_print=True )
	outFile.close()
	return filename

##################

import sys
import os

# Assume user has updated their path correctly.
mpiCommand="mpirun"

# First some helper functions to help set up the run
# Should probably go into io sub-package
def stgCmdLineParam( paramName, val ):
	'''Format a given parameter and it's value correctly for passing to StGermain on the command
	line, to over-ride something in a model XML'''
	return "--%s=%s" % (paramName, str(val))

def strRes( resTuple ):
	'''Turn a given tuple of resolutions into a string, suitable for using as an output dir'''
	assert len(resTuple) in range(2,4)
	resStr = ""
	for res in resTuple[:-1]: resStr += str(res)+"x"
	resStr += str(resTuple[-1])
	return resStr

def generateResOpts( resTuple ):
	'''Given a tuple of desired resolutions for a model, convert this to options to pass to StG
	on the command line'''
	# ResParams should probably be part of a useful struct/dict stored in standard place.
	resParams=["elementResI","elementResJ","elementResK"]
	assert len(resTuple) in range(2,4)
	resOptsStr=""
	for ii in range(len(resTuple)):
		resOptsStr+=stgCmdLineParam(resParams[ii],resTuple[ii])+" "

	# This is to ensure, since we're overriding, if only 2D model is being run, it ignores any 3rd
	# dimension spec set in the original model file
	resOptsStr+=stgCmdLineParam("dim",len(resTuple))
	return resOptsStr


# TODO: some of this functionality could be handled via strategy pattern - JobRunner (the MPI stuff)
def runModel( modelRun, extraCmdLineOpts=None ):

	# Check runExe found in path

	# Pre-run checks for validity - e.g. at least one input file, nproc is sensible value
	if ( modelRun.simParams ):
		assert( modelRun.simParams.checkValidParams() )

	# Construct run line
	mpiPart = "%s -np %d " % (mpiCommand, modelRun.jobParams.nproc)
	runExe=uwa.getVerifyStgExePath("StGermain")
	stgPart = "%s " % (runExe)
	for inputFile in modelRun.modelInputFiles:	
		stgPart += inputFile+" "
	if modelRun.analysisXML:
		stgPart += modelRun.analysisXML+" "

	# TODO: How to best handle custom command line options
	# Perhaps these should be passed through, either by script or as part of model definition
	# Possibly a list would be better than a straight string, to help user avoid spacing stuff-ups
	if extraCmdLineOpts:
		stgPart += " "+extraCmdLineOpts

	runCommand = mpiPart + stgPart + " > logFile.txt"

	# Run the run command, sending stdout and stderr to defined log paths
	print runCommand
	# TODO: the mpirunner should check things like mpd are set up properly, in case of mpich2
	os.system( runCommand )

	# Check status of run (eg error status)

	# Construct a modelResult
	# Get necessary stuff from FrequentOutput.dat
	# TODO: this should be in a sub-module - is currently quite hacky
	freqFile = open( modelRun.outputPath + "/FrequentOutput.dat", 'r' )

	# Parse out the headings
	headerLine = freqFile.readline()
	cols = headerLine.split()

	# Obtain time and memory at time-stamp specified by problem.steps
	lines = freqFile.readlines()
	lastLine = lines[-1]
	cols = lastLine.split()
	tSteps = float( cols[0] )
	simTime = float( cols[1] )

	result = uwa.modelresult.ModelResult( modelRun.name, simTime )
	
	return result
