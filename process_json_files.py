# -*- coding: utf-8 -*-


import pandas as pd
import psutil
import time
from pathlib import Path
import multiprocessing as mp
from contextlib import contextmanager
import gzip
import json
import numpy as np


@contextmanager
def poolcontext(*args, **kwargs):
    pool = mp.Pool(*args, **kwargs)
    yield pool
    pool.terminate()


def get_files(directory, pattern):
    """
    Receives filepath
    Pattern indicates only json.gz files
    produces list of filepaths for each file
    """
    for path in Path(directory).rglob(pattern):
        yield path.absolute()


def make_edgesdf(json_lines):
    """
    Opens each json object as a pandas dataframe
    Reduces it to the necessary columns, find unique repos/actors
    Creates two dataframes - edges and nodes - per Neptune reqs
    """
    rawdf = pd.DataFrame(json_lines)
    # feature engineering
    rawdf["repo_id"] = rawdf["actor"].apply(lambda row: row["id"])
    rawdf["actor_id"] = rawdf["repo"].apply(lambda row: row["id"])
    rawdf["actor_login"] = rawdf["actor"].apply(lambda row: row["login"])
    rawdf["repo_name"] = rawdf["repo"].apply(lambda row: row["name"])
    edgesdf = rawdf[["id", "type", "repo_id", "actor_id", "repo_name", "actor_login"]]
    edgesdf.columns = ["id", "label", "from", "to", "repo_name", "actor_login"]
    # get unique repos & actors
    repos = rawdf.groupby("repo_id")["repo_name"].first()
    actors = rawdf.groupby("actor_id")["actor_login"].first()
    # make labels
    nodesdf = pd.concat([repos, actors], axis=1)
    nodesdf = nodesdf.reset_index(drop=False)
    nodesdf["type"] = np.where(nodesdf["repo_name"].isnull(), "actor", "repo")
    nodesdf["label"] = np.where(
        nodesdf["repo_name"].isnull(), nodesdf["actor_login"], nodesdf["repo_name"]
    )
    nodesdf = nodesdf.drop(["actor_login", "repo_name"], axis=1)
    return edgesdf, nodesdf


def process_file(filename):
    """
    Opens each json object, converts to string
    Converts to pandas dataframe and formats
    Returns processed dataframe
    """
    lines = []
    with gzip.open(filename, "rb") as f:
        for line in f:
            lines.append(json.loads(line))
    edgesdf, nodesdf = make_edgesdf(lines)
    return edgesdf, nodesdf


def split_apply_combine(directory, pattern, processes=-1):
    """
    Opens each json.gz file, searches and processes it
    Apply multiprocessing for efficiency
    Combine outputs into a single pandas dataframe
    """
    # Decide how many processes will be created
    if processes <= 0:
        num_cpus = psutil.cpu_count(logical=False)
    else:
        num_cpus = processes

    # Get files based on pattern "json.gz"
    files = []
    for file in get_files(directory=directory, pattern=pattern):
        files.append(file)
    start = time.time()

    # Create the pool
    with poolcontext(processes=num_cpus) as pool:
        edge_dfs_list, node_dfs_list = zip(*pool.map(process_file, files))
    processed_edgesdf = pd.concat(edge_dfs_list, ignore_index=True)
    processed_nodesdf = pd.concat(node_dfs_list, ignore_index=True)
    processed_nodesdf = processed_nodesdf.groupby("index").first()
    processed_nodesdf = processed_nodesdf.reset_index(drop=False)
    end = time.time()
    print("Completed in: %s sec" % (end - start))
    return processed_edgesdf, processed_nodesdf


def process_json_files(analysis_name):
    """
    Receives json files and compiles them
    Produces 2 csv files for in format expected by Amazon Neptune
    """
    print("processing json files...")
    parent_dir = Path.joinpath(Path.cwd().parents[1], analysis_name)
    data_dir = Path.joinpath(parent_dir, "data")
    edges_outfile_name = "{}_edges_processed".format(analysis_name)
    nodes_outfile_name = "{}_nodes_processed".format(analysis_name)
    edges_outfile_path = Path.joinpath(
        parent_dir, "outputs", "{}.csv".format(edges_outfile_name)
    )
    nodes_outfile_path = Path.joinpath(
        parent_dir, "outputs", "{}.csv".format(nodes_outfile_name)
    )
    processed_edgesdf, processed_nodesdf = split_apply_combine(
        directory=data_dir, pattern="*.json.gz", processes=-1
    )
    processed_edgesdf.to_csv(edges_outfile_path, index=False)
    processed_nodesdf.to_csv(nodes_outfile_path, index=False)
    print("Finished processing json files: ", edges_outfile_path)
