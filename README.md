# EyeLoop [![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0) [![contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat)](https://github.com/simonarvin/eyeloop/issues) [![Build Status](https://travis-ci.com/simonarvin/eyeloop.svg?branch=master)](https://travis-ci.com/simonarvin/eyeloop) ![version](https://img.shields.io/badge/version-0.35--beta-brightgreen) ![lab](https://img.shields.io/badge/yonehara-lab-blue) ![beta](https://img.shields.io/badge/-beta-orange)

<p align="center">
<img src="https://github.com/simonarvin/eyeloop/blob/master/misc/imgs/logo.svg?raw=true" width = "280">
</p>
<p align="center">
<img src="https://github.com/simonarvin/eyeloop/blob/master/misc/imgs/eyeloop%20overview.svg?raw=true">
</p>

<p align="center">
    <img src="https://github.com/simonarvin/eyeloop/blob/master/misc/imgs/sample_1.gif?raw=true" align="center" height="150">&nbsp; <img src="https://github.com/simonarvin/eyeloop/blob/master/misc/imgs/sample_3.gif?raw=true" align="center" height="150">&nbsp; <img src="https://github.com/simonarvin/eyeloop/blob/master/misc/imgs/sample_4.gif?raw=true" align="center" height="150">
  </p>

EyeLoop is a Python 3-based eye-tracker tailored specifically to dynamic, closed-loop experiments on consumer-grade hardware. Users are encouraged to contribute to EyeLoop's development.

## Features ##
- [x] **High-speed** > 1000 Hz on non-specialized hardware (no dedicated processing units necessary).
- [x] Modular, readable, **customizable**.
- [x] **Open-source**, and entirely Python 3.
- [x] **Works on any platform**, easy installation.

## Overview ##
- [How it works](#how-it-works)
- [Getting started](#getting-started)
- [Your first experiment](#designing-your-first-experiment)
- [Data](#data)
- [User interface](#graphical-user-interface)
- [Authors](#authors)
- [Examples](https://github.com/simonarvin/eyeloop/blob/master/examples)
- [*EyeLoop Playground*](https://github.com/simonarvin/eyeloop_playground)

## How it works ##
<p align="center">
<img src="https://github.com/simonarvin/eyeloop/blob/master/misc/imgs/software%20logic.svg?raw=true" width = "500">
</p>

EyeLoop consists of two functional domains: the engine and the optional modules. The engine performs the eye-tracking, whereas the modules perform optional tasks, such as:

- Experiments
- Data acquisition
- Importing video sequences to the engine

> The modules import or extract data from the engine, and are therefore called *Importers* and *Extractors*, respectively.

One of EyeLoop's most appealing features is its modularity: Experiments are built simply by combining modules with the core Engine. Thus, the Engine has one task only: to compute eye-tracking data based on an *imported* sequence, and offer the generated data for *extraction*.

> How does [the Engine](https://github.com/simonarvin/eyeloop/blob/master/eyeloop/engine/README.md) work?\
> How does [the Importer](https://github.com/simonarvin/eyeloop/blob/master/eyeloop/importers/README.md) work?\
> How does [the Extractor](https://github.com/simonarvin/eyeloop/blob/master/eyeloop/extractors/README.md) work?

## Getting started ##

### Installation ###

Install EyeLoop by cloning the repository:
```
git clone https://github.com/simonarvin/eyeloop.git
```

>Dependencies: ```python -m pip install -r requirements.txt```

>Using pip:
> ```pip install .```

You may want to use a Conda or Python virtual environment when
installing `eyeloop`, to avoid mixing up with your system dependencies.

>Using pip and a virtual environment:

> ```python -m venv venv```

> ```source venv/bin/activate```

> ```(venv) pip install .```

Alternatively:

>- numpy: ```python pip install numpy```
>- opencv: ```python pip install opencv-python```

To download full examples with footage, check out EyeLoop's playground repository:

```
git clone https://github.com/simonarvin/eyeloop_playground.git
```

---

### Initiation ###

EyeLoop is initiated through the command-line utility `eyeloop`.
```
eyeloop
```
To access the video sequence, EyeLoop must be connected to an appropriate *importer class* module. Usually, the default opencv importer class (*cv*) is sufficient. For some machine vision cameras, however, a vimba-based importer (*vimba*) is neccessary.
```
eyeloop --importer cv/vimba
```
> [Click here](https://github.com/simonarvin/eyeloop/blob/master/eyeloop/importers/README.md) for more information on *importers*.

To perform offline eye-tracking, we pass the video argument ```--video``` with the path of the video sequence:
```
eyeloop --video [file]/[folder]
```
<p align="right">
    <img src="https://github.com/simonarvin/eyeloop/blob/master/misc/imgs/models.svg?raw=true" align="right" height="150">
</p>

EyeLoop can be used on a multitude of eye types, including rodents, human and non-human primates. Specifically, users can suit their eye-tracking session to any species using the ```--model``` argument.

```
eyeloop --model ellipsoid/circular
```
> In general, the ellipsoid pupil model is best suited for rodents, whereas the circular model is best suited for primates.

To learn how to optimize EyeLoop for your video material, see [*EyeLoop Playground*](https://github.com/simonarvin/eyeloop_playground).

To see all command-line arguments, pass:

```
eyeloop --help
```

## Designing your first experiment ##

<p align="center">
    <img src="https://github.com/simonarvin/eyeloop/blob/master/misc/imgs/setup.svg?raw=true" align="center" height="250">
</p>

In EyeLoop, experiments are built by stacking modules. By default, EyeLoop imports two base *extractors*, namely a FPS-counter and a data acquisition tool. To add custom extractors, e.g., for experimental purposes, use the argument tag ```--extractors```:

```
eyeloop --extractors [file_path]/p (where p = file prompt)
```

Inside the *extractor* file, or a composite python file containing several *extractors*, define the list of *extractors* to be added:
```python
extractors_add = [extractor1, extractor2, etc]
```

*Extractors* are instantiated by EyeLoop at start-up. Then, at every subsequent time-step, the *extractor's* ```fetch()``` function is called by the engine.
```python
class Extractor:
    def __init__(self) -> None:
        ...
    def fetch(self, core) -> None:
        ...
```
```fetch()``` gains access to all eye-tracking data in real-time via the *core* pointer.

> [Click here](https://github.com/simonarvin/eyeloop/blob/master/eyeloop/extractors/README.md) for more information on *extractors*.

### Open-loop example ###

As an example, we'll here design a simple *open-loop* experiment where the brightness of a PC monitor is linked to the phase of the sine wave function. We create anew python-file, say "*test_ex.py*", and in it define the sine wave frequency and phase using the instantiator:
```python
class Experiment:
    def __init__(self) -> None:
        self.frequency = ...
        self.phase = 0
```
Then, by using ```fetch()```, we shift the phase of the sine wave function at every time-step, and use this to control the brightness of a cv-render.
```python
    ...
    def fetch(self, engine) -> None:
        self.phase += self.frequency
        sine = numpy.sin(self.phase) * .5 + .5
        brightness = numpy.ones((height, width), dtype=float) * sine
        cv2.imshow("Experiment", brightness)
```

To add our test extractor to EyeLoop, we'll need to define an extractors_add array:
```python
extractors_add = [Experiment()]
```

Finally, we test the experiment by running command:
```
eyeloop --extractors path/to/test_ex.py
```

> See [Examples](https://github.com/simonarvin/eyeloop/blob/master/examples) for demo recordings and experimental designs.

> For extensive test data, see [*EyeLoop Playground*](https://github.com/simonarvin/eyeloop_playground)


## Data ##
EyeLoop produces a json-datalog for each eye-tracking session. The datalog's first column is the timestamp.
The next columns define the pupil (if tracked):

```((center_x, center_y), radius1, radius2, angle)```

The next columns define the corneal reflection (if tracked):

```((center_x, center_y), radius1, radius2, angle)```

The next columns contain any data produced by custom Extractor modules


## Graphical user interface ##
The default graphical user interface in EyeLoop is [*minimum-gui*.](https://github.com/simonarvin/eyeloop/blob/master/eyeloop/guis/minimum/README.md)

> EyeLoop is compatible with custom graphical user interfaces through its modular logic. [Click here](https://github.com/simonarvin/eyeloop/blob/master/eyeloop/guis/README.md) for instructions on how to build your own.

## Running unit tests ##

Install testing requirements by running in a terminal:

`pip install -r requirements_testing.txt`

Then run tox: `tox`

Reports and results will be outputted to `/tests/reports`


## Known issues ##
- [ ] Respawning/freezing windows when running *minimum-gui* in Ubuntu.

## References ##
If you use any of this code or data, please cite [Arvin et al. 2021] ([article](https://www.frontiersin.org/articles/10.3389/fncel.2021.779628/full)).
```latex

@ARTICLE{Arvin2021-tg,
  title    = "{EyeLoop}: An open-source system for high-speed, closed-loop
              eye-tracking",
  author   = "Arvin, Simon and Rasmussen, Rune and Yonehara, Keisuke",
  journal  = "Front. Cell. Neurosci.",
  volume   =  15,
  pages    = "494",
  year     =  2021
}

```

## License ##
This project is licensed under the GNU General Public License v3.0. Note that the software is provided "as is", without warranty of any kind, express or implied.

## Authors ##

**Lead Developer:**
Simon Arvin, sarv@dandrite.au.dk
<p align="right">
    <img src="https://github.com/simonarvin/eyeloop/blob/master/misc/imgs/constant.svg?raw=true" align="right" height="180">
    </p>

**Researchers:**

- Simon Arvin, sarv@dandrite.au.dk
- Rune Rasmussen, runerasmussen@biomed.au.dk
- Keisuke Yonehara, keisuke.yonehara@dandrite.au.dk

**Corresponding Author:**
Keisuke Yonehera, keisuke.yonehara@dandrite.au.dk</br></br>

---
<p align="center">
    <img src="https://github.com/simonarvin/eyeloop/blob/master/misc/imgs/aarhusuniversity.svg?raw=true" align="center" height="40">&nbsp;&nbsp;&nbsp;&nbsp;
    <img src="https://github.com/simonarvin/eyeloop/blob/master/misc/imgs/dandrite.svg?raw=true" align="center" height="40">&nbsp;&nbsp;&nbsp;&nbsp;
    <img src="https://github.com/simonarvin/eyeloop/blob/master/misc/imgs/nordicembl.svg?raw=true" align="center" height="40">
</p>
<p align="center">
    <a href="http://www.yoneharalab.com">
    <img src="https://github.com/simonarvin/eyeloop/blob/master/misc/imgs/yoneharalab.svg?raw=true" align="center" height="18">&nbsp;&nbsp;&nbsp;&nbsp;
    </a>
    </p>
