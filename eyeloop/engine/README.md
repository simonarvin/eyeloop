# Engine #
<p align="right">
    <img src="https://github.com/simonarvin/eyeloop/blob/master/misc/imgs/engine_ill.svg?raw=true" align="right" height="300">
  </p>

The engine processes each frame of the video sequentially. First, the user selects the corneal reflections, then the pupil. The frame is binarized, filtered, and smoothed by a gaussian kernel. Then, the engine utilizes a walk-out algorithm to detect contours. This produces a matrix of points, which is filtered to discard bad matches. Using the corneal reflections, any overlap between the corneal reflections and the pupil is removed. Finally, the shape is parameterized by a fitting model: either an ellipsoid (suitable for rodents, cats, etc.), or a circle model (human, non-human primates, rodents, etc.). The target species is easily changed:
```
python eyeloop/run_eyeloop.py --model circular/ellipsoid
```
Lastly, the data is formatted in JSON and passed to all modules, such as for rendering, or data acquisition and experiments.

## Shape processors ##
EyeLoop's engine communicates with the *Shape* class, which processes the walkout contour detection. Accordingly, at least two *Shape*'s are defined by the instantiator, one for the pupil and *n* for the corneal reflections:

```python
class Engine:
    def __init__(self, ...):
        max_cr_processor = 3 #max number of corneal reflections
        self.cr_processors  =   [Shape(self, type = 2) for _ in range(max_cr_processor)]
        self.pupil_processor=   Shape(self)
        ...

```
