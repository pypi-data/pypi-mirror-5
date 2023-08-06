#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Manuel Guenther <Manuel.Guenther@idiap.ch>
# Tue Apr 24 18:55:40 CEST 2012

# This file contains the python (distutils/setuptools) instructions so your
# package can be installed on **any** host system. It defines some basic
# information like the package name for instance, or its homepage.
#
# It also defines which other packages this python package depends on and that
# are required for this package's operation. The python subsystem will make
# sure all dependent packages are installed or will install them for you upon
# the installation of this package.
#
# The 'buildout' system we use here will go further and wrap this package in
# such a way to create an isolated python working environment. Buildout will
# make sure that dependencies which are not yet installed do get installed, but
# **without** requiring administrative privileges on the host system. This
# allows you to test your package with new python dependencies w/o requiring
# administrative interventions.

from setuptools import setup, find_packages

# The only thing we do in this file is to call the setup() function with all
# parameters that define our package.
setup(

    # This is the basic information about your project. Modify all this
    # information before releasing code publicly.
    name='bob.example.faceverify',
    version='0.4.2',
    description='Example for using Bob to create face verification systems',
    url='http://pypi.python.org/pypi/bob.example.faceverify',
    license='GPLv3',
    author='Manuel Guenther',
    author_email='manuel.guenther@idiap.ch',

    long_description=open('README.rst').read(),

    # This line is required for any distutils based packaging.
    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,

    # This line defines which packages should be installed when you "install"
    # this package. All packages that are mentioned here, but are not installed
    # on the current system will be installed locally and only visible to the
    # scripts of this package. Don't worry - You won't need administrative
    # privileges when using buildout.

    install_requires=[
        "setuptools",
        "bob >= 1.2.0a0",               # base signal proc./machine learning library
        "xbob.db.atnt",               # the AT&T (ORL) database of images
    ],

    # This entry defines which scripts you will have inside the 'bin' directory
    # once you install the package (or run 'bin/buildout'). The order of each
    # entry under 'console_scripts' is like this:
    #   script-name-at-bin-directory = module.at.your.library:function
    entry_points={
      'console_scripts': [
        'eigenface.py = faceverify.eigenface:main',
        'gabor_graph.py = faceverify.gabor_graph:main',
        'dct_ubm.py = faceverify.dct_ubm:main'
        ],

       # bob unittest declaration
      'bob.test': [
        'faceverify = faceverify.tests:FaceVerifyExampleTest',
        ],
     },

)
