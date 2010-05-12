import matplotlib.pyplot as plt
import uwa.analysis.fields as fields
from uwa.systest.fieldCvgWithScaleTest import *
import uwa.analysis.fields as fields

# Convergence checker
# StgFEM case
print "\n** Results from real StgFEM data - from a Convergence file**"
cvgFilePath = "./output/cvgTest"
lenScales, fErrorData = fields.getFieldScaleCvgData_SingleCvgFile(cvgFilePath)
testAllCvgWithScale(lenScales, fErrorData, defFieldScaleCvgCriterions)
