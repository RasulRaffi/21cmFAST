---
title: '21cmFAST v3: A Python-integrated C code for generating 3D realizations of the cosmic 21cm signal.'
tags:
  - Python
  - astronomy
  - cosmology
  - simulation
authors:
  - name: Steven G. Murray
    orcid: 0000-0003-3059-3823
    affiliation: 1
  - name: Bradley Greig
    orcid: 0000-0002-4085-2094
    affiliation: 2, 3
  - name: Andrei Mesinger
    orcid: 0000-0003-3374-1772
    affiliation: 4
  - name: Julian B. Muñoz
    orcid: 0000-0002-8984-0465
    affiliation: 5
  - name: Yuxiang Qin
    orcid: 0000-0002-4314-1810
    affiliation: 4
  - name: Jaehong Park
    orcid: 0000-0003-3095-6137
    affiliation: 4
  - name: Catherine A. Watkinson
    orcid: 0000-0003-1443-3483
    affiliation: 6

affiliations:
 - name: School of Earth and Space Exploration, Arizona State University, Phoenix, USA
   index: 1
 - name: ARC Centre of Excellence for All-Sky Astrophysics in 3 Dimensions (ASTRO 3D)
   index: 2
 - name: School of Physics, University of Melbourne, Parkville, VIC 3010, Australia
   index: 3
 - name: Scuola Normale Superiore, Piazza dei Cavalieri 7, 56126 Pisa, Italy
   index: 4
 - name: Department of Physics, Harvard University, 17 Oxford St., Cambridge, MA, 02138, USA
   index: 5
 - name: School of Physics and Astronomy, Queen Mary University of London, G O Jones Building, 327 Mile End Road, London, E1 4NS, UK
   index: 6

date: 29 Feb 2020
bibliography: paper.bib
---

# Summary

The field of 21-cm cosmology -- in which the hyperfine spectral line of neutral hydrogen
(appearing at the rest-frame wavelength of 21 cm) is mapped over large swathes of the
Universe's history -- has developed radically over the last decade.
The promise of the field is to revolutionize our
knowledge of the first stars, galaxies, and black holes through the timing and patterns
they imprint on the cosmic 21-cm signal.
In order to interpret the eventual observational data, a range of physical models have
been developed -- from simple analytic models of the global history of hydrogen reionization,
through to fully hydrodynamical simulations of the 3D evolution of the brightness
temperature of the spectral line.
Between these extremes lies an especially versatile middle-ground: fast semi-numerical
models that approximate the full 3D evolution of the relevant fields: density, velocity,
temperature, ionization, and radiation (Lyman-alpha, neutral hydrogen 21-cm, etc.).
These have the advantage of being comparable to the full first-principles
hydrodynamic simulations, but significantly quicker to run; so much so that they can
be used to produce thousands of realizations on scales comparable to those observable
by upcoming low-frequency radio telescopes, in order to explore the very wide
parameter space that still remains consistent with the data.


Amongst practitioners in the field of 21-cm cosmology, the `21cmFAST` program has become
the *de facto* standard for such semi-numerical simulators.
`21cmFAST` [@mesinger2007; @mesinger2010] is a high-performance C code that uses the
excursion set formalism [@furlanetto2004] to
identify regions of ionized hydrogen atop a cosmological density field evolved using
first- or second-order Lagrangian perturbation theory [@zeldovich1970; @scoccimarro2002],
tracking the thermal and ionization state of the intergalactic medium, and computing
X-ray, soft UV and ionizing UV cosmic radiation fields based on parametrized galaxy models.
For example, the following figure contains slices of lightcones (3D fields in which one
axis corresponds to both spatial *and* temporal evolution) for the various
component fields produced by `21cmFAST`.

![Sample of Component Fields output by 21cmFAST](yuxiangs-plot-small.png){height=300px}

*Figure 1: A Sample of component field lightcones produced by 21cmFAST. Cosmic evolution occurs from bottom to top. From left to right, quantities shown are: (i) dark matter overdensity field; (ii) Lyman-alpha flux; (iii) Lyman-Werner flux; (iv) X-ray heating rate; (v) locally-averaged UVB; (vi) critical halo mass for star formation in Atomically Cooled Galaxies; (vii) critical halo mass for star formation in Molecularly Cooled Galaxies; (viii) cumulative number of recombinations per baryon; (ix) neutral hydrogen fraction; and (x) the 21cm brightness temperature. A high-resolution version of this figure is available at http://homepage.sns.it/mesinger/Media/light-cones_minihalo.png*

However, `21cmFAST` is a highly specialized code, and its implementation has been
quite specific and relatively inflexible.
This inflexibility makes it difficult to modify the behaviour of the code without detailed
knowledge of the full system, or disrupting its workings.
This lack of modularity within the code has led to
widespread code "branching" as researchers hack new physical features of interest
into the C code; the lack of a streamlined API has led derivative codes which run
multiple realizations of `21cmFAST` simulations (such as the Monte Carlo simulator,
`21CMMC` [@greig2015]) to re-write large portions of the code in order to serve their purpose.
It is thus of critical importance, as the field moves forward in its understanding -- and
the range and scale of physical models of interest continues to increase -- to
reformulate the `21cmFAST` code in order to provide a fast, modular, well-documented,
well-tested, stable simulator for the community.

# Features of 21cmFAST v3

This paper presents `21cmFAST` v3+, which is formulated to follow these essential
guiding principles.
While keeping the same core functionality of previous versions of `21cmFAST`, it has
been fully integrated into a Python package, with a simple and intuitive interface, and
a great deal more flexibility.
At a higher level, in order to maintain best practices, a community of users and
developers has coalesced into a formal collaboration which maintains the project via a
Github organization.
This allows the code to be consistently monitored for quality, maintaining high test
coverage, stylistic integrity, dependable release strategies and versioning,
and peer code review.
It also provides a single point-of-reference for the community to obtain the code,
report bugs and request new features (or get involved in development).

A significant part of the work of moving to a Python interface has been the
development of a robust series of underlying Python structures which handle the passing
of data between Python and C via the `CFFI` library.
This foundational work provides a platform for future versions to extend the scientific
capabilities of the underlying simulation code.
The primary *new* usability features of `21cmFAST` v3+ are:

* Convenient (Python) data objects which simplify access to and processing of the various
  fields that form the brightness temperature.
* Enhancement of modularity: the underlying C functions for each step of the simulation
  have been de-coupled, so that arbitrary functionality can be injected into the process.
* Conversion of most global parameters to local structs to enable this modularity, and
  also to obviate the requirement to re-compile in order to change parameters.
* Simple `pip`-based installation.
* Robust on-disk caching/writing of data, both for efficiency and simplified reading of
  previously processed data (using HDF5).
* Simple high-level API to generate either coeval cubes (purely spatial 3D fields defined
  at a particular time) or full lightcone data (i.e. those coeval cubes interpolated over
  cosmic time, mimicking actual observations).
* Improved exception handling and debugging.
* Convenient plotting routines.
* Simple configuration management, and also more intuitive management for the
  remaining C global variables.
* Comprehensive API documentation and tutorials.
* Comprehensive test suite (and continuous integration).
* Strict `semantic versioning <https://semver.org>`_.

While in v3 we have focused on the establishment of a stable and extendable infrastructure,
we have also incorporated several new scientific features, appearing in separate papers:

* Generate transfer functions using the `CLASS` Boltzmann code [@Lesgourgues2011].
* Simulate the effects of relative velocities between dark matter and Baryons [@munoz2019a; @munoz2019b].
* Correction for non-conservation of ionizing photons (Park, Greig et al., *in prep*).
* Include molecularly cooled galaxies with distinct properties [@qin2020]
* Calculate rest-frame UV luminosity functions based on parametrized galaxy models.

`21cmFAST` is still in very active development.
Amongst further usability and performance improvements,
future versions will see several new physical models implemented,
including milli-charged dark matter models [@Munoz2018] and forward-modelled CMB
auxiliary data [@qin2020a].

In addition, `21cmFAST` will be incorporated into large-scale inference codes, such as
`21CMMC`, and is being used to create large data-sets for inference via machine learning.
We hope that with this new framework, `21cmFAST` will remain an important component
 of 21-cm cosmology for years to come.

# Examples

`21cmFAST` supports installation using `conda`, which means installation is as simple
as typing `conda install -c conda-forge 21cmFAST`. The following example can then
be run in a Python interpreter.

In-depth examples can be found in the official documentation.
As an example of the simplicity with which a full lightcone may be produced with
the new `21cmFAST` v3, the following may be run in a Python interpreter (or Jupyter
notebook):

```python
import py21cmfast as p21c

lightcone = p21c.run_lightcone(
    redshift=6.0,              # Minimum redshift of lightcone
    max_redshift=30.0,
    user_params={
        "HII_DIM": 150,        # N cells along side in output cube
        "DIM": 400,            # Original high-res cell number
        "BOX_LEN": 300,        # Size of the simulation in Mpc
    },
    flag_options={
        "USE_TS_FLUCT": True,  # Don't assume saturated spin temp
        "INHOMO_RECO": True,   # Use inhomogeneous recombinations
    },
    lightcone_quantities=(     # Components to store as lightcones
        "brightness_temp",
        "xH_box",
        "density"
    ),
    global_quantities=(        # Components to store as mean
        "xH_box",              # values per redshift
        "brightness_temp"
    ),
)

# Save to a unique filename hashing all input parameters
lightcone.save()

# Make a lightcone sliceplot
p21c.plotting.lightcone_sliceplot(lightcone, "brightness_temp")
```

![Brightness Temperature Lightcone](lightcone.pdf){height=300px}
*Figure 2: Brightness temperature lightcone produced by the example code in this paper.*

```python
# Plot a global quantity
p21c.plotting.plot_global_history(lightcone, "xH")
```

![Global reionization history](xH_history.pdf){height=300px}
*Figure 3: Globally volume-averaged hydrogen neutral fraction produced by the example code in this paper.*


# Acknowledgements

This work was supported in part by the European Research Council
(ERC) under the European Union’s Horizon 2020 research
and innovation programme (AIDA – #638809). The results
presented here reflect the authors’ views; the ERC is not
responsible for their use.

# References