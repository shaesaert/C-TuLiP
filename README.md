# C-TuLiP


WARNING: This explanation mainly covers  the discrete controller. The continuous control operations are not included.
Date = 19th September 2017

I. Requirements and Installation
------------------------
   1. Python version 2.7.13/3.6
   2. Tulip version 1.4 & Polytope (both cloned from the github version and installed as explained)
   3. State Chart Autocoder (Also cloned from the github version and installed as explained. See documentation files.)
   4. Install C-TuLiP

### 1. Install Python in separate environment
The software runs stable with on the current version of Python 2.7.13 or 3.6.
    Still it can be handy to install an additional version of Python and to use a virtual environment for this the use of anaconda is advised\
    https://www.continuum.io/downloads\
   After installation in the terminal:\
   `$   conda create -n python36 python=3.6 anaconda` \
     activate the environment with\
   `$   source activate python36`\
   All packages associated to this python version can now be installed either via Anaconda or via the terminal in the active python36 environment.

### 2. Installing version Tulip & Polytope
   Follow the installation advice for installing TuLiP (see https://pypi.python.org/pypi/tulip/1.2.0).
  The  TuLiP packages will only work well if you install,
  * cvxopt,
  * numpy,
  * scypi, and
  * matplotlib
  
An anaconda installation works well for these packages (especially for linking cvxopt correctly.)


Remark that when you have several python versions on your computer then this version of TuLiP,
    together with its required packages, should be installed in the same environment the version of python.
   To install TuLiP download, unzip, open terminal and go to the right folder using:\
    `$   cd pathto/tulip` 
   then install as: 
    `$   pip install`. 
   Afterwards the installation can be tested with
    `$   ./run_tests.py`
   in the terminal from the root of the TuLiP folder. Note that this requires the python package ``Nose``.

**Remark for CVXopt**
  First make sure you have GLPK, for example with\
    `  $   sudo port install glpk`. 
  In the virtual environment use
    `$     export CVXOPT_BUILD_GLPK=1` and 
    `$     pip install cvxopt`.

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

### 3. Install C-TuLiP
Do a `pip . install` in the  C-Tulip folder.


II Running the (tutorial) Examples
-----------------------------
In the `Example folder`

 * Discrete synthesis problems
    * Communication Window example
    * Lift controller
    * Arbiter controller
 * Continuous synthesis problem
    * Alice, a simplified rover speed control


##### 1. Discrete synthesis problem

Following commands should be executed in the python2 environement.
To begin, start with `$   python Lift.py`,
which will result in the creation of 
`Lift_gen.xml`, an XML file, that SCA can accept as input.

The folder (C-harness ...) with the makefile for the demo and autocoding will temporally be referred to as the SCADemo folder.

***Option 1:*** Code only the state-chart of the discrete controller.

***Option 2:*** Code both the state-chart of the discrete controller
     and its effect on some given state-charts

For Option 1 and 2 copy the relevant xml files to the SCADemo folder.
For Option 2 import the "filename"_gen.xml to a XML file containing pre-existing state-charts by opening
the latter in MagicDraw and importing it. Be sure that none of the behaviours
 get modified with the import.
 Sometimes MagicDraw renames the events to be triggered. This will give issues with Autocoding it.
Finally follow the readme instructions in the SCADemo folder to autocode and to generate the demo.

