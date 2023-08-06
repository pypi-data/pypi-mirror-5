#!/usr/bin/env python
# Setup script for oBB.
from setuptools import setup, Extension
from sys import version_info, exit
from numpy import get_include

# Make sure the correct version of Python is installed.
if (version_info[:2] < (2,6))or(version_info[0] == 3):
    print "oBB requires Python 2.6 to 2.7. Python %d.%d detected" % \
          version_info[:2]
    exit(-1)

# Get package version
exec(open('obb/version.py').read())

# Setup QuadProg++ Extension
ext_modules = [Extension('PyQuadProg',
                          sources=['pyquadprog/PyQuadProg.cpp','quadprog/QuadProg++.cc','quadprog/Array.cc'],
			  include_dirs=['pyquadprog','quadprog',get_include()],
			  language='c++'
			  )]

# Setup package
setup(
    name='oBB',
    version=__version__ ,
    description='Parallel global optimization of Hessian Lipschitz continuous functions.',
    author='J. Fowkes',
    author_email='jaroslav.fowkes@ed.ac.uk',
    packages=['obb', 'obb.test'],
    scripts=['bin/sins.sh','bin/sins.py','bin/sins_rbf.sh','bin/sins_rbf.py','bin/coconut.sh','bin/coconut.py'],
    include_package_data=True,
    package_data={'obb': ['obb/coconut/*','obb/coconut_tol']},
    ext_modules=ext_modules,
    url='http://pypi.python.org/pypi/oBB/',
    license='LGPLv2',
    long_description=open('README.txt').read(),
    install_requires=[
        "numpy >= 1.3.0",
        "mpi4py >= 1.3",
        "cvxopt >= 1.1.3",
        #"matplotlib >= 1.1.0",
    ],
    classifiers=[
	"Development Status :: 3 - Alpha",
	"Intended Audience :: Science/Research",
	"License :: OSI Approved :: GNU Lesser General Public License v2 (LGPLv2)",
	"Natural Language :: English",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 2.6", 	
	"Topic :: Scientific/Engineering :: Mathematics",
    ],
    zip_safe=False)
    
