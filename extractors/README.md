# Extractors #

<p align="right">
    <img src="https://github.com/simonarvin/eyeloop/blob/master/misc/imgs/extractor_overview.svg?raw=true" align="right" width = "450">
  </p>

Extractors form the *executive branch* of EyeLoop: Experiments, such as open- or closed-loops, are designed using Extractors. Similarly, data acquisition utilizes the Extractor class. So how does it work?

## Why use an Extractor ##
To do.

## Context ##

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
class Engine:
    def activate(self) -> None:
            for extractor in self.extractors:
                extractor.activate()
```

Finally, the Extractor array is loaded by the Engine at each time-step:
```python
    def run_extractors(self) -> None:
            for extractor in self.extractors:
                    extractor.fetch(self)
```

At the termination of the Engine, the Extractor array is *released*:
```python
    def release(self) -> None:
            for extractor in self.extractors:
                extractor.release()
```

## Building your first custom Extractor ##
To do.
