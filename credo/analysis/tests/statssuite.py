import matplotlib.pyplot as plt
from scipy.stats import linregress as scipylinregress
from credo.analysis.stats import linreg as credolinreg
import math

# -------------------------------------
# Testing

xArr = [1.5, 2.4, 3.2, 4.8,  5.0, 7.0,  8.43]
yArr = [3.5, 5.3, 7.7, 6.2, 11.0, 9.5, 10.27]
gradient, intercept, r_value, prob_value, std_err = scipylinregress(xArr,yArr)
print "** Results using Scipy**"
print "Gradient", gradient
print "Intercept", intercept
print "R value (Pearson correlation)", r_value
print "R-squared", r_value**2
print "prob-value", prob_value


xCoeff, yCoeff, rSq = credolinreg(xArr,yArr)
print "\n** Results from custom func used in CREDO**"
print "xCoeff (gradient)", xCoeff
print "yCoeff (intercept)", yCoeff
print "R value (Pearson correlation)", math.sqrt(rSq)
print "R-squared", rSq

# StgFEM case
print "\n** Results from real StgFEM data**"

scales = [1.000000e-01, 5.000000e-02, 3.333333e-02, 2.500000e-02]
velField1Err = [9.48975248e-06, 5.98833029e-07, 1.18487871e-07, 3.74909918e-08]

scaleLogs = map(math.log10, scales)
velErrLogs = map(math.log10, velField1Err)
print "Len scales(log10): %s" % scaleLogs
print "errors vs analytic(log10): %s" % velErrLogs

xCoeff, yCoeff, rSq = credolinreg(scaleLogs, velErrLogs)
cvgRate = xCoeff
intercept = yCoeff
print "R value (Pearson correlation)", math.sqrt(rSq)
print "xCoeff (cvgRate)", xCoeff
