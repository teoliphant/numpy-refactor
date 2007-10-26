# Last Change: Tue Oct 09 04:00 PM 2007 J
import os
import sys
import string

from os.path import basename, join as pjoin, dirname
from copy import deepcopy

from utils import popen_wrapper
from fortran import parse_f77link, check_link_verbose

#-----------------
# Public functions
#-----------------

# Getting verbose flag
def _CheckFVerbose(context, fcomp):
    flags = ['-v', '--verbose', '-verbose', '-V']
    for flag in flags:
        if _check_f_vflag(context, flag, fcomp):
            return 1, flag

    return 0, ''
        
def CheckF77Verbose(context):
    context.Message('Checking F77 %s verbose flag ... ' % context.env['F77'] )

    res, flag = _CheckFVerbose(context, 'F77')
    if res:
        context.Result(flag)
        context.env['F77LINK_VFLAG'] = flag
    else:
        context.Result('Failed !')

    return res
        
def CheckF90Verbose(context):
    context.Message('Checking F90 %s verbose flag ... ' % context.env['F90'] )

    res, flag = _CheckFVerbose(context, 'F90')
    if res:
        context.Result(flag)
        context.env['F90LINK_VFLAG'] = flag
    else:
        context.Result('Failed !')

    return res
        
# Checking whether the fortran compiler can compile and link a dummy program
def _CheckFDryRun(context, fc = 'F77'):
    """Check whether the compiler fc can compile a program."""
    env = context.env
    try:
        fcomp = env[fc]
    except KeyError:
        raise RuntimeError("Compiler type %s not known !" % fc)
    
    context.Message('Checking if %s compiler %s can create executables - ' % (fc, fcomp))
    # We use our own builder as long as I don't resolve the issue of TryLink
    # returning 1 when it fails.
    result = _build_empty_program(context, fc)[0]
    context.Result((result and 'yes' or 'no'))
    return result

def CheckF77DryRun(context):
    """Check whether the F77 compiler can compile a program."""
    return _CheckFDryRun(context, 'F77')

def CheckF90DryRun(context):
    """Check whether the F90 compiler can compile a program."""
    return _CheckFDryRun(context, 'F90')

# Getting fortran support runtime
def CheckF77Clib(context):
    """This tries to get Fortran runtime facilities necessary at link stage,
    and put the relevant flags in env['F77_LDFLAGS']."""
    if sys.platform[:5] == 'win32':
        raise Exception("FIXME: This is not tested on windows.... No chance "\
                        "of working if using visual Intel")
    fcompiler = 'F77'
    # TODO: check that F77 exists, and can be run
    if not context.env.has_key(fcompiler):
        raise Exception("F77 should be set before calling CheckF77Clib !")

    fflags = 'LINKFLAGS'
    env = context.env
    config = context.sconf
    context.Message('Checking %s C compatibility runtime ...' % env[fcompiler])
    # XXX: check how to get verbose output
    verbose = '-v'

    # Convention old* variables MUST be restored in ANY CONDITION.
    oldLINKFLAGS = env.has_key(fflags) and deepcopy(env[fflags]) or []

    try:
        context.env.Append(LINKFLAGS = verbose)
        res, cnt = _build_empty_program(context, fcompiler)
    finally:
        env.Replace(LINKFLAGS = oldLINKFLAGS)

    if res == 1:
        final_flags = parse_f77link(cnt)
        env.Append(F77_LDFLAGS = ' '.join(final_flags))
        context.Result(env['F77_LDFLAGS'])
    else:
        context.Result('Failed !')

    return res

# If need a dummy main
def _CheckFDummyMain(context, fcomp):
    fcn_tmpl = """
int %s() { return 0; }
"""
    env = context.env
    savedLINK = env.has_key('LINK') and deepcopy(env['LINK']) or []
    try:
        env['LINK'] = env[fcomp]
        mains = ["MAIN__", "__MAIN", "_MAIN", "MAIN_"]
        mains.extend([string.lower(m) for m in mains])
        mains.insert(0, "")
        mains.append("MAIN")
        mains.append("main")
        for m in mains:
            prog = fcn_tmpl % "dummy"
            if m:
                prog = fcn_tmpl % m + prog
            result = context.TryLink(prog, '.c')
            if result:
                if not m:
                    m = None
                break
    finally:
        env.Replace(LINK = savedLINK)
    return result, m

# XXX: refactor those by using function templates
def CheckF77DummyMain(context):
    context.Message('Checking if %s needs dummy main - ' % context.env['F77'])
    res, m = _CheckFDummyMain(context, 'F77')
    if res:
        context.Result("%s." % str(m))
        context.env['F77_DUMMY_MAIN'] = m
    else:
        context.Result("Failed !")

    return res

def CheckF90DummyMain(context):
    context.Message('Checking if %s needs dummy main - ' % context.env['F90'])
    res, m = _CheckFDummyMain(context, 'F90')
    if res:
        context.Result("%s." % str(m))
        context.env['F90_DUMMY_MAIN'] = m
    else:
        context.Result("Failed !" % str(m))

    return res

# Fortran name mangling
def _CheckFMangling(context, fc, dummym, ext):
    subr = """
      subroutine foobar()
      return
      end
      subroutine foo_bar()
      return
      end
"""
    main_tmpl = """
int %s() { return 1; }
"""
    prog_tmpl = """
void %s(void);
void %s(void);
int my_main() {
    %s();
    %s();
    return 0;
}
"""
    env = context.env
    savedLINK = env.has_key('LINK') and deepcopy(env['LINK']) or []
    savedLIBS = env.has_key('LIBS') and deepcopy(env['LIBS']) or []
    # TODO: if does not exist, call the function to get the F77_DUMMY_MAIN
    m = dummym
    try:
        env['LINK'] = env[fc]
        # variants:
        #   lower-case, no underscore, no double underscore: foobar, foo_bar
        #   ...
        #   upper-case, underscore, double underscore: FOOBAR_, FOO_BAR__
        context.TryCompile(subr, ext)
        obj = context.lastTarget
        env.Append(LIBS = env.StaticLibrary(obj))
        under = ['', '_']
        doubleunder = ['', '_']
        casefcn = ["lower", "upper"]
        gen = _RecursiveGenerator(under, doubleunder, casefcn)
        while True:
            try:
                u, du, c = gen.next()
                def make_mangler(u, du, c):
                    return lambda n: getattr(string, c)(n) +\
                                     u + (n.find('_') != -1 and du or '')
                mangler = make_mangler(u, du, c)
                foobar = mangler("foobar")
                foo_bar = mangler("foo_bar")
                prog = prog_tmpl % (foobar, foo_bar, foobar, foo_bar)
                if m:
                    prog = main_tmpl % m + prog
                result = context.TryLink(prog, '.c')
                if result:
                    break
            except StopIteration:
                result = mangler = u = du = c = None
                break
    finally:
        env.Replace(LINK = savedLINK)
        env.Replace(LIBS = savedLIBS)
    return result, mangler, u, du, c

def CheckF77Mangling(context):
    env = context.env
    context.Message('Checking %s name mangling - ' % env['F77'])
    res, mangler, u, du, c = _CheckFMangling(context, 'F77', env['F77_DUMMY_MAIN'], '.f')
    if res:
        context.Result("'%s', '%s', %s-case." % (u, du, c))
        env['F77_NAME_MANGLER'] = mangler
    else:
        context.Result("all variants failed.")
    return res

def CheckF90Mangling(context):
    env = context.env
    context.Message('Checking %s name mangling - ' % env['F90'])
    res, mangler, u, du, c = _CheckFMangling(context, 'F90', env['F90_DUMMY_MAIN'], '.f90')
    if res:
        context.Result("'%s', '%s', %s-case." % (u, du, c))
        env['F90_NAME_MANGLER'] = mangler
    else:
        context.Result("all variants failed.")
    return res

#------------------
# Support functions
#------------------
def _check_f_vflag(context, flag, fcomp):
    """Return True if flag is an acceptable verbose flag for fortran compiler
    fcomp."""
    
    oldLINKFLAGS = context.env['LINKFLAGS']
    res = 0
    try:
        context.env.Append(LINKFLAGS = flag)
        res, out = _build_empty_program(context, fcomp)
    finally:
        context.env['LINKFLAGS'] = oldLINKFLAGS
        
    return res and check_link_verbose(out)

def _build_empty_program(context, fcomp):
    """Build an empty fortran stand alone program, and capture the output of
    the link step.

    Return:
        st : 1 on success, 0 on failure.
        list : list of lines of the output."""
    cnt = []
    src = """
      PROGRAM MAIN
      END"""
    # XXX: the logic to choose fortran compiler is bogus...
    if fcomp == 'F77':
        res = context.TryCompile(src, '.f')
    elif fcomp == 'F90':
        res = context.TryCompile(src, '.f90')
    else:
        raise RuntimeError("fcomp %s not implemented..." % fcomp)
        return 0
    if res:
        oldLINK = context.env['LINK']
        # XXX: get the fortran compiler
        context.env['LINK'] = '$' + fcomp
        res = 0
        try:
            # We always want to do this build, and we do not want scons cache
            # to interfer. So we build a command executed directly through our
            # popen_wrapper, which output is captured.

            # XXX: does this scheme to get the program name always work ? Can
            # we use Scons to get the target name from the object name ?
            slast = str(context.lastTarget)
            dir = dirname(slast)
            test_prog = pjoin(dir, basename(slast).split('.')[0])
            cmd = context.env.subst('$LINKCOM', 
                                    target = context.env.File(test_prog),
                                    source = context.lastTarget)
            st, out = popen_wrapper(cmd, merge = True)
            if st:
                res = 0
            else:
                res = 1
            cnt = out.split('\n')
        finally:
            context.env['LINK'] = oldLINK
            
    return res, cnt

# Helper to generate combinations of lists
def _RecursiveGenerator(*sets):
   """Returns a generator that yields one tuple per element combination.
      A set may be any iterable to which the not operator is applicable.
   """
   if not sets: return
   def calc(sets):
      head, tail = sets[0], sets[1:]
      if not tail:
         for e in head:
            yield (e,)
      else:
         for e in head:
            for t in calc(tail):
               yield (e,) + t
   return calc(sets)

