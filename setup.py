#!/usr/bin/env python
import setuptools

setuptools.setup(
    name='minimetadata',
    install_requires=open('requires.txt').readlines(),
    packages = ['minimetadata'],
    entry_points = {
        'console_scripts': [
            'minimetadata=minimetadata.main:main',
            ],
        }
)

