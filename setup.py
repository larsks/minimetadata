#!/usr/bin/env python
import setuptools

setuptools.setup(
    install_requires=open('requires.txt').readlines(),
    packages = ['minimetadata'],
    entry_points = {
        'console_scripts': [
            'minimetadata=minimetadata.main:main',
            ],
        }
)

