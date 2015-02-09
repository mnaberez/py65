__version__ = '0.21'

import os
import sys

py_version = sys.version_info[:2]
PY3 = py_version[0] == 3

if PY3:
    if py_version < (3, 2):
        raise RuntimeError('On Python 3, Py65 requires Python 3.2 or later')
else:
    if py_version < (2, 6):
        raise RuntimeError('On Python 2, Py65 requires Python 2.6 or later')

from setuptools import setup, find_packages
here = os.path.abspath(os.path.dirname(__file__))

DESC = """\
Simulate 6502-based microcomputer systems in Python."""

CLASSIFIERS = [
    'Development Status :: 3 - Alpha',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'Natural Language :: English',
    'Operating System :: POSIX',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.2',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Assembly',
    'Topic :: Software Development :: Assemblers',
    'Topic :: Software Development :: Disassemblers',
    'Topic :: Software Development :: Debuggers',
    'Topic :: Software Development :: Embedded Systems',
    'Topic :: Software Development :: Interpreters',
    'Topic :: System :: Emulators',
    'Topic :: System :: Hardware'
]

setup(
    name='py65',
    version=__version__,
    license='License :: OSI Approved :: BSD License',
    url='https://github.com/mnaberez/py65',
    description='6502 microprocessor simulation package',
    long_description=DESC,
    classifiers=CLASSIFIERS,
    author="Mike Naberezny",
    author_email="mike@naberezny.com",
    maintainer="Mike Naberezny",
    maintainer_email="mike@naberezny.com",
    packages=find_packages(),
    install_requires=[],
    extras_require={},
    tests_require=[],
    include_package_data=True,
    zip_safe=False,
    namespace_packages=['py65'],
    test_suite="py65.tests",
    entry_points={
        'console_scripts': [
            'py65mon = py65.monitor:main',
        ],
    },
)
