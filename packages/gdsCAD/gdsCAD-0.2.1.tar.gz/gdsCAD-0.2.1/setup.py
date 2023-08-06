# -*- coding: utf-8 -*-

from distutils.core import setup

setup(
    name='gdsCAD',
    version='0.2.1',
    author='Andrew G. Mark',
    author_email='mark@is.mpg.de',
    packages=['gdsCAD'],
#    scripts=['bin/stowe-towels.py','bin/wash-towels.py'],
    url='https://pypi.python.org/pypi/gdsCAD',
    license='LICENSE.txt',
    description='A simple Python package for creating or reading GDSII layout files.',
    long_description=open('README.txt').read(),
)