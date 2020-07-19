import importlib
import logging
import sys
from pathlib import Path

import eyeloop.config as config
from eyeloop.engine.engine import Engine
from eyeloop.extractors.DAQ import DAQ_extractor
from eyeloop.extractors.frametimer import FPS_extractor
from eyeloop.guis.minimum.minimum_gui import GUI
from eyeloop.utilities.argument_parser import Arguments
from eyeloop.utilities.file_manager import File_Manager
from eyeloop.utilities.format_print import welcome
from eyeloop.utilities.shared_logging import setup_logging

EYELOOP_DIR = Path(__file__).parent
PROJECT_DIR = EYELOOP_DIR.parent

logger = logging.getLogger(__name__)


class EyeLoop:
    """
    EyeLoop is a Python 3-based eye-tracker tailored specifically to dynamic, closed-loop experiments on consumer-grade hardware.
    Lead developer: Simon Arvin
    Git: https://github.com/simonarvin/eyeloop
    """

    def __init__(self, args, logger=None):

        welcome("Server")

        config.arguments = Arguments(args)
        config.file_manager = File_Manager(output_root=config.arguments.output_dir)
        if logger is None:
            logger, logger_filename = setup_logging(log_dir=config.file_manager.new_folderpath, module_name="run_eyeloop")

        config.graphical_user_interface = GUI()

        config.engine = Engine(self)

        fps_counter = FPS_extractor()
        data_acquisition = DAQ_extractor(config.file_manager.new_folderpath)

        extractors = [fps_counter, data_acquisition]
        config.engine.load_extractors(extractors)

        try:
            logger.info(f"Initiating tracking via Importer: {config.arguments.importer}")
            importer_module = importlib.import_module(f"eyeloop.importers.{config.arguments.importer}")
            config.importer = importer_module.Importer()
            config.importer.route()

            # exec(import_command, globals())

        except ImportError:
            logger.exception("Invalid importer selected")


if __name__ == '__main__':
    EyeLoop(sys.argv[1:], logger=None)
