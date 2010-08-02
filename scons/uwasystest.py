import os
import sys
import py_compile
from SCons.Script import *

class ToolUWASysTestWarning(SCons.Warnings.Warning):
    pass

SCons.Warnings.enableWarningClass(ToolUWASysTestWarning)

def generate(env, **kw):
    # Extend the Python path, actual path, and Stg Vars, so uwa can be used.
    # We need to update actual environment variables, not the SCons env,
    # so test scripts which are sub-programs can be executed.
    # TODO: update this to be a build dir thing when UWA is installed properly.
    # Set up paths etc for functions below
    stgBaseDir = os.path.abspath('.')
    uwaPath = os.path.abspath('uwa')
    sys.path.insert(0, uwaPath)
    import uwa.systest.systestrunner
    os.environ['STG_BASEDIR'] = stgBaseDir
    # Set up the environment for sub-scripts
    env['ENV']['STG_BASEDIR'] = stgBaseDir
    env.PrependENVPath('PATH', os.path.join(uwaPath, "scripts"))
    env.PrependENVPath('PYTHONPATH', "%s" % uwaPath)

    testOutput = "./testLogs"
    Execute(Mkdir(testOutput))
    env['TEST_OUTPUT_PATH'] = os.path.abspath(testOutput)

    env.SetDefault(CHECK_INTEGRATION_TARGET="check-integration")
    env.SetDefault(CHECK_CONVERGENCE_TARGET="check-convergence")
    env.SetDefault(CHECK_LOWRES_TARGET="check-lowres")

    LOWRES_SUITES = []
    INTEGRATION_SUITES = []
    CONVERGENCE_SUITES = []
    # Need to use Export rather than saving on env object, since we clone
    #  the env for each sub-project
    Export('LOWRES_SUITES')
    Export('INTEGRATION_SUITES')
    Export('CONVERGENCE_SUITES')

    # This will append to the standard help with testing help.
    Help("""
SCons-Check Options:
    Type: './scons.py check' to run the stgUnderworld unit and low-res integration tests only,
          './scons.py check-complete' to run the stgUnderworld unit, convergence, low-res and normal-res integration tests,
          './scons.py check-unit' to run the stgUnderworld unit tests only,
          './scons.py check-convergence' to run the stgUnderworld convergence tests only,
          './scons.py check-integration' to run the normal-res integration tests,
          './scons.py check-lowres' to run the low-res integration tests.
""" )

    def pathToPyModuleName(relPath):
        """Convert a relative path of a suite to a Python module
        name to import. E.g.:
        StgFEM/SysTest/PerformanceTests/testAll.py becomes
        StgFEM.SysTest.PerformanceTests.testAll"""
        newPath = relPath.rstrip(".py")
        modName = newPath.replace(os.sep, '.')
        return modName
    
    def addStGermainTarget(env, target, source):
        """Adds StGermain executable as a dependency - useful for an
        emitter for test run suites.""" 
        env.Depends(target[0], 
            File(os.path.join(env['build_dir'], 'bin/StGermain')))
        # TODO: would be kind of good to allow dependency to be specified
        #  on all other libraries and plugins:- that probably involves
        #  scanning XMLs, a bit over the top for now.
        return target, source


    # This is the core Builder for running a set of system tests
    def runSuites(env, target, source, **kw):
        """SCons builder function for running suites. The `source`
        argument must be a list of test scripts relative to
        the base of a project.
        
        .. note:: currently `source` argument is a list of suite file names,
           as SCons File objects. Ideally would like some smarter target
           checking, perhaps if these were .pyc files that depended on 
           both the .py file, and the relevant project executable."""
        xmlOutputDir = str(target[0])
        suiteFiles = map(str, source)
        suiteModNames = map(pathToPyModuleName, suiteFiles)
        uwa.systest.systestrunner.runSuitesFromModules(suiteModNames,
            xmlOutputDir)
        return None

    # Define a builder for a cvg suite: should be dependent on a project
    def sysTestSuite(env, target, source, **kw):
        py_compile.compile(source[0].get_abspath(),
            cfile=target[0].get_abspath())
        return None

    def addSysTestSuite(env, suiteFilename, suiteList):
        projectName = env['CURR_PROJECT']
        cvgTest = env.SysTestSuite(suiteFilename.rstrip(".py"))
        subImport = pathToPyModuleName(suiteFilename)
        testImportName = "%s.%s" % (projectName, subImport)
        # This will append this test's info to the check-cvg alias,
        # not redefine it.
        #env.Alias("check-cvg", cvgTest)
        # SuiteListName is now an actual variable
        suiteList.append(os.path.join(projectName, suiteFilename))
        # Or append the target? suiteList.append(cvgTest)
        # Alias for running just this particular test
        testResultDir = os.path.join(env['TEST_OUTPUT_PATH'], 
            testImportName)
        # TODO: perhaps here is where to update the CURR_PROJECT as a
        # Dependency of the suite, so it builds Underworld first
        singleTestRunner = env.RunSuites(Dir(testResultDir), suiteFilename)
        env.Alias(testImportName, singleTestRunner) 
        env.AlwaysBuild(singleTestRunner)
        # TODO: It would also be cool to update a list of suites based
        #  on the project, e.g. build a "check-Underworld" target to
        #  run all suites added to Underworld project.
        return None

    def addLowResTestSuite(env, suiteFilename):
        # The Import and Export are 'magic' SCons features, see:
        # see http://www.scons.org/doc/HTML/scons-user/x3255.html
        Import('LOWRES_SUITES')
        retVal = addSysTestSuite(env, suiteFilename, LOWRES_SUITES)
        Export('LOWRES_SUITES')
        return retVal

    def addIntegrationTestSuite(env, suiteFilename):
        Import('INTEGRATION_SUITES')
        retVal = addSysTestSuite(env, suiteFilename, INTEGRATION_SUITES)
        Export('INTEGRATION_SUITES')
        return retVal

    def addConvergenceTestSuite(env, suiteFilename):
        Import('CONVERGENCE_SUITES')
        retVal = addSysTestSuite(env, suiteFilename, CONVERGENCE_SUITES)
        Export('CONVERGENCE_SUITES')
        return retVal

    # Define the runSuites function as a proper builder
    # The emitter adds StGermain binary as a required target.
    runSuitesBuilder = Builder(action=runSuites, emitter=addStGermainTarget)
    sysTestSuiteBuilder = Builder(action=sysTestSuite, suffix=".pyc",
        src_suffix=".py")
    # Add all the builders we've defined
    env.Append(BUILDERS={
        "RunSuites":runSuitesBuilder,
        "SysTestSuite":sysTestSuiteBuilder})
    # This adds our pseudo-builders for various test suites
    #  See http://www.scons.org/doc/HTML/scons-user/c3805.html
    env.AddMethod(addLowResTestSuite, "AddLowResTestSuite")
    env.AddMethod(addIntegrationTestSuite, "AddIntegrationTestSuite")
    env.AddMethod(addConvergenceTestSuite, "AddConvergenceTestSuite")


def exists(env):
    # Should probably have this search for the uwa
    # libraries/source or something.
    return True        
