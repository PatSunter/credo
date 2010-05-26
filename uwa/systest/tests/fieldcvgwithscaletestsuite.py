import matplotlib.pyplot as plt
import uwa.analysis.fields as fields
from uwa.systest.fieldCvgWithScaleTest import *
import uwa.analysis.fields as fields

# Convergence checker
# StgFEM case
print "\n** Results from real StgFEM data - from a Convergence file**"
cvgFilePath = "./output/cvgTest"
lenScales, fErrorData = fields.getFieldScaleCvgData_SingleCvgFile(cvgFilePath)
overallRes = testAllCvgWithScale(lenScales, fErrorData, 
    defFieldScaleCvgCriterions)
velResult = testCvgWithScale("VelocityField", lenScales,
    fErrorData["VelocityField"], defFieldScaleCvgCriterions["VelocityField"])
pResult = testCvgWithScale("PressureField", lenScales,
    fErrorData["PressureField"], defFieldScaleCvgCriterions["PressureField"])
