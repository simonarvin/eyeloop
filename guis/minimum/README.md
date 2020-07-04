# minimum-gui instructions #
*minimum-gui* is EyeLoop's default minimalistic graphical user interface. It operates with bare minimum processing overhead. In the present text, we describe how to utilize *minimum-gui*.

<p align="right">
<img src="https://github.com/simonarvin/eyeloop/blob/master/guis/minimum/graphics/instructions_md/start.svg?raw=true" align="right" width = "300">
</p>

**Overview**\
*minimum-gui* consists of two panels. The left panel contains the source video sequence and an eye-tracking preview. The right panel contains the binary filter of the pupil (top) and corneal reflections (bottom).

## Getting started ##
- **A**: Select the corneal reflections by hovering and key-pressing <kbd>2</kbd>, <kbd>3</kbd> or <kbd>4</kbd>. This initiates the tracking algorithm, which is rendered in the preview panel. Adjust binarization (key-press <kbd>W</kbd>/<kbd>S</kbd>) and gaussian (key-press <kbd>E</kbd>/<kbd>D</kbd>) parameters to improve detection. To switch between corneal reflections, key-press the corresponding index (for example, key-press <kbd>2</kbd> to modify corneal reflection "2").
- **B**: Select the pupil by hovering and key-pressing <kbd>1</kbd>. Similar to the corneal reflections, this initiates tracking. Adjust binarization (key-press <kbd>R</kbd>/<kbd>F</kbd>) and gaussian parameters (key-press <kbd>T</kbd>/<kbd>G</kbd>) for optimal detection. 
- **C**: To initiate the eye-tracking trial, key-press <kbd>Z</kbd> and confirm by key-pressing <kbd>Y</kbd>.

> Key-press "q" to stop tracking.

## Optional ##
### Rotation ###
<p align="right">
<img src="https://github.com/simonarvin/eyeloop/blob/master/guis/minimum/graphics/instructions_md/rotation.svg?raw=true" align="right" width = "200">
</p>
Since EyeLoop's conversion algorithm computes the angular coordinates of the eye based on the video sequence, users must align it to the horizontal and vertical real-world axes. To obtain alignment, key-press <kbd>O</kbd> or <kbd>P</kbd> to rotate the video stream in real-time.

> Note: EyeLoop's *converter* module contains a corrective function, that transforms the eye-tracking coordinates based on any given angle. This enables users to apply a rotational vector in post hoc analysis.

### Markers ###
To crudely remove interfering artefacts, pass command-line argument ```--markers 1``` when initiating EyeLoop. This enables *markers*, which are placed in pairs forming rectangles exempt from the eye-tracking algorithm. In *minimum-gui*, press <kbd>B</kbd> to place a marker, and press <kbd>V</kbd> to undo.

