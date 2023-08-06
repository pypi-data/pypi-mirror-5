#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from sys import version_info
from setuptools import setup, find_packages

setup(
    name='weave-minimal',
    version='1.3',
    author='Martin Zimmermann',
    author_email='info@posativ.org',
    packages=find_packages(),
    zip_safe=True,
    url='https://github.com/posativ/weave-minimal/',
    license='BSD revised',
    description='lightweight firefox weave/sync server',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Topic :: Internet",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7"
    ],
    install_requires=['werkzeug>=0.%i' % (8 if version_info[0] == 2 else 9)],
    entry_points={
        'console_scripts':
            ['weave-minimal = weave:main'],
    },
)
