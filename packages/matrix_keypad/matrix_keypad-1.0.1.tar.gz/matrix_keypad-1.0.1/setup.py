from distutils.core import setup

setup(
    name = 'matrix_keypad',
    packages = ['matrix_keypad'],
    version = '1.0.1',
    description = 'Matrix Keypad',
    author='Chris Crumpacker',
	author_email = 'chris@chriscrumpacker.com',
	url = 'http://crumpspot.blogspot.com/2013/08/python-matrix-keypad-package.html',
	classifiers = [
		"Programming Language :: Python",
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
		"Operating System :: OS Independent",
		"Environment :: Other Environment",
		"Development Status :: 4 - Beta",
		"Intended Audience :: Developers",
		"Topic :: System :: Hardware",
		"Topic :: Software Development :: Libraries :: Python Modules",
		],
	long_description = """\
Introduction
============

Python Library for Matrix Keypads. 
Written and tested on a Model B Raspberry Pi.
Supports both a 3x4 and 4x4 keypad included

:Project Page:  Project_Page_
:PyPI page:  PyPI_Page_

Version
=======

:v0.1.0:
	May 2013

	Initial Scripts

:v1.0.0:
    
	August 19th, 2013
    
	Initial package build
	
:v1.0.1:
    
	August 19th, 2013
    
	Initial package build and push to PyPI

Author
======

:Author:	Chris Crumpacker
:Email:		chris@chriscrumpacker.com
:Web:		http://www.chriscrumpacker.com
:Blog:		http://crumpspot.blogspot.com

Prerequisites
=============

If the I2C Port expander MCP23017 or MCP23008 is being used, the Adafruit Python library for I2C and the MCP will need to be installed.

You can clone the whole library like so::

	git clone https://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code.git

or the two files needed can be pulled out, Adafruit_I2C.py_ & Adafruit_MCP230xx.py_.

Install
=======


Files Included
==============
::

    README.txt
    LICENSE.txt
    setup.py
    matrix_keypad/
        __init__.py
        matrix_keypad_RPi_GPIO.py
        matrix_keypad_MCP230xx.py
        matrix_keypad_demo.py
        matrix_keypad_demo2.py

Usage
=====
*See the demo scripts included to see this all in action.*

To call the library select which one you intend to use and use the correct line::

    from matrixKeypad_MCP230xx import keypad

or::

    from matrixKeypad_RPi_GPIO import keypad

Then name the library so it is easier to reference later::
	
    kp = keypad()

It is possible to just check to see if a digit is currently pressed.::

    checkKeypad = kp.getKey()
	
Or a simple function to call the keypad library and 
loop through it waiting for a digit press ::

    def digit():
        # Loop while waiting for a keypress
        digitPressed = None
        while digitPressed == None:
            digitPressed = kp.getKey()
        return digitPressed
	
References
==========

Column and Row scanning adapted from Bandono's matrixQPI_ which is wiringPi based.

.. --------------------------------------------------------------------------
.. Links

.. _Project_Page: http://crumpspot.blogspot.com/2013/08/python-matrix-keypad-package.html
.. _PyPI_Page: https://pypi.python.org/pypi
.. _Adafruit_I2C.py: https://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code/blob/master/Adafruit_I2C/Adafruit_I2C.py
.. _Adafruit_MCP230xx.py: https://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code/blob/master/Adafruit_MCP230xx/Adafruit_MCP230xx.py
.. _matrixQPI: https://github.com/bandono/matrixQPi?source=cc
	"""
)