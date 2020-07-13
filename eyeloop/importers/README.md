# Importers #
<p align="right">
    <img src="https://github.com/simonarvin/eyeloop/blob/master/misc/imgs/importer_overview.svg?raw=true" align="right" height="250">
    </p>

To use a video sequence for eye-tracking, we use an *importer* class as a bridge to EyeLoop's engine. The importer fetches the video sequence from the camera, or offline from a directory, and imports it. Briefly, the importer main class ```IMPORTER``` includes functions to rotate, resize and save the video stream. Additionally, it *arms* the engine by passing neccesary variables.

## Why use an importer? ##
The reason for using an *importer* class, rather than having video importation "*built-in*", is to avoid incompatibilities. For example, while most web-cameras are compatible with opencv (importer *cv*), Vimba-based cameras (Allied Vision cameras), are not. Thus, by modularizing the importation of image frames, EyeLoop is easily integrated in markedly different setups.

## Importers ##

- Most cameras are compatible with the *cv Importer* (default).
- Allied Vision cameras require the Vimba-based *Importer*, *vimba*.

## Building your first custom importer ##
To build our first custom importer, we instantiate our *Importer* class:
```python
class Importer(IMPORTER):
    def __init__(self) -> None:
        self.scale = config.arguments.scale
```
Here, we define critical variables, such as scaling. Then, we load the first frame, retrieve its dimensions and, lastly, *arm* the engine:

```python
        ...
        (load image)
        width, height = (image dimensions)
        self.arm(width, height, image)
```
Finally, the ```route()``` function loads the video frames and passes them to the engine sequentially:
```python
def route(self) -> None:
        while True:
            image = ...
            config.engine.update_feed(image)
            self.frame += 1
```
Optionally, add a ```release()``` function to control termination of the importation process:
```python
def release(self) -> None:
        terminate()
```

That's it!
> Consider checking out [*cv Importer*](https://github.com/simonarvin/eyeloop/blob/master/importers/cv.py) as a code example.
