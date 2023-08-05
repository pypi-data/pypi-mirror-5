#!/usr/bin/python2.6
"""Setup file for r53."""

__author__ = 'cooper bethea'
__author_email__ = 'cooper.bethea@gmail.com'

from setuptools import setup

setup(
    name='r53',
    version='0.2',
    description='Command line script to synchronize Amazon Route53 DNS data.',
    package_dir={'': 'src'},
    packages=['r53'],
    install_requires=[
        'boto',
        'lxml',
        'argparse',
        ],
    entry_points={
        'console_scripts': [
            'r53 = r53.r53:main',
            ],
        },
    zip_safe=False,
    )
