import argparse
from pathlib import Path

EYELOOP_DIR = Path(__file__).parent.parent
PROJECT_DIR = EYELOOP_DIR.parent


class Arguments:
    """
    Parses all command-line arguments and config.pupt parameters.
    """

    def __init__(self, args) -> None:
        self.config = None
        self.markers = None
        self.video = None
        self.output_dir = None
        self.importer = None
        self.scale = None
        self.tracking = None
        self.model = None

        self.parsed_args = self.parse_args(args)
        self.build_config(parsed_args=self.parsed_args)

    @staticmethod
    def parse_args(args):
        parser = argparse.ArgumentParser(description='Help list')
        parser.add_argument("-v", "--video", default="0", type=str,
                            help="Input a video sequence for offline processing.")

        parser.add_argument("-o", "--output_dir", default=str(PROJECT_DIR.joinpath("data").absolute()), type=str,
                            help="Specify output destination.")
        parser.add_argument("-c", "--config", default="0", type=str, help="Input a .pupt config file (preset).")
        parser.add_argument("-i", "--importer", default="cv", type=str,
                            help="Set import route of stream (cv, vimba, ...)")
        parser.add_argument("-sc", "--scale", default=1, type=float, help="Scale the stream (default: 1; 0-1)")
        parser.add_argument("-m", "--model", default="ellipsoid", type=str,
                            help="Set pupil model type (circular; ellipsoid = default).")
        parser.add_argument("-ma", "--markers", default=0, type=int,
                            help="Enable/disable artifact removing markers (0: disable/default; 1: enable)")
        parser.add_argument("-tr", "--tracking", default=1, type=int,
                            help="Enable/disable tracking (1/enabled: default).")
        parser.add_argument("-bt", "--bthreshold", default=-1, type=float,
                            help="Set blink threshold manually (0-255).")

        return parser.parse_args(args)

    def build_config(self, parsed_args):
        self.config = parsed_args.config

        if self.config != "0":  # config file was set.
            self.parse_config(self.config)

        self.markers = parsed_args.markers
        self.video = Path(parsed_args.video.strip("\'\"")).absolute()  # Handle quotes used in argument
        self.output_dir = Path(parsed_args.output_dir.strip("\'\"")).absolute()
        self.importer = parsed_args.importer.lower()
        self.scale = parsed_args.scale
        self.tracking = parsed_args.tracking
        self.model = parsed_args.model.lower()
        self.bthreshold = parsed_args.bthreshold

    def parse_config(self, config: str) -> None:
        with open(config, "r") as content:
            print("Loading config preset: ", config)
            for line in content:
                split = line.split("=")
                parameter = split[0]
                parameter = split[1].rstrip("\n").split("\"")

                if len(parameter) != 1:
                    parameter = parameter[1]
                else:
                    parameter = parameter[0]

                if parameter == "video":
                    print("Video preset: ", parameter)
                    self.video = parameter
                elif parameter == "dest":
                    print("Destination preset: ", parameter)
                    self.output_dir = Path(parameter).absolute()

                elif parameter == "import":
                    print("Importer preset: ", parameter)
                    self.importer = parameter
                elif parameter == "model":
                    print("Model preset: ", parameter)
                    self.model = parameter
                elif parameter == "markers":
                    print("Markers preset: ", parameter)
                    self.markers = parameter
            print("")
