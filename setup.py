__version__ = '0.9'

import os
import sys

if sys.version_info[:2] < (2, 4):
    msg = ("Py65 requires Python 2.4 or better, you are attempting to "
           "install it using version %s.  Please install with a "
           "supported version" % sys.version)
    sys.stderr.write(msg)
    sys.exit(1)

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
    name = 'py65',
    version = __version__,
    license = 'License :: OSI Approved :: BSD License',
    url = 'http://github.com/mnaberez/py65',
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
        'CHANGES.txt',
        'LICENSE.txt',
        'README.markdown',
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
