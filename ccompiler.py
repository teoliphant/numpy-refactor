
import re
import os
import sys
import new

from distutils.ccompiler import *
from distutils import ccompiler
from distutils.sysconfig import customize_compiler

import log
from exec_command import exec_command
from misc_util import compiler_to_string

# Using customized CCompiler.spawn.
def CCompiler_spawn(self, cmd, display=None):
    if display is None:
        display = cmd
        if type(display) is type([]): display = ' '.join(display)
    log.info(display)
    s,o = exec_command(cmd)
    if s:
        if type(cmd) is type([]):
            cmd = ' '.join(cmd)
        raise DistutilsExecError,\
              'Command "%s" failed with exit status %d' % (cmd, s)
CCompiler.spawn = new.instancemethod(CCompiler_spawn,None,CCompiler)

def CCompiler_compile(self, sources, output_dir=None, macros=None,
                      include_dirs=None, debug=0, extra_preargs=None,
                      extra_postargs=None, depends=None):
    from fcompiler import FCompiler
    if isinstance(self, FCompiler):
        display = []
        for fcomp in ['f77','f90','fix']:
            fcomp = getattr(self,'compiler_'+fcomp)
            if fcomp is None:
                continue
            display.append('%s options: "%s"' % (os.path.basename(fcomp[0]),
                                                 ' '.join(fcomp[1:])))
        display = '\n'.join(display)
    else:
        ccomp = self.compiler_so
        display = '%s options: "%s"' % (os.path.basename(ccomp[0]),
                                        ' '.join(ccomp[1:]))
    log.info(display)
    macros, objects, extra_postargs, pp_opts, build = \
            self._setup_compile(output_dir, macros, include_dirs, sources,
                                depends, extra_postargs)
    cc_args = self._get_cc_args(pp_opts, debug, extra_preargs)
    display = "compile options: '%s'" % (' '.join(cc_args))
    if extra_postargs:
        display += "extra: '%s'" % (' '.join(extra_postargs))
    log.info(display)
    for obj, (src, ext) in build.items():
        self._compile(obj, src, ext, cc_args, extra_postargs, pp_opts)
        
    # Return *all* object filenames, not just the ones we just built.
    return objects

CCompiler.compile = new.instancemethod(CCompiler_compile,None,CCompiler)

def CCompiler_customize_cmd(self, cmd):
    """ Customize compiler using distutils command.
    """
    log.info('customize %s using %s' % (self.__class__.__name__,
                                        cmd.__class__.__name__))
    if getattr(cmd,'include_dirs',None) is not None:
        self.set_include_dirs(cmd.include_dirs)
    if getattr(cmd,'define',None) is not None:
        for (name,value) in cmd.define:
            self.define_macro(name, value)
    if getattr(cmd,'undef',None) is not None:
        for macro in cmd.undef:
            self.undefine_macro(macro)
    if getattr(cmd,'libraries',None) is not None:
        self.set_libraries(self.libraries + cmd.libraries)
    if getattr(cmd,'library_dirs',None) is not None:
        self.set_library_dirs(self.library_dirs + cmd.library_dirs)
    if getattr(cmd,'rpath',None) is not None:
        self.set_runtime_library_dirs(cmd.rpath)
    if getattr(cmd,'link_objects',None) is not None:
        self.set_link_objects(cmd.link_objects)
    self.show_customization()
    return
CCompiler.customize_cmd = new.instancemethod(\
    CCompiler_customize_cmd,None,CCompiler)

def CCompiler_show_customization(self):
    for attrname in ['include_dirs','libraries','library_dirs',
                 'rpath','link_objects']:
        attr = getattr(self,attrname,None)
        if not attr:
            continue
        log.info("compiler '%s' is set to %s" % (attrname,attr))

CCompiler.show_customization = new.instancemethod(\
    CCompiler_show_customization,None,CCompiler)


def CCompiler_customize(self, dist):
    # See FCompiler.customize for suggested usage.
    log.info('customize %s' % (self.__class__.__name__))
    customize_compiler(self)
    return
CCompiler.customize = new.instancemethod(\
    CCompiler_customize,None,CCompiler)


if sys.platform == 'win32':
    compiler_class['mingw32'] = ('mingw32ccompiler', 'Mingw32CCompiler',
                                 "Mingw32 port of GNU C Compiler for Win32"\
                                 "(for MSC built Python)")
    if os.environ.get('OSTYPE','')=='msys' or \
           os.environ.get('MSYSTEM','')=='MINGW32':
        # On windows platforms, we want to default to mingw32 (gcc)
        # because msvc can't build blitz stuff.
        log.info('Setting mingw32 as default compiler for nt.')
        ccompiler._default_compilers = (('nt', 'mingw32'),) \
                                       + ccompiler._default_compilers


_distutils_new_compiler = new_compiler
def new_compiler (plat=None,
                  compiler=None,
                  verbose=0,
                  dry_run=0,
                  force=0):
    # Try first C compilers from scipy_distutils.
    if plat is None:
        plat = os.name
    try:
        if compiler is None:
            compiler = get_default_compiler(plat)
        (module_name, class_name, long_description) = compiler_class[compiler]
    except KeyError:
        msg = "don't know how to compile C/C++ code on platform '%s'" % plat
        if compiler is not None:
            msg = msg + " with '%s' compiler" % compiler
        raise DistutilsPlatformError, msg

    module_name = "scipy_distutils." + module_name
    try:
        __import__ (module_name)
    except ImportError, msg:
        print msg
        module_name = module_name[6:]
        try:
            __import__(module_name)
        except ImportError:
            raise DistutilsModuleError, \
                  "can't compile C/C++ code: unable to load module '%s'" % \
                  module_name
    try:
        module = sys.modules[module_name]
        klass = vars(module)[class_name]
    except KeyError:
        raise DistutilsModuleError, \
              ("can't compile C/C++ code: unable to find class '%s' " +
               "in module '%s'") % (class_name, module_name)
    compiler = klass(None, dry_run, force)
    print '*'*80
    print klass
    print compiler_to_string(compiler)
    print '*'*80
    return compiler

ccompiler.new_compiler = new_compiler

