#!/usr/bin/env python

import sys, getopt
import credo

import pdb

def main(argv):

    if len(argv) == 0:
        usage()
        sys.exit(2)

    try:                                
        opts, args = getopt.getopt(argv, "v", ["verbose"])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    modelName=args[0]

    inputFiles=[]
    outputPath=""
    nproc=0
    #TODO: would be good to get these provided from a static function
    # of credo.modelRun ...
    assigned={'inputFile':False,'outputPath':False,'nproc':False}
    optional=[]

    for arg in args[1:]:
        try:
            param, val = arg.split('=')
        except ValueError:
            print "CREDO ModelRun XML Writer: Error with provided" \
                " argument '%s', should be in the form param=value\n" % arg
            sys.exit(2)

        if val == "":
            print "CREDO ModelRun XML Writer: Error with provided"\
                " argument '%s', needs a value provided for the"
                " parameter to be written\n" % param
            sys.exit(2)

        if param in assigned:
            assigned[param]=True
            #TODO: could make this bit more maintainable by filling in
            # dictionary directly...
            if param == 'inputFile':
                inputFiles.append(val)
            if param == 'outputPath':
                outputPath=val
            if param == 'nproc':
                nproc=val
        elif param in optional:
            # None currently
            pass
        else:
            print "CREDO ModelRun XML Writer: Error with provided argument '%s',"\
                " param '%s' is not in known list of model result parameters"\
                % (arg,param)
            print "Parameters that need to be assigned are:"
            print assigned.keys()
            print "Optional parameters are:"
            print optional
            sys.exit(2)

    for kw, val in assigned.iteritems():
        if val != True:
            print "CREDO ModelRun XML Writer: Error, necessary parameter"\
                " '%s' not specified.\n" % kw
            print "Parameters that need to be assigned are:"
            print assigned.keys()
            sys.exit(2)

    mRun = credo.ModelRun(modelName, inputFiles, outputPath, nproc)
    mRun.writeModelRunXML()

def usage():
    print "Error in command line options passed to the XML writer script\n"

if __name__ == "__main__":
    main(sys.argv[1:])
