#!/usr/bin/env python
# -*- coding: utf8 -*-

from distutils.core import setup, Extension

cnfmodule = Extension(
    'satispy.cnf',
    sources = [
        'src/ext/cnf_module.c',
        'src/ext/cnf_cnf.c',
        'src/ext/cnf_variable.c'
    ]
)

setup(
    name='satispy',
    version='1.0a4',
    description='An interface to SAT solver tools (like minisat)',
    author='FÁBIÁN Tamás László',
    author_email='giganetom@gmail.com',
    url='https://github.com/netom/satispy/',
    download_url='https://github.com/netom/satispy/tarball/1.0a4#egg=satispy-1.0a4',
    license='BSD License',
    platforms='OS Independent',
    package_dir = {'': 'src/python'},
    packages=['satispy', 'satispy.io', 'satispy.solver'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Plugins',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Software Development :: Libraries'
    ],
    ext_modules = [cnfmodule]
)
