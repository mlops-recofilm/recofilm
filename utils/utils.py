import os
import pickle
import pandas as pd


def make_directory(directory):
    """
    Create a directory if it doesn't exist.

    Args:
        directory (str): The path of the directory to be created.

    Returns:
        None
    """
    if not (os.path.exists(directory)):
        os.makedirs(directory)


def save_object(filepath, fileobject):
    """
    Save a Python object using pickle.

    Args:
        filepath (str): The path to save the object.
        fileobject (object): The Python object to be saved.

    Returns:
        None
    """
    with open(filepath, "wb") as f:
        pickle.dump(fileobject, f)


def load_object(filepath):
    """
    Load a Python object from a pickle file.

    Args:
        filepath (str): The path of the file containing the pickle object.

    Returns:
        object: The loaded Python object.
    """
    with open(filepath, "rb") as f:
        obj = pickle.load(f)
    return obj


def month_diff(input, output=None):
    """
    Calculate the number of months between two dates.

    Args:
        input (pd.Timestamp): The input date.
        output (pd.Timestamp, optional): The output date. Default is None, which corresponds to "2016-01-01".

    Returns:
        int: The number of months between the input and output dates.
    """
    if output is None:
        output = pd.Timestamp("2016-01-01")
    return 12 * (output.year - input.year) + (output.month - input.month)


def year_diff(input, output=None):
    """
    Calculate the number of years between two dates.

    Args:
        input (pd.Timestamp): The input date.
        output (pd.Timestamp, optional): The output date. Default is None, which corresponds to "2016-01-01".

    Returns:
        int: The number of years between the input and output dates.
    """
    return int(month_diff(input, output)/12)
