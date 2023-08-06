# -*- coding: utf-8 -*-
from distutils.core import setup

setup(
    name='clg',
    version='0.1',
    author='François Ménabé',
    author_email='francois.menabe@gmail.com',
    py_modules=['clg'],
    license='LICENCE.txt',
    description='Command line generator from a dictionnary.',
    long_description=open('README').read(),
    install_requires=[
        'argparse',
    ]
)
