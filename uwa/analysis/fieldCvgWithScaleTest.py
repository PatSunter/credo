import uwa.analysis.fields as fields

# The criteria of convergence: first is cvg rate, second is correlation
defFieldScaleCvgCriterions = {
    'VelocityField':(1.6,0.99),
    'PressureField':(0.9,0.99),
    'StrainRateField':(0.85,0.99) }

# For each field
# Check all the necessary convergence files available
# Get the final error vs analytic soln value for each res

# Then apply the convergence check algorithm to each of these.

#def convergenceCheck( resSets, compareResults ):
#    f


def testAllCvgWithScale(fieldErrorData, fieldCvgCriterions):    
    for fieldName, cvgTestData in fieldErrorData.iteritems():
        runRes, dofErrors = cvgTestData
        fieldConv = fields.calcFieldCvgWithScale(fieldName, runRes, dofErrors)
        reqCvgRate, reqCorr = fieldCvgCriterions[fieldName]
        for dofI, dofConv in enumerate(fieldConv):
            cvgRate, pearsonCorr = dofConv
            print "Field %s, dof %d - cvg rate %f, corr %f" \
                % (fieldName, dofI, cvgRate, pearsonCorr)
            #plt.plot(resLogs, errLogs)
            #plt.show()

            testStatus = True
            if cvgRate < reqCvgRate: 
                testStatus = False
                print "  -Bad! - cvg %f less than req'd %f for this field."\
                    % (cvgRate, reqCvgRate)

            if pearsonCorr < reqCorr:
                testStatus = False
                print "  -Bad! - corr %f less than req'd %f for this field."\
                    % (pearsonCorr, reqCorr)

            if testStatus: print "  -Good"
