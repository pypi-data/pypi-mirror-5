============================================================
PYTHON APPLICATION TO DETERMINE AND SOLVE HAMILTON EQUATIONS
============================================================


To use the Hamilton package, you will need to install python and some basic requirements.

---------------
PYTHON SOFTWARE
---------------

Requirements to use python:
===========================

1. Download  and  install Python
--> http://www.python.org/download/
--> download version 2 (you can also download version 3, but then you might experience 
    trouble with existing third-party software that is not yet compatible with python 3)

2. Download and install Python editor
--> There are numerous editors for python: http://wiki.python.org/moin/PythonEditors
--> Use Spyder for example (works on UNIX, Mac OSX  and Windows)
	--> link: http://code.google.com/p/spyderlib/
	-->Spyder automatically installs all necessary dependencies (e.g. Python, Qt, PyQt, etc.)


Requirements to use the Hamilton library:
=========================================

Use Spyder with standard python executable (NOT ADVISABLE)
-----------------------------------------------------------

Spyder automatically installs all necessary dependencies (e.g. Python, Qt, PyQt, etc.)
Latest Spyder version comes with some python libraries such as Numpy, Scipy, Matplotlib, 
Sympy, etc.

Spyder normally uses the python version that comes with the Spyder app, for example (for Mac):
Spyder>Preferences>Consolo>Advanced settings>Python executable : 

/Applications/Spyder.app/Contents/MacOS/python 

Although this works fine, you might get some errors trying to import and use the python 
control lib (as well as the Slycot lib), because this library uses another numpy version. 
The Hamilton lib includes a control function (uses the control lib), therefore we strongly 
advise to change your 'Python executable' in Spyder to the Python version you downloaded and 
installed on your computer. 

Use Spyder with manually downloaded Python as executable (ADVISABLE): 
---------------------------------------------------------------------

To check the path of this version, use the 'which' command in your terminal
(for UNIX and Mac OSX). e.g .:

$ which python
/Library/Frameworks/Python.framework/Versions/2.7/bin/python

For Windows, use the 'where' command.

You will need to install Qt, SIP, and PyQt:

Qt: http://qt-project.org/downloads
SIP and PyQt: http://www.riverbankcomputing.co.uk/software/pyqt/intro

Unfortunately it's not possible to use the libraries that come with Spyder, so you will have
to download and install them manually. Install the following necessary python libraries to 
use the Hamilton library: 
	- Sympy (http://sympy.org/en/index.html)
	- Numpy (http://www.numpy.org/)
	- Scipy (http://www.scipy.org/)
	- Matplotlib (http://matplotlib.org/)
	- Control (https://www.cds.caltech.edu/~murray/wiki/Control_Systems_Library_for_Python)
	- Slycot (https://github.com/avventi/Slycot)         (the control library uses Slycot)

(again, numerous python editors can be used)

Download and install the Hamilton Package:
==========================================

(Download from: https://pypi.python.org/pypi?%3Aaction=search&term=Hamilton&submit=search)

1. Unpack the Hamilton file (tar file for unix systems)
2. Open terminal, go to the unpacked directory (contains setup.py file) and enter: 
   python setup.py install
3. Normally the directory 'Hamilton' should be installed, you can find this directory in 
   the 'site packages' directory of your python library


Use the Hamilton Package:
=========================

Once previous steps are completed, you should be able open and run the interface (GUI-Hamilton.py): 

1. Open Spyder (make sure python executable in your 'console settings' is changed to your python path) 
2. Open the GUI-Hamilton.py file (or one of the standard examples)
3. Press F5 and the program starts to run
4. The Graphical User Interface (GUI) will show up, and you are good to go!


==========
HAVE FUN !
==========



