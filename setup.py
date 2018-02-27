#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('CHANGELOG.rst') as change_log_file:
    change_log = change_log_file.read()

requirements = ['Click>=6.0', ]

setup_requirements = ['pytest-runner', ]

test_requirements = ['pytest', ]

setup(
    author='William Jamir Silva',
    author_email='william@esss.co',
    maintainer='William Jamir Silva',
    maintainer_email='william@esss.co',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    description="Facilitate moving python modules across project by rewriting import statements "
                "using google-pasta",
    entry_points={
        'console_scripts': [
            'renamer=module_renamer.cli:main',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + change_log,
    include_package_data=True,
    keywords='module_renamer',
    name='module_renamer',
    packages=find_packages(include=['module_renamer']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/ESSS/module_renamer',
    version='0.1.0',
    zip_safe=False,
)
