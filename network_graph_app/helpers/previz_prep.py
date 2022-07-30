# -*- coding: utf-8 -*-
import pandas as pd
import json
from pathlib import Path


def prep_dictionary(edgesdf):
    """
    Translate gharchive ID's to continuous integers
    Input: Query results from previous step as pandas dataframe
    Returns: Pandas dataframe of all connections (i.e., "edges")
    """
    # actors
    actor_elems = edgesdf["actor_id"].unique()
    nums = range(len(actor_elems))
    actors_map = list(zip(actor_elems, nums))
    actors_dict = dict(actors_map)
    # repos
    repo_elems = edgesdf["repo_id"].unique()
    nums = range(
        len(actors_map),
        len(repo_elems) + len(actors_map),
    )
    repos_map = list(zip(repo_elems, nums))
    repos_dict = dict(repos_map)
    # create nodes
    edgesdf["actor_node"] = edgesdf["actor_id"].apply(lambda x: actors_dict[x])
    edgesdf["repo_node"] = edgesdf["repo_id"].apply(lambda x: repos_dict[x])
    # create edges

    def f(x):
        actor_id = x["actor_id"]
        repo_id = x["repo_id"]

        return (actors_dict[actor_id], repos_dict[repo_id])

    edgesdf["edge"] = edgesdf.apply(f, axis=1)
    print("edgesdf", edgesdf.head(2).T)
    return edgesdf


def transform_4viz(prime_repo, edgesdf):
    """
    Using igraph, produce (x,y) coordinates in format expected by igraph
    Input: Processed results from previous step as pandas dataframe
    Returns: Python dictionary that is ready for igraph
    """
    prime_node = int(
        edgesdf[edgesdf["repo_id"] == prime_repo]["repo_node"].value_counts().index[0]
    )

    edges = edgesdf["edge"].tolist()
    edge_types = edgesdf["edge_type"].tolist()
    nodes = (
        edgesdf["actor_node"].unique().tolist() + edgesdf["repo_node"].unique().tolist()
    )
    ids = (
        edgesdf["actor_login"].unique().tolist()
        + edgesdf["repo_name"].unique().tolist()
    )

    tags = ["actor"] * len(edgesdf["actor_id"].unique().tolist()) + ["repo"] * len(
        edgesdf["repo_id"].unique().tolist()
    )
    labels = list(zip(tags, ids))
    classes = ["actor"] * len(edgesdf["actor_id"].unique().tolist()) + ["repo"] * len(
        edgesdf["repo_id"].unique().tolist()
    )

    # save as json
    edges_nodes = {
        "edges": edges,
        "edge_types": edge_types,
        "nodes": nodes,
        "classes": classes,
        "labels": labels,
        "prime_node": prime_node,
    }
    print(edges_nodes.keys())
    print(edges_nodes["labels"][0])
    print(edges_nodes["labels"][-1])
    return edges_nodes


def previz_prep(analysis_name, prime_repo):
    """
    Receives pandas dataframe
    Returns a json object  properly formatted for  network graph
    """

    print("preparing query results...")
    prime_repo = int(prime_repo)
    infile_path = Path.joinpath(
        Path.cwd().parents[1],
        analysis_name,
        "outputs",
        "{}_processed.csv".format(prime_repo),
    )
    outfile_name = "{}_query_results.json".format(prime_repo)
    outfile_path = Path.joinpath(
        Path.cwd().parents[1], analysis_name, "outputs", outfile_name
    )
    edgesdf = pd.read_csv(infile_path)
    edgesdf = prep_dictionary(edgesdf)
    json_results = transform_4viz(prime_repo, edgesdf)

    with open(outfile_path, "w") as outfile:
        json.dump(json_results, outfile)
    print(outfile_path)
