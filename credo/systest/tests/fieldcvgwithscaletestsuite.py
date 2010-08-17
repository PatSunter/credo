import matplotlib.pyplot as plt
import credo.analysis.fields as fields
from credo.systest.fieldCvgWithScaleTest import *
import credo.analysis.fields as fields

# Convergence checker
# StgFEM case
print "\n** Results from real StgFEM data - from a Convergence file**"
cvgFilePath = "./output/cvgTest"
lenScales, fErrorData = fields.getFieldScaleCvgData_SingleCvgFile(cvgFilePath)
overallRes = testAllCvgWithScale(lenScales, fErrorData, 
    defFieldScaleCvgCriterions)

velCvg = fields.calcFieldCvgWithScale("VelocityField", lenScales,
     fErrorData["VelocityField"])
pCvg = fields.calcFieldCvgWithScale("PressureField", lenScales,
     fErrorData["PressureField"])

velResult = testCvgWithScale("VelocityField", velCvg,
    defFieldScaleCvgCriterions["VelocityField"])
pResult = testCvgWithScale("PressureField", pCvg,
     defFieldScaleCvgCriterions["PressureField"])
