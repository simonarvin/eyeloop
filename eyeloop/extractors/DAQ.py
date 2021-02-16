import json
import logging
from pathlib import Path


class DAQ_extractor:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        self.datalog_path = Path(output_dir, f"datalog.json")
        self.file = open(self.datalog_path, "a")

    def activate(self):
        return

    def fetch(self, core):
        try:
            self.file.write(json.dumps(core.dataout) + "\n")

        except ValueError:
            pass

    def release(self, core):
        try:
            self.file.write(json.dumps(core.dataout) + "\n")
            self.file.close()
        except ValueError:
            pass
        self.fetch(core)
        #return
        #logging.debug("DAQ_extractor.release() called")

    # def set_digital_line(channel, value):
    # digital_output = PyDAQmx.Task()
    # digital_output.CreateDOChan(channel,'do', DAQmxConstants.DAQmx_Val_ChanPerLine)
    # digital_output.WriteDigitalLines(1,
    #                                 True,
    #                                 1.0,
    #                                 DAQmxConstants.DAQmx_Val_GroupByChannel,
    #                                 numpy.array([int(value)], dtype=numpy.uint8),
    #                                 None,
    #                                 None)
    # digital_output.ClearTask()
