# C-TuLiP


WARNING: This explanation mainly covers  the discrete controller. The continuous control operations are not included.
Date = 19th September 2017

I. Requirements
------------------------
   1. Python version 2.7.13/3.6
   2. Tulip version 1.4 & Polytope (both cloned from the github version and installed as explained)
   3. State Chart Autocoder (Also cloned from the github version and installed as explained. See documentation files.)


### 1. Install Python in separate environement
The software runs stable with on the current version of Python 2.7.13 or 3.6.
    Still it can be handy to install an additional version of Python and to use a virtual environment for this the use of anaconda is advised\
    https://www.continuum.io/downloads\
   After installation in the terminal:\
   `$   conda create -n python36 python=3.6 anaconda` \
     activate the environment with\
   `$   source activate python36`\
   All packages associated to this python version can now be installed either via Anaconda or via the terminal in the active python36 environment.

### 2. Installing old version Tulip & Polytope
   Follow the installation advice for installing TuLiP (see https://pypi.python.org/pypi/tulip/1.2.0).
  The  TuLiP packages will only work well if you install,
  * cvxopt,
  * numpy,
  * scypi, and
  * matplotlib\
  A anaconda installation works well for these packages (especially for linking cvxopt correctly.)

  -------------------------------
  **Remark for CVXopt**
  First make sure you have GLPK, for example with

    $   sudo port install glpk

  In the virtual environment use

    $     export CVXOPT_BUILD_GLPK=1
    $     pip install cvxopt

  ----------------------


  Remark that when you have several python versions on your computer then this version of TuLiP,
    together with its required packages, should be installed in the same environment as python 2.7.10.
   To install TuLiP download, unzip, open terminal and go to the right folder using:\
    `$   cd pathto/tulip`\
   then install as:\
    `$   pip install`.\
   Afterwards the installation can be tested with
    `$   ./run_tests.py`
   in the terminal from the root of the TuLiP folder. Note that this requires the python package ``Nose``.


### 3. Installing State Chart Autocoder
\
   (text obtained from example https://vehicles.caltech.edu/tmp/tulipsca.tar.gz)
    The JPL Statechart Autocoder is available from
    https://github.com/JPLOpenSource/SCA

   To fetch a copy of the SCA repository and build the autocoder,

    $    git clone https://github.com/JPLOpenSource/SCA.git
    $    cd SCA/autocoder
    $    make

   The resulting file is named "autocoder.jar". E.g., to get the help message, try

    $    java -jar autocoder.jar -h

   In the example described below, we must use autocoder.jar as well as supporting
    components from the "Quantum Framework" in Python (in the SCA repo). To arrange
    your shell environment for easy access to these, try the following, where you
    need to modify `/your/path/to/SCA` to be the absolute path to the SCA repo that
    we cloned above.

    $    export SCA=/your/path/to/SCA
    $    export PYTHONPATH=$PYTHONPATH:$SCA/QF_Py/src
    $    export PYTHONPATH=$PYTHONPATH:$SCA/QF_Py/bin
    $    export PATH=$PATH:$SCA/QF_Py/bin
    $    alias autocoder='java -jar $SCA/autocoder/autocoder.jar'

   Adding the following lines of text to your `.bash_profile in your` home directory will ensure that on start up your path is set correctly.
   If the above succeeded, then you can now get the help message using  ` autocoder -h`.

II Install C-TuLiP
-----------------------------
Do a `pip . install` in the  C-Tulip folder. 


III Running the (tutorial) Examples
-----------------------------

The code for generating XMI and a partial Python implementation are in the
Python module dumpsmach.py.
Two examples can easily be checked
 * Thermostat design
    * `ThermoStat.py` = script  to generate state-chart using TuLiP
    * `runner_ThermoStat.py` = script for demonstrating with generated code
 * Alice, a simplified rover speed control`
    * `AliceSimp.py` = script  to generate state-chart using TuLiP
    * `runner_Alice.py`= script for demonstrating with generated code

##### 1. Design state-chart with TuLiP

Following commands should be executed in the python2 environement.
To begin,

    $   python ThermoStat.py

which will result in the creation of four files:
* ThermoStat_gen.xml - an XML file that SCA can accept as input;
* ThermoStat_gen.impl - code fragments in Python providing, e.g., control input selection that realizes edges in the discrete abstraction;
* ThermoStat_gen.pickle - various data required by code in tst.impl.

I will also give a figure
* thermostat_bump.svg - a visualization of the Mealy machine in SVG format;



##### 2. Autocode state-chart to python with SCA

Folder with makefile for demo and autocoding will temporally be referred to as the SCADemo folder.

Option 1 :
    Code only the state-chart of the discrete controller.

Option 2 :
    Code both the state-chart of the discrete controller and the effect on the abstract system

For Option 1&2 copy the relevant xml files to the SCADemo folder.
For Option 2 import the "filename"_sys.xml to the "filename"_gen.xml by opening the latter in MagicDraw and importing it. Be sure that none of the effect behaviours get modified with the import. Sometimes MagicDraw renames the events to be triggered. This will give issues with Autocoding it.

Finalaly follow the readme instructions in the SCADemo folder to autocode and to generate the demo.

## Installation issues


install dsdp for cvxopt gives missing malloc.h
replace include <malloc.h> with <malloc/malloc.h>
https://lists.apple.com/archives/xcode-users/2007/Jul/msg00570.html
