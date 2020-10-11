Installation
===============

Installing with Anaconda / conda
--------------------------------

The easiest way to install PyOSP is through `conda 
<https://docs.conda.io/projects/conda/en/latest/user-guide/install/download.html>`_ 
with the following command::

    conda install -c conda-forge -c kgsdev pyosp

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

    py.test -v

All tests should pass.