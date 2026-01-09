#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup script for Chandojñānam.

This file is kept for backwards compatibility.
The main configuration is in pyproject.toml.
"""

from setuptools import setup, find_packages
import os

# Read the long description from README
def read_long_description():
    here = os.path.abspath(os.path.dirname(__file__))
    readme_path = os.path.join(here, 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, encoding='utf-8') as f:
            return f.read()
    return ''

setup(
    name='chanda',
    version='0.1.1',
    description='Sanskrit meter identification and analysis library',
    long_description=read_long_description(),
    long_description_content_type='text/markdown',
    author='Hrishikesh Terdalkar',
    author_email='hrishikeshrt@proton.me',
    url='https://github.com/hrishikeshrt/chanda',
    license='AGPL-3.0-or-later',
    packages=find_packages(exclude=['tests', 'experiments', 'static', 'templates']),
    package_data={
        'chanda': ['data/*.csv', 'data/*.json'],
    },
    include_package_data=True,
    install_requires=[
        'python-Levenshtein>=0.12.2',
        'indic-transliteration>=2.3.10',
        'sanskrit-text>=0.2.1',
    ],
    extras_require={
        'dev': [
            'pytest>=7.0',
            'pytest-cov>=3.0',
            'black>=22.0',
            'flake8>=4.0',
            'mypy>=0.950',
        ],
        'docs': [
            'sphinx>=4.0',
            'sphinx-rtd-theme>=1.0',
            'sphinx-autodoc-typehints>=1.18',
        ],
        'webapp': [
            'Flask>=2.2.2',
            'Flask-Uploads>=0.2.1',
            'pytesseract>=0.3.9',
            'google-drive-ocr>=0.2.6',
        ],
    },
    entry_points={
        'console_scripts': [
            'chanda=chanda.cli:main',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Text Processing :: Linguistic',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='sanskrit prosody meter chanda poetry linguistics nlp digital-humanities',
    python_requires='>=3.8',
    project_urls={
        'Documentation': 'https://chanda.readthedocs.io',
        'Source': 'https://github.com/hrishikeshrt/chanda',
        'Bug Reports': 'https://github.com/hrishikeshrt/chanda/issues',
    },
)
