Installation
===============

Installing with Anaconda / conda
--------------------------------

The easiest way to install PyOSP is through `conda 
<https://docs.conda.io/projects/conda/en/latest/user-guide/install/download.html>`_ 
with the following command::

    conda install -c conda-forge pyosp

Installing in a new environment (recommended)
---------------------------------------------

Although it is not required, installing the library in a clean environment represents
good practice and helps avoid potential dependency conflicts. We also recommends install
all dependencies with pyosp through conda-forge channel::

    conda create -n env_pyosp 
    conda activate env_pyosp
    conda config --env --add channels conda-forge
    conda config --env --set channel_priority strict
    conda install python=3 pyosp
    
Installing from source
----------------------
You may install the development version by cloning the source repository
and installed locally:

.. code-block:: bash

    git clone https://github.com/PyOSP-devs/PyOSP.git
    cd pyosp
    conda install --file requirements.txt
    python setup.py install

Testing
-------
If you want to run the unit tests for PyOSP, please run::

    pytest -v

All tests should pass.