import json
import logging
from pathlib import Path


class DAQ_extractor:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        self.datalog_path = Path(output_dir, f"datalog.json")

    def activate(self):
        return

    def fetch(self, engine):
        with open(self.datalog_path, "a") as datalog:
            datalog.write(json.dumps(engine.dataout) + "\n")

    def release(self):
        return
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
