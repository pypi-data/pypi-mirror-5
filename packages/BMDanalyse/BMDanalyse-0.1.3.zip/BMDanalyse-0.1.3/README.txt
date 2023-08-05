==========
BMDanalyse
==========
*Tool for the regional analysis of a time series of medical images*

Copyright 2013, Michael Hogg

https://pypi.python.org/pypi/BMDanalyse/

Author
------

Michael Hogg (michael.christopher.hogg@gmail.com)

Requirements
------------

PyQt4/PySide,
python 2.6 / 2.7,
pyqtgraph >= 0.9.7,
numpy >= 1.4.0, 
matplotlib >= 1.0,
PIL >= 1.1.6

Support:
--------
Contact author by email 

Installation Methods
--------------------
a. Install from source

   1. Ensure that all dependencies are installed
   2. Download the zip file (available on PyPi))
   3. Extract zip file using any unzip utility
   4. Browse to extracted folder containing setup.py and install using::

      $ python setup.py install

   5. Ensure that %PYTHONHOME%/Scripts is in PATH 

b. Binaries for 32-bit and 64-bit Python (available on PyPi)

   1. Download executable binary installer
   2. Run executable binary installer 

How to run
----------

(1) From the command prompt:
    
    On windows (assuming that %PYTHONHOME%/Scripts is in PATH) open a command prompt and enter:
    $ BMDanalyse

(2) From within a python session:

    $ import BMDanalyse
    $ BMDanalyse.run()

    To use PySide if both PyQt and PySide are installed, import PySide first:
    $ import PySide
    $ import BMDanalyse
    $ BMDanalyse.run()

Documentation
-------------
See website for instructions on how to use BMDanalyse.
