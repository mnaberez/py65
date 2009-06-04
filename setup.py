__revision__ = '$Id$'

from ez_setup import use_setuptools
use_setuptools()

import os
import sys
import string

version, extra = string.split(sys.version, ' ', 1)
maj, minor = string.split(version, '.', 1)

if not maj[0] >= '2' and minor[0] >= '4':
    msg = ("Py65 requires Python 2.4 or better, you are attempting to "
           "install it using version %s.  Please install with a "
           "supported version" % version)

from setuptools import setup, find_packages
here = os.path.abspath(os.path.normpath(os.path.dirname(__file__)))

DESC = """\
Simulate 6502-based microcomputer systems in Python."""

CLASSIFIERS = [
    'Development Status :: 3 - Alpha',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'Natural Language :: English',
    'Operating System :: POSIX',
    'Programming Language :: Assembly',
    'Topic :: Software Development :: Assemblers',
    'Topic :: Software Development :: Disassemblers',
    'Topic :: Software Development :: Debuggers',
    'Topic :: Software Development :: Embedded Systems',
    'Topic :: Software Development :: Interpreters',
    'Topic :: System :: Emulators',
    'Topic :: System :: Hardware'
    ]

version_txt = os.path.join(here, 'src/py65/version.txt')
py65_version = open(version_txt).read().strip()

dist = setup(
    name = 'py65',
    version = py65_version,
    license = 'License :: OSI Approved :: BSD License',
    url = 'http://github.com/mnaberez/py65',
    download_url = 'http://github.com/mnaberez/py65/downloads',
    description = '6502 microprocessor simulation package',
    long_description= DESC,
    classifiers = CLASSIFIERS,
    author = "Mike Naberezny",
    author_email = "mike@naberezny.com",
    maintainer = "Mike Naberezny",
    maintainer_email = "mike@naberezny.com",
    package_dir = {'':'src'},
    packages = find_packages(os.path.join(here, 'src')),
    # put data files in egg 'doc' dir
    data_files=[ ('doc', [
        'CHANGES',
        'README.markdown',
        'TODO',
        ]
    )],
    install_requires = [],
    extras_require = {},
    tests_require = [],
    include_package_data = True,
    zip_safe = False,
    namespace_packages = ['py65'],
    test_suite = "py65.tests",
    entry_points = {
     'console_scripts': [
         'py65mon = py65.monitor:main',
         ],
      },
)
