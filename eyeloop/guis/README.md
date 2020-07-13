# Building your first custom graphical user interface #
.. in progress ..

To integrate a custom graphical user interface, pass it to the engine in eyeloop.py:
```python
graphical_user_interface = ...
ENGINE = Engine(self, graphical_user_interface, file_manager, arguments)
```
The graphical user interface should contain a ```load_engine(self, ENGINE)``` function:
```python
def load_engine(self, ENGINE) -> None:
        self.ENGINE = ENGINE
        ...
```

The graphical user interface is responsible for:
- Selecting corneal reflections (array ```ENGINE.cr_processors```).
- Selecting the pupil (Shape object ```ENGINE.pupil_processor```).
- Adjusting binarization and gaussian parameters (via ```ENGINE.cr_processors``` and ```ENGINE.pupil_processor```).
- Rotating the video feed (via ```ENGINE.angle```).

Additional functions are easily integrated.
