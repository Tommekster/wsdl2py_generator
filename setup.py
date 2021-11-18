#!/usr/bin/env python

from distutils.core import setup

setup(
    name='wsdl2py generator',
    version='0.1',
    license="MIT",
    description='Python classes generator from WSDL',
    author='Tomas Zikmund',
    author_email='python@tomaszikmund.eu',
    url='https://github.com/tommekster/',
    packages=['wsdl2py_generator'],
    install_requires=[
        "zeep>=4.1.0"
    ],
)
