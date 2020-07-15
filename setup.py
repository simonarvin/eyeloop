#!/usr/bin/env python
from glob import glob
from os.path import join

from setuptools import setup, find_packages


install_requires = [
    'opencv-contrib-python>=4.2.*',
    'pymba==0.3.*',
    'numpy==1.19.*'
]

setup(
    name='eyeloop',
    description='EyeLoop is a Python 3-based eye-tracker tailored specifically to dynamic, '
                'closed-loop experiments on consumer-grade hardware.',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url='https://github.com/simonarvin/eyeloop',
    license='GPL',
    license_file='LICENSE',
    platforms='any',
    python_requires='>=3.7',
    version='0.1',
    entry_points={
        'console_scripts': [
            'eyeloop=eyeloop.run_eyeloop:EyeLoop'
        ]
    },
    packages=find_packages(include=["eyeloop.*"]),
    install_requires=install_requires,
    project_urls={
        "Documentation": "https://github.com/simonarvin/eyeloop",
        "Source": "https://github.com/simonarvin/eyeloop",
        "Tracker": "https://github.com/simonarvin/eyeloop/issues"
    }
)
