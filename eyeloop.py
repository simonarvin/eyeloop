import sys
sys.path.append('../')

from engine.engine import Engine

from importers.vimba import Importer

from utilities.format_print import clear, welcome
from utilities.argument_parser import Arguments
from utilities.file_manager import File_Manager

from extractors.DAQ import DAQ_extractor
from extractors.frametimer import FPS_extractor

from guis.minimum.minimum_gui import GUI


class EyeLoop:
    """
    EyeLoop is a Python 3-based eye-tracker tailored specifically to dynamic, closed-loop experiments on consumer-grade hardware.
    Lead developer: Simon Arvin
    Git: https://github.com/simonarvin/eyeloop
    """
    def __init__(self):

        welcome("Server")

        arguments = Arguments()
        file_manager = File_Manager(dir = arguments.destination)
        print(arguments.video)
        graphical_user_interface = GUI()

        ENGINE = Engine(self, graphical_user_interface, file_manager, arguments)

        fps_counter = FPS_extractor()
        data_acquisition = DAQ_extractor(file_manager.new_folderpath)


        extractors = [fps_counter, data_acquisition]
        ENGINE.load_extractors(extractors)

        try:
            print("Initiating tracking via {}".format(arguments.importer))
            import_command = "from importers.{} import Importer".format(arguments.importer)
            exec(import_command, globals())
        except Exception as e:
            print("Invalid importer selected.\n", e)

        importer = Importer(ENGINE)

        importer.route()


if __name__ == '__main__':

    EyeLoop()
