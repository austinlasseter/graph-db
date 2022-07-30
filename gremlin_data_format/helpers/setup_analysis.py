# -*- coding: utf-8 -*-
from pathlib import Path
import os


def make_dirs(analysis_name):

    """
    Creates a folder structure that is unique to each analysis
    Folders are located above and outside of the git repository to reduce clutter
    """
    print("initializing folder setup...")
    primary_dir = Path.joinpath(Path.cwd().parents[1], str(analysis_name))
    data_dir = Path.joinpath(Path.cwd().parents[1], str(analysis_name), "data")
    no_hits_dir = Path.joinpath(
        Path.cwd().parents[1], str(analysis_name), "data", "no_hits"
    )
    outputs_dir = Path.joinpath(Path.cwd().parents[1], str(analysis_name), "outputs")

    Path(primary_dir).mkdir(parents=True, exist_ok=True)
    Path(data_dir).mkdir(parents=True, exist_ok=True)
    Path(no_hits_dir).mkdir(parents=True, exist_ok=True)
    Path(outputs_dir).mkdir(parents=True, exist_ok=True)
    os.chdir(data_dir)

    return data_dir
