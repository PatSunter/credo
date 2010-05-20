import os
import operator

'''A Module for convenient access to StGermain FrequentOutput files'''

STG_DEF_FREQ_FILENAME='FrequentOutput.dat'
FREQ_HEADER_LINESTART='#'

class FreqOutput:
    '''A simple class to store information about a frequent output file,
    and make it accessible.'''
    def __init__(self, path, filename=STG_DEF_FREQ_FILENAME):
        self.path = path
        self.filename = filename
        fullFilename = os.path.join(path, filename)
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
            # need to do this rather than just enumerate because
            # of possible duplicate header lines
            recordNum = 0
            for lineNum, line in enumerate(self.file):
                # See comment above in getAllRecords
                if line[0] == FREQ_HEADER_LINESTART:
                    continue
                tstep = int(line.split()[0])
                self.tStepMap[tstep] = recordNum
                recordNum+=1
        return self.tStepMap    

    def getAllRecords(self):
        if not self.populated:
            self.file.seek(0)
            self.headers = self.getHeaders()
            tStepCol = self.headerColMap['Timestep']
            self.records = []
            for line in self.file:
                if line[0] == FREQ_HEADER_LINESTART:
                    # Currently, on restart runs it will re-add a header to
                    # Freq out, so ignore this
                    continue
                recordValues = line.split()
                # We are assuming all freq output values are floats.
                # Might be better
                # to actually record the data type in the headers somehow?
                recordValueNums = [float(val) for val in recordValues]
                # For now, manually convert tstep specially to int.
                recordValueNums[0] = int(recordValueNums[tStepCol])
                self.records.append(recordValueNums)
        self._finalTimeStep = (self.records[-1])[tStepCol]
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

    def getValuesArray(self, headerName, range="all"):
        if not self.populated: self.populateFromFile()
        # TODO: Check range input is ok. I need to find out the right way to
        # handling unusual values for these 
        recordsSet = self.records
        colNum = self.getColNum(headerName)
        valArray = []
        for record in recordsSet:
            valArray.append(record[colNum])
        return valArray    

    def getTimeStepsArray(self, range="all"):    
        if not self.populated: self.populateFromFile()
        # TODO: Check range input is ok. I need to find out the right way to
        # handling unusual values for these 
        colNum = self.getColNum('Timestep')
        tSteps = [record[colNum] for record in self.records]
        return tSteps

    def getMin(self, headerName):
        '''get the Minimum of the records for a given header, including
        the timestep at which that minimum occured.'''
        return self.getReductionOp(headerName, min)
        
    def getMax(self, headerName):
        '''get the Maximum of the records for a given header, including
        the timestep at which that minimum occured.'''
        return self.getReductionOp(headerName, max)

    def getMean(self, headerName):
        '''gets the Mean of the records for a given header.
        
        Note: this is provided for convenience. If user wants to do more complex
        statistical operations, use the getValuesArray, then process this
        directly using stats functions/libraries.'''
        if not self.populated: self.populateFromFile()
        valArray = self.getValuesArray(headerName)
        return sum(valArray, 0.0) / len(valArray)

    def printAllMinMax(self):
        '''Print the maximum and minimum values of all fields in the frequent
        output.'''
        if not self.populated: self.populateFromFile()
        print "Maximum and minimum values for quantities in Frequent Output:"
        for header in self.headers:
            if header == 'Timestep': continue
            min, minStep = self.getMin(header)
            max, maxStep = self.getMax(header)
            print "\t%s: min %f (at step %d), max %f (at step %d)"\
                % (header, min, minStep, max, maxStep)
    
    def getReductionOp(self, headerName, reduceFunc):
        '''Utility function for doing comparison operations on the records
        list, e.g. the max or minimum - where reduceFunc can operate on the
        whole records list at once, and support the "key" syntax to pick
        correct field out of tuples for comparison.'''
        if not self.populated: self.populateFromFile()
        if len(self.records) == 0: return None, None
        colNum = self.getColNum(headerName)
        tStepColNum = self.getColNum('Timestep')
        retRecord = reduceFunc(self.records, key=operator.itemgetter(colNum))
        return retRecord[colNum], retRecord[tStepColNum]

    def getComparisonOp(self, headerName, cmpFunc):
        '''Utility function for doing comparison operations on the records
        list, e.g. the max or minimum - where cmpFunc is a single operator'''
        if not self.populated: self.populateFromFile()
        if len(self.records) == 0: return None, None
        colNum = self.getColNum(headerName)
        tStepColNum = self.getColNum('Timestep')
        firstRec = self.records[0]
        retVal, retStep = firstRec[colNum], firstRec[tStepColNum]
        for record in self.records:
            if cmpFunc(record[colNum], retVal):
                retVal, retStep = record[colNum], record[tStepColNum]
        return retVal, retStep

    def plotOverTime(self, headerName, show=False, save=True, path="."):
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            print "Error, to use UWA built-in plot functions, please "\
                " install the matplotlib python library."
            return    
        
        if not self.populated: self.populateFromFile()
        valuesArray = self.getValuesArray(headerName)
        tSteps = self.getTimeStepsArray()

        plot = plt.clf()   # Start by clearing any pre-existing figure
        plt.plot(tSteps, valuesArray)
        plt.xlabel("Timestep")
        plt.ylabel(headerName)
        plt.title("Output parameter '%s' over time"\
            % (headerName))

        if save:
            filename = os.path.join(path, headerName+"-timeSeries.png")
            plt.savefig(filename, format="png")
        if show: plt.show()
        return plt
