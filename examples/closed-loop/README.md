# Closed-loop experiment #

<p align="center">
    <img src="https://github.com/simonarvin/eyeloop/blob/master/misc/imgs/closed-loop.svg?raw=true" align="center" width=600>
    </br><sub align = "center"><b>Fig. Closed-loop experiment exhibiting properties of dynamical systems.</b> (A) Closed-loop experiment using reciprocal feedback. Monitor brightness is set as a function of the pupil area. (B) State velocity, v, depends on pupil area, A. (C) Four trials of the closed loop with differing parameters showing distinct dynamic behavior.</sub>
  </p>

One of EyeLoop’s most appealing applications is closed-loop experiments (Fig). To demonstrate this, we designed an extractor to use the pupil area to modulate the brightness of a monitor, in effect a reciprocal feedback loop: Here, the light reflex causes the pupil to dilate in dim settings, which causes the extractor to increase monitor brightness. In turn, this causes the pupil to constrict, causing the extractor to decrease brightness and return the experiment to its initial state.

The brightness formula contains four critical variables (Fig B): The rate of change, I, which is dependent on the pupil area, and its scalar, q. The velocity, v, which applies the rate of change to monitor brightness, and, the velocity friction, f, which decays the velocity towards zero. Interestingly, by varying these parameters, we observe behaviors characteristic of dynamical systems: For the reference and the slow decay trials, we find emergent limit-cycle oscillations (Fig C). This dynamic is dramatically impaired by a small scalar, and abolished in the low rate trial. These findings illustrate how a simple closed-loop experiment may generate self-sustaining dynamics emerging from the eyes engaging with the system, and the system engaging with the eyes.

## How to reproduce ##
