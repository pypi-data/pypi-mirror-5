#!/usr/bin/env python

from setuptools import setup
from diff_cover import VERSION, DESCRIPTION
 
REQUIREMENTS = [line.strip() for line in 
                open("requirements.txt").readlines()]

setup(
    name='diff_cover',
    version=VERSION,
    author='edX',
    url='http://github.com/edx/diff-cover',
    description=DESCRIPTION,
    license='AGPL',
    classifiers=['Development Status :: 3 - Alpha',
                 'Environment :: Console',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: GNU Affero General Public License v3',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python',
                 'Topic :: Software Development :: Testing',
                 'Topic :: Software Development :: Quality Assurance'],
    packages=['diff_cover'],
    install_requires=['setuptools'] + REQUIREMENTS,
    entry_points={
        'console_scripts': ['diff-cover = diff_cover.tool:main']
    }
)
