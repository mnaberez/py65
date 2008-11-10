__revision__ = '$Id$'

import urllib
import urllib2
if not hasattr(urllib2, 'splituser'):
    # setuptools wants to import this from urllib2 but it's not
    # in there in Python 2.3.3, so we just alias it.
    urllib2.splituser = urllib.splituser

from ez_setup import use_setuptools
use_setuptools()

import os
import sys
import string

version, extra = string.split(sys.version, ' ', 1)
maj, minor = string.split(version, '.', 1)

if not maj[0] >= '2' and minor[0] >= '3':
    msg = ("Py65 requires Python 2.3 or better, you are attempting to "
           "install it using version %s.  Please install with a "
           "supported version" % version)

from setuptools import setup, find_packages
here = os.path.abspath(os.path.normpath(os.path.dirname(__file__)))

DESC = """\
Py65 is a simulation of the original NMOS 6502 microprocessor 
from MOS Technology, written in Python. """

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
    url = '',
    download_url = '',
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
        'README.txt',
        'TODO.txt',
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
