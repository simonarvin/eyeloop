# Constants #

<p align="right">
    <img src="https://github.com/simonarvin/eyeloop/blob/master/misc/imgs/constant.svg?raw=true" align="right" width = "350">
  </p>

EyeLoop's engine, *Shape* processors, and *minimum-gui* have constants, that are rarely changed in updates. These include:
- Color scheme (*minimum-gui*).
- Walk-out parameters (steps, angular increments)
- Corneal reflection filtering parameters.

The constants are static during run-time, but users are free to modify them.
> Hint: Consider playing around with the walk-out parameters (*engine_constants.py*) to improve detection in your recordings.
