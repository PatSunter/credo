fCompListMgr = FieldCompListMgr()

# if reading from XML
fCompListMgr.readFromStgXML()
# means we can now access fCompListMgr.fieldCompares

# Comparing two straight fields.
fComp = FieldCompare("VelocityField", "PressureField")

# Comparing against analytic
tempAnalytic = AnalyticPluginField("StgFEM_CosineHillRotate", 0)
fComp = FieldCompare("TemperatureField", tempAnalytic)
0)

# Comparing against reference
tempRef = ReferenceField("PressureField", "expected/Multigrid-referenceTest")
fComp = FieldCompare("PressureField", tempRef)

# TODO: how do we write Stg XML - and package the individual ops into a list?
for fComp in [fComp1, fComp2, fComp3]:
    fCompListMgr.add(fComp)

fCompListMgr.writeStgXML()

# Qtns: does the above suggest the fields will actually operable in Python, i.e.
# to get out data from them?

# Get results

fCompRes = fCompOp.getResult()
# fCompRes then contains convergence info ...

# Operate on result?
status = fCompRes.checkWithinTol( 0.1, "last" )
fCompRes.plotOverTime() 
fComp.writeInfoXML()
fCompRes.writeInfoXML()

# Or general funcs?
fields.plotOverTime(fComp, fCompRes)
fields.writeInfoXML(fComp, fCompRes)
