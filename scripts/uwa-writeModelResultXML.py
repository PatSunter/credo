#!/usr/bin/env python

import sys, getopt
import uwa

def main(argv):

    if len(argv) == 0:
        usage()
        sys.exit(2)

    try:
        opts, args = getopt.getopt(argv, "vu", ["verbose", "update"])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    modelName=args[0]

    updateMode=False
    for opt, arg in opts:
        if opt in ('-u', '--update'):
            updateMode=True

    walltime=0
    fResults=[]
    #TODO: would be good to get these provided from a static function
    # of uwa.modelRun ...
    assigned={'walltime':False}
    optional=['FR']

    for arg in args[1:]:
        try:
            param, val = arg.split('=')
        except ValueError:
            print "UWA ModelResults XML Writer: Error with provided argument"\
                " '%s', should be in the form param=value\n" % arg
            sys.exit(2)

        if val == "":
            print "UWA ModelResults XML Writer: Error with provided argument"\
                "'%s', needs a value provided for the parameter to be"\
                " written\n" % param
            sys.exit(2)

        if param in assigned:
            assigned[param]=True
            #TODO: could make this bit more maintainable by filling in
            # dictionary directly...
            if param == 'walltime':
                walltime=val
        elif param in optional:
            if param == 'FR':
                fieldName, tol, error = val.split(',')
                fResult = uwa.FieldResult(fieldName, float(tol), float(error))
                if updateMode:
                    #Write the value straight away
                    mrFile = uwa.defaultModelResultFilename(modelName)
                    uwa.updateModelResultsXMLFieldInfo(mrFile, fResult)
                else:
                    fResults.append(fResult)
        else:
            print "UWA ModelResults XML Writer: Error with provided argument"\
                " '%s', param '%s' is not in known list of model result "\
                " parameters" % (arg,param)
            print "Parameters that need to be assigned are:"
            print assigned.keys()
            print "Optional parameters are:"
            print optional
            sys.exit(2)

    if not updateMode:
        for kw, val in assigned.iteritems():
            if val != True:
                print "UWA ModelResults XML Writer: Error, necessary"\
                    " parameter '%s' not specified.\n" % kw
                print "Parameters that need to be assigned are:"
                print assigned.keys()
                sys.exit(2)

        mRes = uwa.ModelResult(modelName, walltime)
        mRes.fieldResults = fResults
        uwa.writeModelResultsXML(mRes)

def usage():
    print "Error in command line options passed to the XML writer script\n"

if __name__ == "__main__":
    main(sys.argv[1:])
