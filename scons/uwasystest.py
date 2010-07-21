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
