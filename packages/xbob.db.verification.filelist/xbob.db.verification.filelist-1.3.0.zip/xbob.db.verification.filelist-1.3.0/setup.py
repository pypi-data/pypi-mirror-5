#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Laurent El Shafey <laurent.el-shafey@idiap.ch>
# modified by Elie Khoury <elie.khoury@idiap.ch>

from setuptools import setup, find_packages

# The only thing we do in this file is to call the setup() function with all
# parameters that define our package.
setup(

    name='xbob.db.verification.filelist',
    version='1.3.0',
    description='Verification File List Database Access API for Bob',
    url='http://github.com/bioidiap/xbob.db.verification.filelist',
    license='GPLv3',
    author='Laurent El Shafey',
    author_email='laurent.el-shafey@idiap.ch',
    long_description=open('README.rst').read(),

    # This line is required for any distutils based packaging.
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,

    install_requires=[
      'setuptools',
      'bob',  # base signal proc./machine learning library
      'xbob.db.verification.utils' # defines a set of utilities for face verification databases like this one.
    ],

    namespace_packages = [
      'xbob',
      'xbob.db',
      'xbob.db.verification'
      ],

    entry_points={

      # declare database to bob
      'bob.db': [
        'filelist = xbob.db.verification.filelist.driver:Interface',
        ],

      # declare tests to bob
      'bob.test': [
        'filelist = xbob.db.verification.filelist.test:Verification_fileList_DatabaseTest',
        ],

      },

    classifiers = [
      'Development Status :: 4 - Beta',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
      'Natural Language :: English',
      'Programming Language :: Python',
      'Topic :: Scientific/Engineering :: Artificial Intelligence',
      'Topic :: Database :: Front-Ends',
      ],
)
