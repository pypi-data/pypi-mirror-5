#! /usr/bin/python
# -*- coding: utf-8 -*-
from setuptools import setup
import os.path

setup(name='pyblue',
      version='1.0.4',
      description='PyBlue',
      author='Nicolas Vanhoren, Istvan Albert',
      author_email='nicolas.vanhoren@unknown.com, istvan.albert@gmail.com',
      url='https://github.com/ialbert/pyblue',
      py_modules = ['pyblue', "utils"],
      packages=['bio'],
      scripts=["pyblue"],
      include_package_data = True,
      data_files=[
          ('./templates/', [
              'templates/extensions.mako',
              'templates/base.boot.mako',
              'templates/base.md.mako',
          ]),
        ],
      long_description="A bioinformatics oriented micro web framework/static web site generator based on PyGreen.",
      keywords="",
      license="MIT",
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Environment :: Web Environment',
          'Intended Audience :: End Users/Desktop',
          'Intended Audience :: Developers',
          'Intended Audience :: Education',
          'License :: OSI Approved :: MIT License',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX',
          'Programming Language :: Python :: 2.6',
          'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
          'Topic :: Scientific/Engineering :: Bio-Informatics',
          ],
      install_requires=[
        "bottle >= 0.11.6",
        "mako >= 0.8.0",
        "argparse",
        "markdown",
        "waitress",
        ],
     )

