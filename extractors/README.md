# Extractors #

<p align="right">
    <img src="https://github.com/simonarvin/eyeloop/blob/master/misc/imgs/extractor_overview.svg?raw=true" align="right" width = "450">
  </p>

Extractors form the *executive branch* of EyeLoop: Experiments, such as open- or closed-loops, are designed using Extractors. Similarly, data acquisition utilizes the Extractor class. So how does it work?

## Structure ##
To do.

## Utilization ##

Extractors are utilized by EyeLoop's *Engine* via the *Extractor array*. Users must first *load* all extractors into the Engine via *EyeLoop.py*:
```python
class EyeLoop:
    def __init__(self) -> None:
        extractors = [...]
        ENGINE = Engine(...)
        ENGINE.load_extractors(extractors)
```

The Extractor array is *activated* by the Engine when the trial is initiated:
```python
def activate(self) -> None:
        for extractor in self.extractors:
            extractor.activate()
```

Finally, at every time-step, the Engine calls the Extractor ```fetch()``` function:
```python
def fetch(self, engine) -> None:
    (do something)
    ...
```
The ```fetch()``` function has access to all eye-tracking data as it is computed via the Engine pointer, engine.            
