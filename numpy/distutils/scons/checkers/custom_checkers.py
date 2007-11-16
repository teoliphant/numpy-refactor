#! /usr/bin/env python
# Last Change: Fri Nov 16 06:00 PM 2007 J

# Module for custom, common checkers for numpy (and scipy)
import sys
import os.path
from copy import deepcopy
from distutils.util import get_platform

from numpy.distutils.scons.core.libinfo import get_config_from_section, get_config
from numpy.distutils.scons.testcode_snippets import cblas_sgemm as cblas_src, \
        c_sgemm as sunperf_src, lapack_sgesv, blas_sgemm, c_sgemm2
from numpy.distutils.scons.fortran_scons import CheckF77Mangling, CheckF77Clib
from numpy.distutils.scons.configuration import add_info
from numpy.distutils.scons.core.utils import rsplit
from numpy.distutils.scons.core.extension_scons import built_with_mstools, built_with_mingw

from perflib import CheckMKL, CheckATLAS, CheckSunperf, CheckAccelerate
from support import check_include_and_run, ConfigOpts, ConfigRes

# XXX: many perlib can be used from both C and F (Atlas being a notable
# exception for LAPACK). So shall we make the difference between BLAS, CBLAS,
# LAPACK and CLAPACK ? How to test for fortran ?

def CheckCBLAS(context, autoadd = 1):
    """This checker tries to find optimized library for cblas.

    This test is pretty strong: it first detects an optimized library, and then
    tests that a simple cblas program can be run using this lib.
    
    It looks for the following libs:
        - Mac OS X: Accelerate, and then vecLib.
        - Others: MKL, then ATLAS, then Sunperf."""
    # XXX: rpath vs LD_LIBRARY_PATH ?
    env = context.env

    def check(func, name, suplibs):
        st, res = func(context, autoadd)
        if st:
            for lib in suplibs:
                res.cfgopts['libs'].insert(0, lib)
            st = check_include_and_run(context, 'CBLAS (%s)' % name, 
                                       res.cfgopts, [], cblas_src, autoadd)
            if st:
                add_info(env, 'cblas', res)
            return st

    # If section cblas is in site.cfg, use those options. Otherwise, use default
    section = "cblas"
    siteconfig, cfgfiles = get_config()
    (cpppath, libs, libpath), found = get_config_from_section(siteconfig, section)
    if found:
        cfg = ConfigOpts(cpppath = cpppath, libs = libs, libpath = libpath,
                         rpath = libpath)
        st = check_include_and_run(context, 'CBLAS (from site.cfg) ', cfg,
                                  [], cblas_src, autoadd)
        if st:
            add_info(env, 'cblas', ConfigRes('cblas', cfg, found))
        return st
    else:
        if sys.platform == 'darwin':
            # Check Accelerate
            st = check(CheckAccelerate, 'Accelerate Framework', [])
            if st:
                return st

            st = check(CheckVeclib, 'vecLib Framework', [])
            if st:
                return st

            add_info(env, 'cblas', 'Def numpy implementation used')
            return 0
            
        else:
            # XXX: think about how to share headers info between checkers ?

            # Check MKL
            st = check(CheckMKL, 'MKL', [])
            if st:
                return st

            # Check ATLAS
            st = check(CheckATLAS, 'ATLAS', ['blas'])
            if st:
                return st

            # Check Sunperf
            st = check(CheckSunperf, 'Sunperf', [])
            if st:
                return st

            add_info(env, 'cblas', 'Def numpy implementation used')
            return 0

def CheckF77BLAS(context, autoadd = 1):
    """This checker tries to find optimized library for blas (fortran F77).

    This test is pretty strong: it first detects an optimized library, and then
    tests that a simple blas program (in C) can be run using this (F77) lib.
    
    It looks for the following libs:
        - Mac OS X: Accelerate, and then vecLib.
        - Others: MKL, then ATLAS, then Sunperf."""
    # XXX: rpath vs LD_LIBRARY_PATH ?
    env = context.env

    # Get Fortran things we need
    if not env.has_key('F77_NAME_MANGLER'):
        if not CheckF77Mangling(context):
            return 0
    func_name = env['F77_NAME_MANGLER']('sgemm')
    test_src = c_sgemm2 % {'func' : func_name}

    def check(func, name, suplibs):
        st, res = func(context, autoadd)
        if st:
            for lib in suplibs:
                res.cfgopts['libs'].insert(0, lib)
            st = check_include_and_run(context, 'BLAS (%s)' % name, res.cfgopts,
                    [], test_src, autoadd)
            if st:
                add_info(env, 'blas', res)
            return st

    # If section blas is in site.cfg, use those options. Otherwise, use default
    section = "blas"
    siteconfig, cfgfiles = get_config()
    (cpppath, libs, libpath), found = get_config_from_section(siteconfig, section)
    if found:
        cfg = ConfigOpts(cpppath = cpppath, libs = libs, libpath = libpath,
                         rpath = libpath)
        st = check_include_and_run(context, 'BLAS (from site.cfg) ', cfg,
                                  [], test_src, autoadd)
        if st:
            add_info(env, 'blas', ConfigRes('blas', cfg, found))
        return st
    else:
        if sys.platform == 'darwin':
            # Check Accelerate
            st = check(CheckAccelerate, 'Accelerate Framework', [])
            if st:
                return st

            st = check(CheckVeclib, 'vecLib Framework', [])
            if st:
                return st
        else:
            # Check MKL
            st = check(CheckMKL, 'MKL', [])
            if st:
                return st

            # Check ATLAS
            st = check(CheckATLAS, 'ATLAS', ['f77blas'])
            if st:
                return st

            # Check Sunperf
            st = check(CheckSunperf, 'Sunperf', [])
            if st:
                return st

    # XXX: Use default values for blas

    return 0

def CheckF77LAPACK(context, autoadd = 1):
    """This checker tries to find optimized library for F77 lapack.

    This test is pretty strong: it first detects an optimized library, and then
    tests that a simple (C) program can be run using this (F77) lib.
    
    It looks for the following libs:
        - Mac OS X: Accelerate, and then vecLib.
        - Others: MKL, then ATLAS."""
    env = context.env

    if not env.has_key('F77_NAME_MANGLER'):
        if not CheckF77Mangling(context):
            add_info(env, 'lapack', 'Def numpy implementation used')
            return 0
    
    # Get the mangled name of our test function
    sgesv_string = env['F77_NAME_MANGLER']('sgesv')
    test_src = lapack_sgesv % sgesv_string

    def check(func, name, suplibs):
        st, res = func(context, autoadd)
        if st:
            for lib in suplibs:
                res.cfgopts['libs'].insert(0, lib)
            st = check_include_and_run(context, 'LAPACK (%s)' % name, res.cfgopts,
                                       [], test_src, autoadd)
            if st:
                add_info(env, 'lapack', res)
            return st

    # If section lapack is in site.cfg, use those options. Otherwise, use default
    section = "lapack"
    siteconfig, cfgfiles = get_config()
    (cpppath, libs, libpath), found = get_config_from_section(siteconfig, section)
    if found:
        # XXX: handle def library names correctly
        if len(libs) == 1 and len(libs[0]) == 0:
            libs = ['lapack', 'blas']
        cfg = ConfigOpts(cpppath = cpppath, libs = libs, libpath = libpath,
                         rpath = deepcopy(libpath))

        # fortrancfg is used to merge info from fortran checks and site.cfg
        fortrancfg = deepcopy(cfg)
        fortrancfg['linkflags'].extend(env['F77_LDFLAGS'])

        st = check_include_and_run(context, 'LAPACK (from site.cfg) ', fortrancfg,
                                  [], test_src, autoadd)
        if st:
            add_info(env, 'lapack', ConfigRes('lapack', cfg, found))
        return st
    else:
        if sys.platform == 'darwin':
            st = check(CheckAccelerate, 'Accelerate Framework', [])
            if st:
                return st

            st = check(CheckVeclib, 'vecLib Framework', [])
            if st:
                return st

            add_info(env, 'lapack: def numpy implementation', opts)
            return 0
        else:
            # Check MKL
            # XXX: handle different versions of mkl (with different names)
            st = check(CheckMKL, 'MKL', ['lapack'])
            if st:
                return st

            # Check ATLAS
            st = check(CheckATLAS, 'ATLAS', ['lapack'])
            if st:
                return st

            # Check Sunperf
            st = check(CheckSunperf, 'Sunperf', ['lapack'])
            if st:
                return st

    add_info(env, 'lapack', 'Def numpy implementation used')
    return 0

def CheckCLAPACK(context, autoadd = 1):
    """This checker tries to find optimized library for lapack.

    This test is pretty strong: it first detects an optimized library, and then
    tests that a simple cblas program can be run using this lib.
    
    It looks for the following libs:
        - Mac OS X: Accelerate, and then vecLib.
        - Others: MKL, then ATLAS."""
    context.Message('Checking CLAPACK ...')
    context.Result('FIXME: not implemented yet')
    return 0
    env = context.env

    # If section lapack is in site.cfg, use those options. Otherwise, use default
    section = "lapack"
    siteconfig, cfgfiles = get_config()
    (cpppath, libs, libpath), found = get_config_from_section(siteconfig, section)
    if found:
        # XXX: handle def library names correctly
        if len(libs) == 1 and len(libs[0]) == 0:
            libs = ['lapack', 'blas']
        cfg = ConfigOpts(cpppath = cpppath, libs = libs, libpath = libpath,
                         rpath = deepcopy(libpath))

        # XXX: How to know whether we need fortran or not
        # ?
        if not env.has_key('F77_NAME_MANGLER'):
            if not CheckF77Mangling(context):
                return 0
        if not env.has_key('F77_LDFLAGS'):
            if not CheckF77Clib(context):
                return 0

        # Get the mangled name of our test function
        sgesv_string = env['F77_NAME_MANGLER']('sgesv')
        test_src = lapack_sgesv % sgesv_string

        # fortrancfg is used to merge info from fortran checks and site.cfg
        fortrancfg = deepcopy(cfg)
        fortrancfg['linkflags'].extend(env['F77_LDFLAGS'])

        st = check_include_and_run(context, 'LAPACK (from site.cfg) ', fortrancfg,
                                  [], test_src, autoadd)
        if st:
            add_info(env, 'lapack', ConfigRes('lapack', cfg, found))
        return st
    else:
        if sys.platform == 'darwin':
            st, opts = CheckAccelerate(context, autoadd)
            if st:
                if st:
                    add_info(env, 'lapack: Accelerate', opts)
                return st
            st, opts = CheckAccelerate(context, autoadd)
            if st:
                if st:
                    add_info(env, 'lapack: vecLib', opts)
                return st

        else:
            # Get fortran stuff (See XXX at the top on F77 vs C)
            if not env.has_key('F77_NAME_MANGLER'):
                if not CheckF77Mangling(context):
		    add_info(env, 'lapack', 'Def numpy implementation used')
                    return 0
            if not env.has_key('F77_LDFLAGS'):
                if not CheckF77Clib(context):
		    add_info(env, 'lapack', 'Def numpy implementation used')
                    return 0

            # Get the mangled name of our test function
            sgesv_string = env['F77_NAME_MANGLER']('sgesv')
            test_src = lapack_sgesv % sgesv_string

            # Check MKL
            st, res = CheckMKL(context, autoadd)
            if st:
                # Intel recommends linking lapack before mkl, guide and co
                res.cfgopts['libs'].insert(0, 'lapack')
                st = check_include_and_run(context, 'LAPACK (MKL)', res.cfgopts,
                                           [], test_src, autoadd)
                if st:
                    add_info(env, 'lapack', res)
                return st

            # Check ATLAS
            st, res = CheckATLAS(context, autoadd = 1)
            if st:
                res.cfgopts['libs'].insert(0, 'lapack')
                st = check_include_and_run(context, 'LAPACK (ATLAS)', res.cfgopts,
                                           [], test_src, autoadd)
                if st:
                    add_info(env, 'lapack', res)
                # XXX: Check complete LAPACK or not. (Checking for not
                # implemented lapack symbols ?)
                return st

            # Check Sunperf
            st, res = CheckSunperf(context, autoadd)
            if st:
                st = check_include_and_run(context, 'LAPACK (Sunperf)', res.cfgopts,
                                           [], test_src, autoadd)
                if st:
                    add_info(env, 'lapack', res)
                return st

    add_info(env, 'lapack', 'Def numpy implementation used')
    return 0
