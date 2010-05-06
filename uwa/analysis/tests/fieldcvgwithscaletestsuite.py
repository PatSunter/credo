import matplotlib.pyplot as plt
import uwa.analysis.fields as fields
from uwa.analysis.fieldCvgWithScaleTest import *

# Convergence checker
# StgFEM case
print "\n** Results from real StgFEM data - from a Convergence file**"
cvgFilePath = "./output/cvgTest"
fieldErrorData = fields.getFieldScaleCvgData_SingleCvgFile(cvgFilePath)
testAllCvgWithScale(fieldErrorData, defFieldScaleCvgCriterions)
