#!/usr/bin/env python

from distutils.core import setup

setup(
    name='Pyjector',
    version='0.1.2',
    description='Control your projector over a serial port',
    author='John Brodie',
    author_email='john@brodie.me',
    url='http://www.github.com/JohnBrodie/pyjector',
    packages=['pyjector'],
    requires=[
        'pyserial',
    ]
)
