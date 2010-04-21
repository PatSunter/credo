from uwa.analysis.fields import FieldTest, FieldTestsInfo
from uwa.io import stgcvg

fieldTests = FieldTestsInfo()
fTest = FieldTest('VelocityField', tol=3e-2)
fieldTests.add(fTest)
results = fieldTests.testConvergence("./output/realistic")

fr = results[0]

fr.plotCvgOverTime(show=True, dofIndex=0, path="./output/realistic")

#Plotting
#dofErrors = stgcvg.getDofErrors_ByDof( fr.cvgFileInfo )

#import matplotlib.pyplot as plt
#plt.plot(dofErrors[0])
#plt.axhline(y=fr.tol, label='tolerance', linewidth=3, color='r')
#plt.xlabel("Timestep")
#plt.ylabel("Error vs analytic soln")
#plt.title("Convergence of field '%s', dof %d, with analytic solution"
#    % (fr.fieldName,0))
#plt.savefig(fr.fieldName+"-cvg.png",format="png")
#plt.show()
