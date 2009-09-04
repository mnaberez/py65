# Py65

Py65 provides tools for simulating hardware based on 6502-like
microprocessors.  It has the following goals:

 - Focus on ease of use and modularity rather than performance.  Py65 is
   written in the Python programming language for productivity, while
   similar programs are written in C for performance.

 - Enable simulations to be created for systems where it might have 
   otherwise not been practical, such as homebuilt computers. 

 - Rigorously unit test all of the components.  While the tools provided
   by Py65 may not always be perfect, their behavior is verified through 
   tests so unexpected results are minimized.
   
## Installation
                          
Py65 packages are [available](http://pypi.python.org/pypi/py65) on the 
Python Package Index (PyPI).  You download them from there or you can 
use `easy_install` to automatically install or upgrade Py65:

    $ easy_install -U py65

Alternatively, you can [download](http://github.com/mnaberez/py65/downloads) 
a package from GitHub in `.tar.gz` or `.zip` format.  After extracting the 
package, use the following command to install Py65:

    $ python setup.py install

## Devices

The following devices are simulated at this time:

 - `mpu6502` simulates the original NMOS 6502 microprocessor from MOS
    Technology, later known as Commodore Semiconductor Group (CSG). At this
    time, all of the documented opcodes are supported.  Support for the
    illegal opcodes is planned for the future.

 - `mpu65c02` simulates a generic CMOS 65C02 microprocessor. There were
    several 65C02 versions from various manufacturers, some with more opcodes
    than others. This simulation is based on the W65C02S from the Western
    Design Center (WDC).

## Monitor

Py65 includes a console-based machine language monitor (sometimes also called
a debugger).  This program, `py65mon`, allows you to interact with the
simulations that you build.  Its features include:

 - Commands that are largely compatible with those used in the monitor of
   the popular VICE emulator for Commodore computers.

 - Ability to load, dump, and fill memory.

 - Simple assemble and disassemble capability, including support for labels 
   and labels with offsets.

## Documentation

Py65 documentation is written using [Sphinx](http://sphinx.pocoo.org/) and is
periodically published to 
[http://6502.org/projects/py65/](http://6502.org/projects/py65/).

## Contributors

These people are responsible for Py65:

 - [Mike Naberezny](http://github.com/mnaberez) is the original author of 
   Py65 and is the primary maintainer.
 
 - [Oscar Lindberg](http://github.com/offe) started the 65C02 simulation 
   module and contributed greatly to its implementation. 

 - [Ed Spittles](http://github.com/biged) helped with testing and provided 
   many useful issue reports and patches.
