import os

'''A Module for convenient access to StGermain FrequentOutput files'''

STG_DEF_FREQ_FILENAME='FrequentOutput.dat'
FREQ_HEADER_LINESTART='#'

class FreqOutput:
    '''A simple class to store information about a frequent output file,
    and make it accessible.'''
    def __init__(self, path, filename=STG_DEF_FREQ_FILENAME):
        self.path = path
        self.filename = filename
        fullFilename = path + os.sep + filename
        if not os.path.exists(fullFilename):
            raise ValueError("Error, the path and filename passed in, '%s' "
                " and '%s', does not point to a valid freq output file."
                % (path, filename))
        self.populated = False
        self.headers = None
        self.headerColMap = {}
        self.records = None
        self.tStepMap = {}
        self._finalTimeStep = None
        try:
            self.file = open(fullFilename, "r")
        except IOError:
            # TODO: create a new exception class for this?
            raise IOError("Freq output file '%s' unable to be opened."
                " Possibly the relevant ModelRun didn't have one enabled."
                % (fullFilename))

    def populateFromFile(self):
        self.getHeaders()
        self.getAllRecords()
        self.getTimestepMap()
        self.populated = True
    
    def getHeaders(self):
        if not self.populated:
            self.file.seek(0)
            firstLine = self.file.readline()
            assert(firstLine[0]) == FREQ_HEADER_LINESTART
            firstLine = firstLine[1:]
            headers = firstLine.split()
            self.headers = headers
            for hI, header in enumerate(headers):
                self.headerColMap[header] = hI    
        return self.headers

    def getTimestepMap(self):
        if not self.populated:
            self.file.seek(0)
            # First line should be headers, skip
            firstLine = self.file.readline()
            assert(firstLine[0]) == FREQ_HEADER_LINESTART
            for lineNum, line in enumerate(self.file):
                tstep = int(line.split()[0])
                self.tStepMap[tstep] = lineNum
        return self.tStepMap    

    def getAllRecords(self):
        if not self.populated:
            self.file.seek(0)
            self.headers = self.getHeaders()
            self.records = []
            for line in self.file:
                recordValues = line.split()
                # We are assuming all freq output values are floats.
                # Might be better
                # to actually record the data type in the headers somehow?
                recordValueFloats = [float(val) for val in recordValues]
                self.records.append(recordValueFloats)
        # TODO: should we record the max timesteps here, and final of other
        # things?
        self._finalTimeStep = (self.records[-1])[self.headerColMap['Timestep']]
        return self.records    

    def getRecordDictAtStep(self, tstep):
        if not self.populated: self.populateFromFile()
        record = self.getRecordAtStep(tstep)
        recordDict = {}
        for header, col in self.headerColMap.iteritems():
            recordDict[header] = record[col]
        return recordDict    
    
    def finalStep(self):
        if not self.populated: self.populateFromFile()
        return self._finalTimeStep

    def getValueAtStep(self, tstep, headerName):
        if not self.populated:
            # We will take the approach that you should always populate the 
            # info for fast access. If memory were really a concern, could use
            # algorithms and/or read file line-by-line until (if) correct 
            # timestep's data found.
            self.populateFromFile()
        colNum = self.getColNum(headerName)
        record = self.getRecordAtStep(tstep)
        value = record[colNum]
        return value

    def getRecordNum(self, tstep):
        assert(self.populated)
        try:
            recordNum = self.tStepMap[tstep]
        except KeyError:
            tSteps = self.tStepMap.keys()
            raise ValueError("Error, timestep at which to get value, %d,"
                " doesn't exist in this Frequent output file (valid range is"
                " (%d-%d)." % (tstep, min(tSteps), max(tSteps)))
        return recordNum        

    def getRecordAtStep(self, tstep):
        assert self.records
        recordNum = self.getRecordNum(tstep)
        record = self.records[recordNum]
        return record

    def getColNum(self, headerName):
        try:
            colNum = self.headerColMap[headerName]
        except KeyError:
            raise ValueError("Error, header to get value of, '%s', doesn't"
                " exist in this Frequent output file. Valid headers are"
                " %s" % (headerName, self.headerColMap.keys()))
        return colNum        

