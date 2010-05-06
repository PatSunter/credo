import matplotlib.pyplot as plt
from scipy import stats

# Trying custom func
from math import sqrt

# From http://www.answermysearches.com/how-to-do-a-simple-linear-regression-in-python/124/
def customlinreg(X, Y):
    """
    Summary
        Linear regression of y = ax + b
    Usage
        real, real, real = linreg(list, list)
    Returns coefficients to the regression line "y=ax+b" from x[] and y[], and R^2 Value
    """
    if len(X) != len(Y):  raise ValueError, 'unequal length'
    N = len(X)
    Sx = Sy = Sxx = Syy = Sxy = 0.0
    for x, y in map(None, X, Y):
        Sx = Sx + x
        Sy = Sy + y
        Sxx = Sxx + x*x
        Syy = Syy + y*y
        Sxy = Sxy + x*y
    det = Sxx * N - Sx * Sx
    a, b = (Sxy * N - Sy * Sx)/det, (Sxx * Sy - Sx * Sxy)/det
    meanerror = residual = 0.0
    for x, y in map(None, X, Y):
        meanerror = meanerror + (y - Sy/N)**2
        residual = residual + (y - a * x - b)**2
    RR = 1 - residual/meanerror
    ss = residual / (N-2)
    Var_a, Var_b = ss * N / det, ss * Sxx / det
    #print "y=ax+b"
    #print "N= %d" % N
    #print "a= %g \\pm t_{%d;\\alpha/2} %g" % (a, N-2, sqrt(Var_a))
    #print "b= %g \\pm t_{%d;\\alpha/2} %g" % (b, N-2, sqrt(Var_b))
    #print "R^2= %g" % RR
    #print "s^2= %g" % ss
    return a, b, RR


# -------------------------------------
# Testing

xArr = [1.5, 2.4, 3.2, 4.8,  5.0, 7.0,  8.43]
yArr = [3.5, 5.3, 7.7, 6.2, 11.0, 9.5, 10.27]
gradient, intercept, r_value, prob_value, std_err = stats.linregress(xArr,yArr)
print "** Results using Scipy**"
print "Gradient and intercept", gradient, intercept
print "R value (Pearson correlation)", r_value
print "R-squared", r_value**2
print "prob-value", prob_value


xCoeff, yCoeff, rSq = customlinreg(xArr,yArr)
print "\n** Results from custom func**"
print "R value (Pearson correlation)", sqrt(rSq)
print "R-squared", rSq
print "xCoeff", xCoeff
print "yCoeff", yCoeff

# StgFEM case
res = [1.000000e-01, 5.000000e-02, 3.333333e-02, 2.500000e-02]
velField1Err = [9.48975248e-06, 5.98833029e-07, 1.18487871e-07, 3.74909918e-08]
#velField2Err = [
#pressFieldErr = [

print "\n** Results from real StgFEM data**"

from math import log10

resLogs = map(log10, res)
velErrLogs = map(log10, velField1Err)
print resLogs
print velErrLogs

xCoeff, yCoeff, rSq = customlinreg(resLogs, velErrLogs)
cvgRate = xCoeff
intercept = yCoeff
print "R value (Pearson correlation)", sqrt(rSq)
print "R-squared", rSq
print "xCoeff (cvgRate)", xCoeff
print "yCoeff (intercept)", yCoeff

# Convergence checker
# StgFEM case
print "\n** Results from real StgFEM data - from a Convergence file**"
from uwa.io import stgcvg

def getFieldConvergence(fieldName, runRes, dofErrors):
    print "Testing convergence for field '%s'" % fieldName
    #print "Run resolutions are %s" % runRes
    #print "Dof errors for %d dofs are %s" % (len(dofErrors), dofErrors)
    resLogs = map(log10, runRes)
    convResults = []
    for errorArray in dofErrors:
        errLogs = map(log10, errorArray)
        cvgRate, intercept, rSq = customlinreg(resLogs, errLogs)
        pearsonCorr = sqrt(rSq)
        convResults.append((cvgRate, pearsonCorr))
    return convResults    

def testAllConvergence(fieldErrorData, fieldCvgCriterions):    
    for fieldName, cvgTestData in fieldErrorData.iteritems():
        runRes, dofErrors = cvgTestData
        fieldConv = getFieldConvergence(fieldName, runRes, dofErrors)
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


# Stage 1: read the convergence file, to grab necessary data (assume all in
# same file)
cvgIndex = stgcvg.genConvergenceFileIndex("./output/cvgTest")

fieldErrorData = {}
for fieldName, cvgFileInfo in cvgIndex.iteritems():
    runRes = stgcvg.getRes(cvgFileInfo.filename)
    dofErrors = stgcvg.getDofErrors_ByDof(cvgFileInfo)
    fieldErrorData[fieldName] = (runRes, dofErrors)    

# The criteria of convergence: first is cvg rate, second is correlation
defFieldCvgCriterions = {
    'VelocityField':(1.6,0.99),
    'PressureField':(0.9,0.99),
    'StrainRateField':(0.85,0.99) }

# Stage 2: perform the actual tests
testAllConvergence(fieldErrorData, defFieldCvgCriterions)

