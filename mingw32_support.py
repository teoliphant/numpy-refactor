"""
Support code for building Python extensions on Windows.

    # NT stuff
    # 1. Make sure libpython<version>.a exists for gcc.  If not, build it.
    # 2. Force windows to use gcc (we're struggling with MSVC and g77 support) 
    # 3. Force windows to use g77

"""

import os, sys
import distutils.ccompiler

# I'd really like to pull this out of scipy and make it part of distutils...
import scipy_distutils.command.build_flib as build_flib


if sys.platform == 'win32':
    # NT stuff
    # 1. Make sure libpython<version>.a exists for gcc.  If not, build it.
    # 2. Force windows to use gcc (we're struggling with MSVC and g77 support) 
    # 3. Force windows to use g77
    
    # 1.  Build libpython<version> from .lib and .dll if they don't exist.    
    import distutils.cygwinccompiler
    from distutils.version import StrictVersion
    from distutils.ccompiler import gen_preprocess_options, gen_lib_options
    from distutils.errors import DistutilsExecError, CompileError, UnknownFileError
    
    from distutils.unixccompiler import UnixCCompiler 
    
    # the same as cygwin plus some additional parameters
    class Mingw32CCompiler(distutils.cygwinccompiler.CygwinCCompiler):
        """ A modified MingW32 compiler compatible with an MSVC built Python.
            
        """
    
        compiler_type = 'mingw32'
    
        def __init__ (self,
                      verbose=0,
                      dry_run=0,
                      force=0):
    
            distutils.cygwinccompiler.CygwinCCompiler.__init__ (self, 
                                                       verbose,dry_run, force)
            
            # we need to support 3.2 which doesn't match the standard
            # get_versions methods regex
            if self.gcc_version is None:
                import re
                out = os.popen('gcc' + ' -dumpversion','r')
                out_string = out.read()
                out.close()
                result = re.search('(\d+\.\d+)',out_string)
                if result:
                    self.gcc_version = StrictVersion(result.group(1))            

            # A real mingw32 doesn't need to specify a different entry point,
            # but cygwin 2.91.57 in no-cygwin-mode needs it.
            if self.gcc_version <= "2.91.57":
                entry_point = '--entry _DllMain@12'
            else:
                entry_point = ''
            if self.linker_dll == 'dllwrap':
                self.linker = 'dllwrap' + ' --driver-name g++'
            elif self.linker_dll == 'gcc':
                self.linker = 'g++'    

            # **changes: eric jones 4/11/01
            # 1. Check for import library on Windows.  Build if it doesn't exist.
            if not import_library_exists():
                build_import_library()
    
            # **changes: eric jones 4/11/01
            # 2. increased optimization and turned off all warnings
            # 3. also added --driver-name g++
            #self.set_executables(compiler='gcc -mno-cygwin -O2 -w',
            #                     compiler_so='gcc -mno-cygwin -mdll -O2 -w',
            #                     linker_exe='gcc -mno-cygwin',
            #                     linker_so='%s --driver-name g++ -mno-cygwin -mdll -static %s' 
            #                                % (self.linker, entry_point))
            if self.gcc_version <= "3.0.0":
                self.set_executables(compiler='gcc -mno-cygwin -O2 -w',
                                     compiler_so='gcc -mno-cygwin -mdll -O2 -w -Wstrict-prototypes',
                                     linker_exe='g++ -mno-cygwin',
                                     linker_so='%s -mno-cygwin -mdll -static %s' 
                                                % (self.linker, entry_point))
            else:            
                self.set_executables(compiler='gcc -mno-cygwin -O2 -w',
                                     compiler_so='gcc -O2 -w -Wstrict-prototypes',
                                     linker_exe='g++ ',
                                     linker_so='g++ -shared')
            # added for python2.3 support
            # we can't pass it through set_executables because pre 2.2 would fail
            self.compiler_cxx = 'g++'
            
            # Maybe we should also append -mthreads, but then the finished
            # dlls need another dll (mingwm10.dll see Mingw32 docs)
            # (-mthreads: Support thread-safe exception handling on `Mingw32')       
            
            # no additional libraries needed 
            self.dll_libraries=[]
            
        # __init__ ()

        def link(self,
                 target_desc,
                 objects,
                 output_filename,
                 output_dir,
                 libraries,
                 library_dirs,
                 runtime_library_dirs,
                 export_symbols = None,
                 debug=0,
                 extra_preargs=None,
                 extra_postargs=None,
                 build_temp=None,
                 target_lang=None):
            if self.gcc_version < "3.0.0":
                distutils.cygwinccompiler.CygwinCCompiler.link(self,
                               target_desc,
                               objects,
                               output_filename,
                               output_dir,
                               libraries,
                               library_dirs,
                               runtime_library_dirs,
                               None, #export_symbols, we do this in our def-file
                               debug,
                               extra_preargs,
                               extra_postargs,
                               build_temp,
                               target_lang)
            else:
                UnixCCompiler.link(self,
                               target_desc,
                               objects,
                               output_filename,
                               output_dir,
                               libraries,
                               library_dirs,
                               runtime_library_dirs,
                               None, # export_symbols, we do this in our def-file
                               debug,
                               extra_preargs,
                               extra_postargs,
                               build_temp,
                               target_lang)

        def object_filenames (self,
                              source_filenames,
                              strip_dir=0,
                              output_dir=''):
            if output_dir is None: output_dir = ''
            print 'cygiwn_output_dir:', output_dir
            obj_names = []
            for src_name in source_filenames:
                # use normcase to make sure '.rc' is really '.rc' and not '.RC'
                (base, ext) = os.path.splitext (os.path.normcase(src_name))
                
                # added these lines to strip off windows drive letters
                # without it, .o files are placed next to .c files
                # instead of the build directory
                drv,base = os.path.splitdrive(base)
                if drv:
                    base = base[1:]
                
                if ext not in (self.src_extensions + ['.rc','.res']):
                    raise UnknownFileError, \
                          "unknown file type '%s' (from '%s')" % \
                          (ext, src_name)
                if strip_dir:
                    base = os.path.basename (base)
                if ext == '.res' or ext == '.rc':
                    # these need to be compiled to object files
                    obj_names.append (os.path.join (output_dir,
                                                base + ext + self.obj_extension))
                else:
                    print 'here', os.path.join (output_dir,
                                                base + self.obj_extension)
                    print '...:', output_dir, base + self.obj_extension                                            
                    obj_names.append (os.path.join (output_dir,
                                                base + self.obj_extension))
            return obj_names
    
        # object_filenames ()

        
    # On windows platforms, we want to default to mingw32 (gcc)
    # because msvc can't build blitz stuff.
    # We should also check the version of gcc available...
    #distutils.ccompiler._default_compilers['nt'] = 'mingw32'
    #distutils.ccompiler._default_compilers = (('nt', 'mingw32'))
    # reset the Mingw32 compiler in distutils to the one defined above
    distutils.cygwinccompiler.Mingw32CCompiler = Mingw32CCompiler
    
    def import_library_exists():
        """ on windows platforms, make sure a gcc import library exists
        """
        if os.name == 'nt':
            lib_name = "libpython%d%d.a" % tuple(sys.version_info[:2])
            full_path = os.path.join(sys.prefix,'libs',lib_name)
            if not os.path.exists(full_path):
                return 0
        return 1
    
    def build_import_library():
        """ Build the import libraries for Mingw32-gcc on Windows
        """
        from scipy_distutils import lib2def
        #libfile, deffile = parse_cmd()
        #if deffile is None:
        #    deffile = sys.stdout
        #else:
        #    deffile = open(deffile, 'w')
        lib_name = "python%d%d.lib" % tuple(sys.version_info[:2])    
        lib_file = os.path.join(sys.prefix,'libs',lib_name)
        def_name = "python%d%d.def" % tuple(sys.version_info[:2])    
        def_file = os.path.join(sys.prefix,'libs',def_name)
        nm_cmd = '%s %s' % (lib2def.DEFAULT_NM, lib_file)
        nm_output = lib2def.getnm(nm_cmd)
        dlist, flist = lib2def.parse_nm(nm_output)
        lib2def.output_def(dlist, flist, lib2def.DEF_HEADER, open(def_file, 'w'))
        
        out_name = "libpython%d%d.a" % tuple(sys.version_info[:2])
        out_file = os.path.join(sys.prefix,'libs',out_name)
        dll_name = "python%d%d.dll" % tuple(sys.version_info[:2])
        args = (dll_name,def_file,out_file)
        cmd = 'dlltool --dllname %s --def %s --output-lib %s' % args
        success = not os.system(cmd)
        # for now, fail silently
        if not success:
            print 'WARNING: failed to build import library for gcc. Linking will fail.'
        #if not success:
        #    msg = "Couldn't find import library, and failed to build it."
        #    raise DistutilsPlatformError, msg
