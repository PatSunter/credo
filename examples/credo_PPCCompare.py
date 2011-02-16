#! /usr/bin/env python
import os, copy
from credo.modelrun import ModelRun, SimParams
from credo.modelsuite import ModelSuite
import credo.jobrunner

jobRunner = credo.jobrunner.defaultRunner()

defParams = SimParams(nsteps=2)
stdRun = ModelRun("Arrhenius-normal",
    os.path.join('..','..', 'Underworld', 'InputFiles', 'Arrhenius.xml'),
    "output/arrBasic", simParams=defParams)
ppcRun = ModelRun("Arrhenius-ppc", "Arrhenius.xml",
    basePath=os.path.join("Ppc_Testing","udw_inputfiles"),
    outputPath="output/arrPIC",
    simParams=defParams)

stdSuite = ModelSuite(os.path.join("output", "arrBasic"))
ppcSuite = ModelSuite(os.path.join(os.getcwd(), "output", "arrPIC"))

for ii in range(10):
    stdRun.outputPath = os.path.join(stdSuite.outputPathBase, "%.5d" % ii)
    ppcRun.outputPath = os.path.join(ppcSuite.outputPathBase, "%.5d" % ii)
    stdSuite.addRun(copy.deepcopy(stdRun))
    ppcSuite.addRun(copy.deepcopy(ppcRun))

stdResults = jobRunner.runSuite(stdSuite)
ppcResults = jobRunner.runSuite(ppcSuite)

#-----------------------------

cpuRegs = []
cpuPPCs = []
for stdRes, ppcRes in zip(stdResults, ppcResults):
    stdRes.readFrequentOutput()
    ppcRes.readFrequentOutput()
    fStep = stdRes.freqOutput.finalStep()
    cpuReg = stdRes.freqOutput.getValueAtStep('CPU_Time', fStep)
    cpuPPC = ppcRes.freqOutput.getValueAtStep('CPU_Time', fStep)
    print "CPU time regular was %g, PPC was %g" % (cpuReg, cpuPPC)
    cpuRegs.append(cpuReg)
    cpuPPCs.append(cpuPPC)

avgReg = sum(cpuRegs) / len(cpuRegs)
avgPPC = sum(cpuPPCs) / len(cpuPPCs)

print "Avg over 10 runs: regular=%f, PPC=%f" % (avgReg, avgPPC)
avgInfo = open("comparePPC.txt", "w")
avgInfo.write("Avg regular = %f\n" % avgReg)
avgInfo.write("Avg PPC = %f\n" % avgPPC)
avgInfo.close()
