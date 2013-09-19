#!/usr/bin/env python
import setuptools

setuptools.setup(
#    install_requires=open('requires.txt').readlines(),
    packages = ['minimetadata'],
    install_requires = open('requires.txt').readlines(),
    entry_points = {
        'console_scripts': [
            'minimetadata=minimetadata.main:main',
            ],
        }
)

