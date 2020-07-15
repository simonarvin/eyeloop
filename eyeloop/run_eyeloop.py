from eyeloop.engine.engine import Engine

from eyeloop.utilities.format_print import welcome
from eyeloop.utilities.argument_parser import Arguments
from eyeloop.utilities.file_manager import File_Manager

from eyeloop.extractors.DAQ import DAQ_extractor
from eyeloop.extractors.frametimer import FPS_extractor

from eyeloop.guis.minimum.minimum_gui import GUI

import eyeloop.config as config


class EyeLoop:
    """
    EyeLoop is a Python 3-based eye-tracker tailored specifically to dynamic, closed-loop experiments on consumer-grade hardware.
    Lead developer: Simon Arvin
    Git: https://github.com/simonarvin/eyeloop
    """

    def __init__(self):

        welcome("Server")

        config.arguments = Arguments()
        config.file_manager = File_Manager(output_root=config.arguments.output_dir)

        config.graphical_user_interface = GUI()

        config.engine = Engine(self)

        fps_counter = FPS_extractor()
        data_acquisition = DAQ_extractor(config.file_manager.new_folderpath)

        extractors = [fps_counter, data_acquisition]
        config.engine.load_extractors(extractors)

        try:
            print("Initiating tracking via {}".format(config.arguments.importer))
            import_command = "from eyeloop.importers.{} import Importer".format(config.arguments.importer)

            exec(import_command, globals())

        except Exception as e:
            print("Invalid importer selected.\n", e)

        config.importer = Importer()
        config.importer.route()


if __name__ == '__main__':
    EyeLoop()
