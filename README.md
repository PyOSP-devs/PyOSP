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
- :milky_way: **Comprehensive**: cuvilinear and circular swath analyses, reclassification of swath data, cross-swath, slice and histogram, etc.  
- :two_women_holding_hands: **Compatible**: work seamlessly with GIS software.
- :anchor: **Dependencies**: Only NumPy, Matplotlib, GDAL and Shapely.

## Installation
We recommend to use the [conda](https://conda.io/en/latest/) package manager to install PyOSP. It will provide pre-built binaries for all dependencies of PyOSP. If you have the [Anaconda distribution](https://www.anaconda.com/) (a Python distribution with many installed libraries for data science), or [miniconda](https://docs.conda.io/en/latest/miniconda.html) (only containing Python and the conda package manager) installed, then simply execute the following command:

```bash
conda install --channel conda-forge pyosp 
```

You can verify installation by entering a Python shell and typing:

```python
import pyosp
print(pyosp.__version__)
```

## Example
Here is a simple example of using PyOSP to perform swath analysis on a synthetic mountain case. The cross-width of mountain is around 90m, and only mountainous area possess non-zero elevations. 

<img alt="homo_case" src="https://i.imgur.com/nSFSqxo.png" height="200"/></p>

Original, elevation, slope and TPI based swath polygons.

```python
import pyosp
import matplotlib.pyplot as plt

line = "/tests/data/homo_baseline.shp"
raster = "/tests/data/homo_stripe.tif"

orig_polygon = "/tests/data/orig_polygon.shp"
elev_polygon = "/tests/data/elev_polygon.shp"
slope_polygon = "/tests/data/slope_polygon.shp"
tpi_polygon = "/tests/data/tpi_polygon.shp"

orig = pyosp.Orig_curv(line, raster, width=100,
                       line_stepsize=3, cross_stepsize=None)

elev = pyosp.Elev_curv(line, raster, width=100,
                       min_elev=0.01,
                       line_stepsize=3, cross_stepsize=None)

slope = pyosp.Slope_curv(line, raster, width=100,
                         min_slope=1,
                         line_stepsize=3, cross_stepsize=None)

tpi = pyosp.Tpi_curv(line, raster, width=100,
                     tpi_radius=50, min_tpi=-5,
                     line_stepsize=3, cross_stepsize=None)
                
pyosp.write_polygon(orig.out_polygon(), orig_polygon)
pyosp.write_polygon(elev.out_polygon(), elev_polygon)
pyosp.write_polygon(slope.out_polygon(), slope_polygon)
pyosp.write_polygon(tpi.out_polygon(), tpi_polygon)
```

You can plot with matplotlib, or open in GIS software.

<img alt="homo_polygon" src="https://i.imgur.com/nLgQEsJ.jpg" height="200"/></p>

Plot, for example, elevation based swath profile.

```python
elev.profile_plot()
```

<img alt="elev_SP" src="https://i.imgur.com/0taXAhF.jpg.jpg" height="200"/></p>

_For more example and usage, please refer to our publication, example gallery and documentation._

## Citing PyOSP

## Contributing

Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Feedback

- If you think PyOSP is useful, consider giving it a start.
- If something is not working, [create an issue](https://github.com/PyOSP-devs/PyOSP/issues/new)
- If you need to get in touch for other reasons, [send us an email](yichuan211@gmail.com)

## Credits
This work is supported by [Kentucky Geological Survey](https://www.uky.edu/KGS/).

## License
[Apache License, Version 2.0](https://github.com/PyOSP-devs/PyOSP/blob/master/LICENSE)
