import os
from datetime import datetime
from pathlib import Path
from shutil import rmtree


def get_data_dir():
    file_dir = Path(os.path.dirname(os.path.realpath(__file__)))
    data_dir = f"{file_dir.parents[2]}/data"
    data_dir = data_dir.replace("//","/")
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    return data_dir

def remove_local_artifacts():
    file_dir = Path(os.path.dirname(os.path.realpath(__file__)))
    proj_dir = file_dir.parents[1]

    unwanted_fols = ["mlartifacts","mlruns"]

    for fol in unwanted_fols:
        if os.path.exists(f"{proj_dir}/{fol}"):
            rmtree(Path(f"{proj_dir}/{fol}"))
    
    for root, dirs, files in os.walk(proj_dir, topdown=False):
        if "__pycache__" in root:
            rmtree(root)
    
    return None

def format_time():
    timenw = str(datetime.now()).split(".")[0]
    fmt = datetime.strptime(timenw, "%Y-%m-%d %H:%M:%S")
    return fmt