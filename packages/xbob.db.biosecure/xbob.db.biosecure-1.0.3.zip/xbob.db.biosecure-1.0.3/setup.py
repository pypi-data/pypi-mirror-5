#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Laurent El Shafey <laurent.el-shafey@idiap.ch>

from setuptools import setup, find_packages

# The only thing we do in this file is to call the setup() function with all
# parameters that define our package.
setup(

    name='xbob.db.biosecure',
    version='1.0.3',
    description='Biosecure Database Access API for Bob',
    url='http://github.com/bioidiap/xbob.db.biosecure',
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
      'xbob.db.verification.utils>=0.1.4' # defines a set of utilities for face verification databases like this one.
      ],

    namespace_packages = [
      'xbob',
      'xbob.db',
      ],

    entry_points = {
      # bob database declaration
      'bob.db': [
        'biosecure = xbob.db.biosecure.driver:Interface',
        ],

      # bob unittest declaration
      'bob.test': [
        'biosecure = xbob.db.biosecure.test:BiosecureDatabaseTest',
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
