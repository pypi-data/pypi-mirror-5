import os, sys, shutil
from setuptools import find_packages
from distutils.core import setup
from distutils.extension import Extension

# Set this to True to enable building extensions using Cython.
# Set it to False to build extensions from the C file (that
# was previously created using Cython).
# Set it to 'auto' to build with Cython if available, otherwise
# from the C file.
USE_CYTHON = False


#if USE_CYTHON:
try:
    from Cython.Distutils import build_ext
except ImportError:
    if USE_CYTHON=='auto':
        USE_CYTHON=False
    else:
        raise
#try:
#    from Cython.Distutils import build_ext
    #use_cython = True
#except ImportError:
    #from distutils.command import build_ext
#    use_cython = False

cmdclass = { }
ext_modules = [ ]

if USE_CYTHON:
    ext_modules += [
        Extension("commpy.channelcoding.acstb", [ "commpy/channelcoding/acstb.pyx" ]),
        Extension("commpy.channelcoding.map_c", [ "commpy/channelcoding/map_c.pyx" ])
    ]
    cmdclass.update({ 'build_ext': build_ext })
    #print "Using Cython"
else:
    ext_modules += [
        Extension("commpy.channelcoding.acstb", [ "commpy/channelcoding/acstb.c" ]),
        Extension("commpy.channelcoding.map_c", [ "commpy/channelcoding/map_c.c" ])
    ]

# Taken from scikit-learn setup.py
DISTNAME = 'scikit-commpy'
DESCRIPTION = 'Digital Communication Algorithms with Python'
LONG_DESCRIPTION = open('README').read()
MAINTAINER = 'Veeresh Taranalli'
MAINTAINER_EMAIL = 'veeresht@gmail.com'
URL = 'http://veeresht.github.com/CommPy'
LICENSE = 'GPL'
# DOWNLOAD_URL = 'http://sourceforge.net/projects/scikit-learn/files/'
VERSION = '0.2.0'

#This is a list of files to install, and where
#(relative to the 'root' dir, where setup.py is)
#You could be more specific.
files = ["channelcoding/*, channelcoding/tests/*"]

setup(
    name = DISTNAME,
    maintainer=MAINTAINER,
    maintainer_email=MAINTAINER_EMAIL,
    description=DESCRIPTION,
    license=LICENSE,
    url=URL,
    version=VERSION,
    #Name the folder where your packages live:
    #(If you have other packages (dirs) or modules (py files) then
    #put them into the package directory - they will be found 
    #recursively.)
    packages = ['commpy', 'commpy.channelcoding', 'commpy.channelcoding.tests'],
    #package_dir={
    #    'commpy' : 'commpy',
    #},
    install_requires=[
          'numpy',
          'scipy',
          'matplotlib',
          'cython',
    ],
       #'package' package must contain files (see list above)
    #This dict maps the package name =to=> directories
    #It says, package *needs* these files.
    package_data = {'commpy' : files },
    #'runner' is in the root.
    scripts = ["runner"],
    cmdclass = cmdclass,
    ext_modules = ext_modules,
    test_suite='nose.collector',
    tests_require=['nose'],

    long_description = """ Work in progress """, 
    classifiers = [
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Telecommunications Industry',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development',
    ]
)
