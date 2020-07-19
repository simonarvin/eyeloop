import logging
import logging.config
import os
import sys
from datetime import datetime
from pathlib import Path

import yaml


def setup_logging(log_config_path=f"{Path(__file__).parent}/logging_config.yaml", log_dir="logs", module_name=None,
                  default_level=logging.INFO) -> (logging.Logger, str):
    """
    Setup logging configuration. Returns logger object.

    :param log_config_path: Path to logging config yaml file
    :param log_dir: Directory that log files will be written into (relative or full path)
    :param module_name: Module name to append to log filename. If none given __name__ will be used.
    :param default_level: Default level of logging.
    :returns: Tuple of (the newly created logging object, path to log file (possibly None if no config was found))
    """
    log_filename = None

    # Check for permissions and change log dir if write access isn't granted
    try:
        if Path(log_dir).exists() is False:
            print(f"log dir not found, Attempting to create dir {log_dir}")
            Path(log_dir).mkdir(parents=True, exist_ok=True)
    except PermissionError:
        log_dir = Path("C:/Temp", "coronaSEIR", "logs")
        print(f"WARNING: Not enough permissions to write to log_dir given. Writing to {log_dir} instead.")

    print(f"Writing log to {Path(log_dir).absolute()}")

    if module_name is None:
        module_name = __name__

    if os.path.exists(log_config_path):
        with open(log_config_path, 'rt') as f:
            config = yaml.safe_load(f.read())

        # Set
        for handler_name, handler in config["handlers"].items():
            if handler_name != "console":
                log_filename = rf"{log_dir}/{datetime.now().strftime('%Y-%m-%d-%H%M%S')}_{module_name}.log"
                handler["filename"] = log_filename

        logging.config.dictConfig(config)

    else:
        raise ValueError(f"Loading logger config failed from {log_config_path} for module {module_name}")

    new_logger = logging.getLogger(module_name)

    # # Catch all unhandled exceptions and log
    # def handle_exception(exc_type, exc_value, exc_traceback):
    #     if issubclass(exc_type, KeyboardInterrupt):
    #         sys.__excepthook__(exc_type, exc_value, exc_traceback)
    #         return
    #
    #     new_logger.error("Uncaught exception! Traceback shown below:", exc_info=(exc_type, exc_value, exc_traceback))
    #     raise exc_type(exc_value)

    # sys.excepthook = handle_exception
    return new_logger, log_filename
