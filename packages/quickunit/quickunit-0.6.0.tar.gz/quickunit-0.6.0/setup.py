#!/usr/bin/env python

from setuptools import setup, find_packages

tests_require = [
    'nose',
    'unittest2',
]

setup(
    name='quickunit',
    version='0.6.0',
    author='David Cramer',
    author_email='dcramer@gmail.com',
    description='A discovery plugin for Nose which relies on sane structure.',
    url='http://github.com/dcramer/quickunit',
    packages=find_packages(exclude=["tests"]),
    zip_safe=False,
    install_requires=[
        'nose>=0.9',
    ],
    entry_points={
        'nose.plugins.0.10': [
            'quickunit = quickunit.plugin:QuickUnitPlugin'
        ],
        'console_scripts': [
            'quickunit-finder = quickunit.scripts.finder:main',
        ],
    },
    license='Apache License 2.0',
    tests_require=tests_require,
    extras_require={
        'tests': tests_require,
    },
    include_package_data=True,
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Topic :: Software Development'
    ],
)
