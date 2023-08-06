#!/usr/bin/env python
import os
import sys

import image_slicer

from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

requires = ['Pillow']

setup(
    name='image_slicer',
    version=image_slicer.__version__,
    description='Cut images into tiles and reassemble them..',
    long_description=open('README.rst').read() + '\n\n' +
                     open('HISTORY.rst').read(),
    author='Sam Dobson',
    author_email='sjd333@gmail.com',
    url='http://python-image-slicer.net',
    install_requires=requires,
    packages=['image_slicer', 'image_slicer.tests'],
    license=open('LICENSE').read(),
    zip_safe=False,
    scripts=['bin/slice-image', 'bin/join-tiles'],
    tests_require=['nose'],
    classifiers=(
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Natural Language :: English',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
    ),
)

