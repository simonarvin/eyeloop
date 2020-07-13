import numpy as np


def distance(p1: np.ndarray, p2: np.ndarray) -> np.ndarray:
    return np.linalg.norm(p1 - p2)


def to_int(non_int: float) -> int:
    return int(non_int + 0.5)


def tuple_int(non_int: tuple) -> tuple:
    return tuple(int(element + 0.5) for element in non_int)


def check_path_type(path) -> str:
    if path == "0":
        return "file"  # live camera stream

    str = path.split("/")
    # str = str.split("\\")

    lastslash = str[len(str) - 1]
    ext = lastslash.split(".")
    if lastslash == ext[0]:
        return "folder"
    else:
        return "file"
