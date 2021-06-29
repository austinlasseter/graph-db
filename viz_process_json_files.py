# -*- coding: utf-8 -*-

import shutil
import pandas as pd
import psutil
import time
from pathlib import Path
import multiprocessing as mp
from functools import partial
from contextlib import contextmanager
import gzip
import json


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


def repo_query(prime_repo, query_df):
    """
    Queries for related actors & repos, up to the 3rd circle
    Input: gharchive ID of flagged repository, df from previous function
    Returns: df of all connections, ready for pre-viz transformation
    """
    prime_repo = int(prime_repo)
    # Cirle 1
    first_actors = query_df[query_df["repo_id"] == prime_repo][
        "actor_id"
    ].unique()  # Make a list of actors touched by prime repo
    first_actors = set(first_actors)
    # Circle 2
    second_repos = []  # make a list of unique repos touched by those actors
    for actor in first_actors:
        second_repos += (
            query_df[query_df["actor_id"] == actor]["repo_id"].unique().tolist()
        )
    second_repos = set(second_repos)
    second_actors = []  # make a list of unique actors who touched those repos
    for repo in second_repos:
        second_actors += (
            query_df[query_df["repo_id"] == repo]["actor_id"].unique().tolist()
        )
    second_actors = set(second_actors)
    # Circle 3
    third_repos = []  # make a list of unique repos touched by those actors
    for actor in second_actors:
        third_repos += (
            query_df[query_df["actor_id"] == actor]["repo_id"].unique().tolist()
        )
    third_repos = set(third_repos)
    third_actors = []  # make a list of unique actors who touched those repos
    for repo in third_repos:
        third_actors += (
            query_df[query_df["repo_id"] == repo]["actor_id"].unique().tolist()
        )
    third_actors = set(third_actors)
    # Combine all 3 circles into a dataframe
    all_actors = first_actors.union(second_actors).union(third_actors)
    all_repos = set([prime_repo]).union(second_repos).union(third_repos)
    edgesdf = query_df[
        (query_df["actor_id"].isin(all_actors)) | (query_df["repo_id"].isin(all_repos))
    ]
    edgesdf = edgesdf.reset_index(drop=True)
    return edgesdf


def make_df(json_lines, prime_repo):
    """
    Opens each json object as a pandas dataframe
    Reduces it to the necessary columns
    Filters for rows that contain relevant data
    """
    rawdf = pd.DataFrame(json_lines)
    rawdf["actor_id"] = rawdf["actor"].apply(lambda row: row["id"])
    rawdf["repo_id"] = rawdf["repo"].apply(lambda row: row["id"])
    rawdf["actor_login"] = rawdf["actor"].apply(lambda row: row["login"])
    rawdf["repo_name"] = rawdf["repo"].apply(lambda row: row["name"])
    query_df = rawdf[["id", "type", "repo_id", "actor_id", "repo_name", "actor_login"]]
    query_df.columns = [
        "edge_id",
        "edge_type",
        "repo_id",
        "actor_id",
        "repo_name",
        "actor_login",
    ]
    edgesdf = repo_query(prime_repo, query_df)
    return edgesdf


def process_file(prime_repo, filename):
    """
    Opens each json object, converts to string & scans for the prime repo
    If not found, moves file to "no_hits" folder
    If found, converts to pandas dataframe and formats
    Returns processed dataframe
    """
    lines = []
    with gzip.open(filename, "rb") as f:
        for line in f:
            lines.append(json.loads(line))
    if str(lines).find(str(prime_repo)) == -1:
        print(filename, "aw, snap!")
        no_hits_path = Path.joinpath(filename.parent, "no_hits", filename.name)
        shutil.move(filename, no_hits_path)
        pass
    else:
        print(filename, "bingo!")
        edgesdf = make_df(lines, prime_repo)
        return edgesdf


def split_apply_combine(prime_repo, directory, pattern, processes=-1):
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
        dfs = pool.map(partial(process_file, prime_repo), files)
    processed_df = pd.concat(dfs, ignore_index=True)
    print("processed_df ", processed_df.shape)
    print("unique actors:", processed_df["actor_id"].nunique())
    print("unique repos:", processed_df["repo_id"].nunique())
    end = time.time()
    print("Completed in: %s sec" % (end - start))
    return processed_df


def process_json_files(analysis_name, prime_repo):
    """
    Receives json filesa and prime repo
    Produces csv file of query results
    """
    print("processing json files...")
    parent_dir = Path.joinpath(Path.cwd().parents[1], analysis_name)
    data_dir = Path.joinpath(parent_dir, "data")
    outfile_name = "{}_processed".format(prime_repo)
    outfile_path = Path.joinpath(parent_dir, "outputs", "{}.csv".format(outfile_name))
    finaldf = split_apply_combine(
        prime_repo, directory=data_dir, pattern="*.json.gz", processes=-1
    )
    finaldf.to_csv(outfile_path, index=False)
    print("Processed json files: ", outfile_path)
