import os
import sys
from SCons.Script import *
#from SCons.Builder import Builder

class ToolUWASysTestWarning(SCons.Warnings.Warning):
    pass

SCons.Warnings.enableWarningClass(ToolUWASysTestWarning)

def generate(env, **kw):
    # Extend the Python path, actual path, and Stg Vars, so uwa can be used.
    # We need to update actual environment variables, not the SCons env,
    # so test scripts which are sub-programs can be executed.
    # TODO: update this when UWA is installed properly.
    uwaPath = os.path.abspath('uwa')
    env['ENV']['STG_BASEDIR'] = os.path.abspath('.')
    env.PrependENVPath('PATH', os.path.join(uwaPath, "scripts"))
    env.PrependENVPath('PYTHONPATH', "%s" % uwaPath)
    env.SetDefault(INTEGRATION_TARGET="check-integration")
    env.SetDefault(CONVERGENCE_TARGET="check-convergence")
    env.SetDefault(LOWRES_TARGET="check-lowres")

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

    # Several of the tests also refer to targets defined initially in
    #  PCU testing, in pcutest.py
    def IntegrationTest(env, target, source, **kw):
        script = File(source[0].split()[0]).srcnode().abspath
        script_dir = os.path.dirname(script)
        script = os.path.basename(script)
        args = source[0].split()[1:]

        runner = env.Action('-./' + script + ' ' + ' '.join(args), chdir=script_dir)
        env.Alias(env["INTEGRATION_TARGET"], [], runner)
        env.AlwaysBuild(env["INTEGRATION_TARGET"])
        env.Alias(env['PCUALL_TARGET'], env['INTEGRATION_TARGET'])
        return None


    def LowResTest(env, target, source, **kw):
        script = File(source[0].split()[0]).srcnode().abspath
        script_dir = os.path.dirname(script)
        script = os.path.basename(script)
        args = source[0].split()[1:]

        runner = env.Action('-./' + script + ' ' + ' '.join(args), chdir=script_dir)
        env.Alias(env["LOWRES_TARGET"], [], runner)
        env.AlwaysBuild(env["LOWRES_TARGET"])
        env.Alias(env['PCUALL_TARGET'], env['LOWRES_TARGET'])
        env.Alias(env['REGTEST_TARGET'], env['LOWRES_TARGET'])
        return None

    def ConvergenceTest(env, target, source, **kw):
        script = File(source[0].split()[0]).srcnode().abspath
        script_dir = os.path.dirname(script)
        script = os.path.basename(script)
        args = source[0].split()[1:]

        runner = env.Action('-./' + script + ' ' + ' '.join(args), chdir=script_dir)
        env.Alias(env["CONVERGENCE_TARGET"], [], runner)
        env.AlwaysBuild(env["CONVERGENCE_TARGET"])
        env.Alias(env['PCUALL_TARGET'], env['CONVERGENCE_TARGET'])
        return None

    env.Append(BUILDERS={"LowResTest":LowResTest, 
        "IntegrationTest":IntegrationTest,
        "ConvergenceTest":ConvergenceTest})

def exists(env):
    # Should probably have this search for the uwa
    # libraries/source or something.
    return True        
