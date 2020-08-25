<p align="center">
  <img alt="PyOSP Logo" src="https://i.imgur.com/KNdbtaJ.png" height="140" /></p>
  <p align="center">
    <a href="/LICENSE"><img alt="Software License" src="https://img.shields.io/github/license/yzh211/PyOSP?style=flat-square"></a>
    <a href="/Release"><img alt="GitHub release (latest by date)" src="https://img.shields.io/github/v/release/yzh211/PyOSP?style=flat-square"></a>
    <img alt="Contributions" src="https://img.shields.io/badge/contributions-welcome-orange?style=flat-square"></a>
    <img alt="Publication" src="https://img.shields.io/badge/Publication-Geomorphology-blue?style=flat-square"></a>
  </p>
</p>

---

<img alt="intro" src="https://i.imgur.com/7jkyyog.gif" height="300"/></p>
_Intelligent and comprehensive swath analysis_

## Features

- :gem: **Intelligent**: objectively identify irregular boundries using elevation, slope, TPI, or other raster analyses.
- :milky_way: **Comprehensive**: cuvilinear and circular swath analysis, reclassification of swath data, cross-swath, slice and histogram, etc.  
- :two_women_holding_hands: **Compatible**: work seamlessly with GIS software.
- :anchor: **Dependencies**: Only NumPy, Matplotlib, GDAL and Shapely.

## Installation
We recommend to use the [conda](https://conda.io/en/latest/) package manager to install PyOSP. This will provide pre-built binaries for all dependencies of PyOSP. If you have the [Anaconda distribution](https://www.anaconda.com/) (a Python distribution with many installed libraries for data science), or [miniconda](https://docs.conda.io/en/latest/miniconda.html) (only containing Python and the conda package manager) installed, then simply run the following command:

```bash
conda install --channel conda-forge pyosp 
```

After installation, you can verify by entering a Python shell and typing:

```python
import pyosp
print(pyosp.__version__)
```
