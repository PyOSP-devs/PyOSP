<p align="center">
  <img alt="pyosp logo" src="https://i.imgur.com/vLPaRWY.png" height="200" /></p>
  <p align="center">
    <a href="/license"><img alt="software license" src="https://img.shields.io/github/license/yzh211/pyosp?style=flat-square"></a>
    <a href="/release"><img alt="github release (latest by date)" src="https://img.shields.io/github/v/release/PyOSP-devs/PyOSP?style=flat-square"></a>
    <a href="/build"><img alt="TravisCI" src="https://travis-ci.org/PyOSP-devs/PyOSP.svg?branch=master"></a>
    <a href='https://coveralls.io/github/PyOSP-devs/PyOSP?branch=master'><img src='https://coveralls.io/repos/github/PyOSP-devs/PyOSP/badge.svg?branch=master' alt='Coverage Status' /></a>
    <img alt="publication" src="https://img.shields.io/badge/publication-geomorphology-blue?style=flat-square"></a>
  </p>
</p>

---

<p><img alt="intro" src="https://i.imgur.com/7jkyyog.gif" height="300"/></p>

_Intelligent and comprehensive swath analysis_

## Features

- :gem: **intelligent**: objectively identify irregular boundries using elevation, slope, tpi, or other raster analyses.
- :milky_way: **comprehensive**: cuvilinear and circular swath analyses, reclassification of swath data, cross-swath, slice and histogram, etc.  
- :two_women_holding_hands: **compatible**: work seamlessly with gis software.
- :anchor: **dependencies**: numpy, matplotlib, gdal, scipy and shapely.

## Documentation
Read the documentation at: https://pyosp.readthedocs.io/en/latest/index.html

## Installation
We recommend to use the [conda](https://conda.io/en/latest/) package manager to install pyosp. It will provide pre-built binaries for all dependencies of pyosp. if you have the [miniconda](https://docs.conda.io/en/latest/miniconda.html) (recommend; only containing python and the conda package manager), or [anaconda distribution](https://www.anaconda.com/) (a python distribution with many installed libraries for data science) installed, then simply execute the following command:

```bash
conda install -c conda-forge -c kgsdev pyosp 
```

You can also install from current branch:

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
Here is a simple example of using pyosp to perform swath analysis on a synthetic mountain case. the cross-width of mountain is around 90m, and only mountainous area possess non-zero elevations. 

<p><img alt="homo_case" src="https://i.imgur.com/nSFSqxo.png" height="200"/></p>

Original, elevation, slope and tpi based swath polygons.

```python
import pyosp

baseline = pyosp.datasets.get_path("homo_baseline.shp") # the path to baseline shapefile
raster = pyosp.datasets.get_path("homo_mount.tif")  # the path to raster file

orig = pyosp.orig_curv(line, raster, width=100,
                       line_stepsize=3, cross_stepsize=none)

elev = pyosp.elev_curv(line, raster, width=100,
                       min_elev=0.01,
                       line_stepsize=3, cross_stepsize=none)

slope = pyosp.slope_curv(line, raster, width=100,
                         min_slope=1,
                         line_stepsize=3, cross_stepsize=none)

tpi = pyosp.tpi_curv(line, raster, width=100,
                     tpi_radius=50, min_tpi=0,
                     line_stepsize=3, cross_stepsize=none)
```

You can plot with matplotlib, or open in gis software.

<p><img alt="homo_polygon" src="https://i.imgur.com/nLgQEsJ.jpg" height="200"/></p>

Plot, for example, elevation based swath profile.

```python
elev.profile_plot()
```

<img alt="elev_sp" src="https://i.imgur.com/0taXAhF.jpg.jpg" height="200"/></p>

_For more example and usage, please refer to our publication, example gallery and documentation._

## Citing pyosp

## Contributing

Any contributions you make are **greatly appreciated**.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/amazingfeature`)
3. Commit your changes (`git commit -m 'add some amazingfeature'`)
4. Push to the branch (`git push origin feature/amazingfeature`)
5. Open a pull request

## Feedback

- If you think pyosp is useful, consider giving it a start.
- If something is not working, [create an issue](https://github.com/pyosp-devs/pyosp/issues/new)
- If you need to get in touch for other reasons, [send us an email](yichuan211@gmail.com)

## Credits
This work is supported by [Kentucky Geological Survey](https://www.uky.edu/kgs/).

## License
[Apache license, version 2.0](https://github.com/pyosp-devs/pyosp/blob/master/license)
