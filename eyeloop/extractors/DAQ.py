import json
import time


class DAQ_extractor:
    def __init__(self, dir):
        self.dir = dir
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = "{}/log{}.json".format(dir, timestamp)
        self.log = open(filename, 'w')

    def fetch(self, engine):
        try:
            self.log.write(json.dumps(engine.dataout) + "\n")
        except:
            pass

    def release(self):
        self.log.close()

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
