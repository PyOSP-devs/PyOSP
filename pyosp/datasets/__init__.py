import os

__all__ = ["_available_file", "get_path"]

_module_path = os.path.dirname(__file__)
_available_file = [p for p in os.listdir(_module_path) if not p.startswith("__")]  

def get_path(dataset):
    if dataset in _available_file:
        return os.path.abspath(os.path.join(_module_path, dataset))
    else:
        msg = "The dataset '{data}' is not available. ".format(data=dataset)
        msg += "Available datasets are {}".format(", ".join(_available_file))
        raise ValueError(msg)
