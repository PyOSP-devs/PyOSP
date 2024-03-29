PyOSP
=====

PyOSP (Python Object-oriented Swath Profile) is an intelligent swath tool that can characterize complex 
topographic features. Unlike traditional swath methods have been limited to rectangular or simplified
curvilinear sampling blocks, PyOSP can objectively characterize complex geomorphic boundaries using
elevation, slope angle, topographic position index (TPI), or other raster calculations by intelligently
assimilating geo-processing information into swath analysis.

PyOSP supports Python 3.6 or higher, and depends on `Numpy <https://numpy.org/>`_ , `Matplotlib 
<https://matplotlib.org/>`_ , `GDAL <https://gdal.org/>`_ , `SciPy <https://www.scipy.org/>`_, and `Shapely <https://shapely.readthedocs.io/en/latest/>`_ .

.. toctree::
   :maxdepth: 1
   :caption: Getting Started

   Installation <user_guide/installation>
   Traditional curvilinear swath analysis <notebooks/fix_width_curv>
   Traditional circular swath analysis <notebooks/fix_radius_cir>
   Object-oriented swath analysis <notebooks/object_homo>

.. toctree::
   :maxdepth: 1
   :caption: Tutorial 
   
   Customized swath analysis and essential data structure <notebooks/customized_swath>
   Slice and histogram analysis <notebooks/Slice_hist>
   Swath profile with scatter plots <notebooks/swath_scatter>
   Cross-swath analysis <notebooks/cross_swath>
   Density(Heat) scatter plot <notebooks/density_scatter>
   Data reclassification <notebooks/reclass>

.. toctree::
   :maxdepth: 1
   :caption: Applications

   Topographic analysis of the Teton Range, Wyoming <notebooks/pyosp_teton>
   Terrace correlation along Licking River, Kentucky <notebooks/pyosp_licking>
   Swath analysis of Olympus Mons, Mars <notebooks/pyosp_olympus>

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
