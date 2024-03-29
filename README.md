<p align="center">
  <img alt="pyosp logo" src="https://i.imgur.com/vLPaRWY.png" height="200" /></p>
  <p align="center">
    <a href="/release"><img alt="github release (latest by date)" src="https://img.shields.io/github/v/release/PyOSP-devs/PyOSP?style=flat-square"></a>
    <a href="/build"><img alt="TravisCI" src="https://travis-ci.org/PyOSP-devs/PyOSP.svg?branch=master"></a>
    <a href='https://coveralls.io/github/PyOSP-devs/PyOSP?branch=master'><img src='https://coveralls.io/repos/github/PyOSP-devs/PyOSP/badge.svg?branch=master' alt='Coverage Status' /></a>
    <a href="/Downloads"><img alt="Conda Downloads" src="https://img.shields.io/conda/dn/conda-forge/pyosp.svg"></a>  
    <a href="https://doi.org/10.1016/j.geomorph.2021.107778"><img alt="publication" src="https://img.shields.io/badge/publication-Geomorphology-blue?style=flat-square"></a>
  </p>
</p>

---

<p><img alt="intro" src="https://i.imgur.com/7jkyyog.gif" height="300"/></p>

_Intelligent and comprehensive swath analysis_

## Features

- :gem: **Intelligent**: objectively identify irregular boundries using elevation, slope, TPI, or other raster analyses.
- :milky_way: **Comprehensive**: cuvilinear and circular swath analyses, reclassification of swath data, cross-swath, slice and histogram, etc.  
- :two_women_holding_hands: **Compatible**: work seamlessly with GIS software.
- :anchor: **Dependencies**: numpy, matplotlib, gdal, scipy and shapely.

## Documentation
Read the documentation at: https://pyosp.readthedocs.io/en/latest/index.html

Introduction, methodology, and case studies: https://doi.org/10.1016/j.geomorph.2021.107778

Applications (starting from scratch):
1. [Topographic analysis of Teton Range, Wyoming](https://pyosp.readthedocs.io/en/latest/notebooks/pyosp_teton.html)
2. [Terrace correlation along the Licking River, Kentucky](https://pyosp.readthedocs.io/en/latest/notebooks/pyosp_licking.html)
3. [Circular swath analysis of Olympus Mons, Mars](https://pyosp.readthedocs.io/en/latest/notebooks/pyosp_olympus.html)

## Installation
We recommend to use the [conda](https://conda.io/en/latest/) package manager to install pyosp. It will provide pre-built binaries for all dependencies of pyosp. If you have the [miniconda](https://docs.conda.io/en/latest/miniconda.html) (recommend; only containing python and the conda package manager), or [anaconda distribution](https://www.anaconda.com/) (a python distribution with many installed libraries for data science) installed, then simply execute the following command:

```bash
conda install -c conda-forge pyosp 
```

## Installing in a new environment (recommended)

Although it is not required, installing the library in a clean environment represents
good practice and helps avoid potential dependency conflicts. We also recommends install
all dependencies with pyosp through conda-forge channel

```bash
conda create -n env_pyosp 
conda activate env_pyosp
conda config --env --add channels conda-forge
conda config --env --set channel_priority strict
conda install python=3 pyosp
```


### You can also install from current branch:

```bash
git clone https://github.com/pyosp-devs/pyosp.git
cd pyosp
conda install --file requirements.txt
python setup.py install
```

You can verify installation by entering a python shell and typing:

```python
import pyosp
print(pyosp.__version__)
```

## Example
Here is a simple example of using pyosp to perform swath analysis on a synthetic mountain case. The cross-width of mountain is around 90m, and flat ground has elevation of zero.

<p><img alt="homo_case" src="https://i.imgur.com/nSFSqxo.png" height="200"/></p>

Original, elevation, slope and tpi based swath calculation.

```python
import pyosp

baseline = pyosp.datasets.get_path("homo_baseline.shp") # the path to baseline shapefile
raster = pyosp.datasets.get_path("homo_mount.tif")  # the path to raster file

orig = pyosp.Orig_curv(baseline, raster, width=100,
                       line_stepsize=3, cross_stepsize=None)

elev = pyosp.Elev_curv(baseline, raster, width=100,
                       min_elev=0.01,
                       line_stepsize=3, cross_stepsize=None)

slope = pyosp.Slope_curv(baseline, raster, width=100,
                         min_slope=1,
                         line_stepsize=3, cross_stepsize=None)

tpi = pyosp.Tpi_curv(baseline, raster, width=100,
                     tpi_radius=50, min_tpi=0,
                     line_stepsize=3, cross_stepsize=None)
```

We can plot with matplotlib, or open in GIS software.

<p><img alt="homo_polygon" src="https://i.imgur.com/nLgQEsJ.jpg" height="200"/></p>

Plot, for example, elevation based swath profile.

```python
elev.profile_plot()
```

<img alt="elev_sp" src="https://i.imgur.com/0taXAhF.jpg.jpg" height="200"/></p>

_For more example and usage, please refer to our documentation._

## Citing pyosp
If you use PyOSP for your work, please cite as:

Y. Zhu, J.M. Dortch, M.A. Massey, et al., An Intelligent Swath Tool to Characterize complex Topographic Features: Theory and Application in the Teton Range, Licking River, and Olympus Mons, Geomorphology (2021), https://doi.org/10.1016/j.geomorph.2021.107778

## Contributing

Any contributions you make are **greatly appreciated**.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/amazingfeature`)
3. Commit your changes (`git commit -m 'add some amazingfeature'`)
4. Push to the branch (`git push origin feature/amazingfeature`)
5. Open a pull request

## Feedback

- If you think pyosp is useful, consider giving it a star.
- If something is not working, [create an issue](https://github.com/pyosp-devs/pyosp/issues/new)
- If you need to get in touch for other reasons, [send us an email](yichuan211@gmail.com)

## Credits
This work is supported by [Kentucky Geological Survey](https://www.uky.edu/kgs/).

## License
[Apache license, version 2.0](https://github.com/pyosp-devs/pyosp/blob/master/license)
