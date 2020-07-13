import json
from tkinter import filedialog

import numpy as np
from interfaces.converter import Conversion_extractor


class Parser():
    data = []
    file_path = ""

    def __init__(self, animal: str) -> None:
        self.animal = animal

    def load_log(self, file_path="") -> None:
        if file_path == "":
            file_path = filedialog.askopenfilename(filetypes=(("json files", "*.json"), ("all files", "*.*")))

        try:
            file = open(file_path, "r")
        except FileNotFoundError:
            print("Please select a valid log.")
        self.file_path = file_path

        for line in file.readlines():
            self.data.append(json.loads(line))
        file.close()

    def crop(self, start, end=-1):
        if end != -1:
            self.data = self.data[start:end]
        else:
            self.data = self.data[start:]

    def compute_area(self) -> np.ndarray:
        converter = Conversion_extractor("area", self.animal)
        return np.array([converter.fetch(entry) for entry in self.data])

    def compute_coordinates(self) -> np.ndarray:
        converter = Conversion_extractor("coordinates", self.animal)
        return np.array([converter.fetch(entry) for entry in self.data])

    def extract_time(self) -> np.ndarray:
        return np.array([entry["time"] for entry in self.data])

    def extract_frame(self) -> np.ndarray:
        return np.array([entry["frame"] for entry in self.data])

    def extract_unique_key(self, key: str) -> np.ndarray:
        extract = []
        for entry in self.data:
            try:
                extract.append(entry[key])
            except:
                pass  # key not in log entry. Skip to next.
        return np.array(extract)

    def to_csv(self):
        try:
            import pandas as pd
        except:
            print("Please make sure that pandas is installed (pip install pandas).")

        file = pd.read_json(self.file_path, lines=True)
        new_path = self.file_path + "_csv"
        file.to_csv(new_path, index=None)
        print("Json succesfully converted to csv.")
        print("Csv saved at {}".format(new_path))
