# Extractors #

<p align="right">
    <img src="https://github.com/simonarvin/eyeloop/blob/master/misc/imgs/extractor_overview.svg?raw=true" align="right" width = "450">
  </p>

*Extractors* form the *executive branch* of EyeLoop: Experiments, such as open- or closed-loops, are designed using *Extractors*. Similarly, data acquisition utilizes the *Extractor* class. So how does it work?

> Check [Examples](https://github.com/simonarvin/eyeloop/blob/master/examples) for full Extractors.

## How the *Engine* handles *Extractors* ##

*Extractors* are utilized by EyeLoop's *Engine* via the *Extractor array*. Users must first *load* all extractors into the *Engine* via *run_eyeloop.py*:
```python
class EyeLoop:
    def __init__(self) -> None:
        extractors = [...]
        ENGINE = Engine(...)
        ENGINE.load_extractors(extractors)
```

The *Extractor array* is *activated* by the *Engine* when the trial is initiated:
```python
class Engine:
    def activate(self) -> None:
            for extractor in self.extractors:
                extractor.activate()
```

Finally, the *Extractor array* is loaded by the *Engine* at each time-step:
```python
    def run_extractors(self) -> None:
            for extractor in self.extractors:
                    extractor.fetch(self)
```

At the termination of the *Engine*, the *Extractor array* is *released*:
```python
    def release(self) -> None:
            for extractor in self.extractors:
                extractor.release()
```

## Structure ##
The *Extractor* class contains four functions:
### 1: ```__init__``` ###

The instantiator sets class variables as soon as the Extractor array is generated, i.e., before the trial has begun.
```python
    class Extractor:
        def __init__(self, ...):
            (set variables)
```

### 2: ```activate``` ###

The ```activate()``` function is called once when the trial is started.
```python
    ...
        def activate(self):
            ...
```

An experiment *Extractor* might activate the experiment when the trial is initiatiated, by resetting timers:
```python
    ...
        def activate(self) -> None:
            self.start = time.time()
```

### 3: ```fetch``` ###

<p align="center">
    <img src="https://github.com/simonarvin/eyeloop/blob/master/misc/imgs/extractor_scheme.svg?raw=true" align="center" width = "350">
  </p>

The ```fetch()``` function is called at the end of every time-step. It receives the *Engine* pointer, gaining access to all eye-tracking data in real-time.
```python
    ...
        def fetch(self, Engine):
            ...
```

A data acquisition *Extractor* would fetch the data via ```Engine.dataout``` and save it, or pass it to a dedicated data acquisition board.
```python
    ...
        def fetch(self, Engine):
            self.log.write(json.dumps(Engine.dataout) + "\n")
```

### 4: ```release``` ###

The ```release()``` function is called when the *Engine* is terminated.
```python
    ...
        def release(self):
            ...
```
