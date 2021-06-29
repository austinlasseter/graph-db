# -*- coding: utf-8 -*-

import json
import plotly.graph_objs as go
import igraph as ig
from pathlib import Path


def get_coords(edges_nodes, network_graph_2d_type):

    """
    Receives JSON object of edges and edges_nodes, and the igraph algo
    Complete selection of algorithms is available at igraph
    Produces JSON object of coordinates
    """

    # create lists of nodes and edges
    edges = edges_nodes["edges"]
    nodes = edges_nodes["nodes"]
    classes = list(map(lambda x: 0 if x == "actor" else 1, edges_nodes["classes"]))
    labels = edges_nodes["labels"]
    # Visualize connections using igraph (2 dimensional only)
    ghg = ig.Graph(directed=False)
    ghg.add_vertices(len(nodes))
    ghg.add_edges(edges)
    layt = ghg.layout(network_graph_2d_type)
    # make coordinates
    Xn = [layt[k][0] for k in range(len(nodes))]  # x-coordinates of nodes
    Yn = [layt[k][1] for k in range(len(nodes))]  # y-coordinates
    Xe = []
    Ye = []
    for e in edges:
        Xe += [layt[e[0]][0], layt[e[1]][0], None]
        Ye += [layt[e[0]][1], layt[e[1]][1], None]
    # make the dictionary of results & coordinates
    coordinates = {}
    coordinates["X_node"] = Xn
    coordinates["Y_node"] = Yn
    coordinates["X_edge"] = Xe
    coordinates["Y_edge"] = Ye
    coordinates["classes"] = classes
    coordinates["labels"] = labels
    return coordinates


def make_plotly_scatter(coordinates, edges_nodes):

    """
    Receives the JSON objects of coordinates & edge-edges_nodes
    Produces an HTML file with the network graph
    """

    prime_node = edges_nodes["prime_node"]
    Xn = coordinates["X_node"]
    Yn = coordinates["Y_node"]
    Xe = coordinates["X_edge"]
    Ye = coordinates["Y_edge"]
    classes = coordinates["classes"]
    labels = coordinates["labels"]

    trace1 = go.Scatter(
        x=Xe,
        y=Ye,
        mode="lines",
        line=dict(color="rgb(125,125,125)", width=1),
        hoverinfo="none",
    )

    trace2 = go.Scatter(
        x=Xn,
        y=Yn,
        mode="markers",
        marker=dict(
            symbol="circle",
            size=6,
            color=classes,
            colorscale=["red", "blue"],
            line=dict(color="rgb(50,50,50)", width=0.5),
        ),
        text=labels,
        hoverinfo="text",
    )

    trace3 = go.Scatter(
        x=[Xn[prime_node]],
        y=[Yn[prime_node]],
        mode="markers",
        marker=dict(
            symbol="circle",
            size=18,
            color="yellow",
            line=dict(color="rgb(50,50,50)", width=0.5),
        ),
        text=[labels[prime_node]],
        hoverinfo="text",
    )

    layout = go.Layout(
        title="Github Network",
        width=1000,
        height=500,
        showlegend=False,
        margin=dict(t=100),
        hovermode="closest",
    )

    # join as figure
    data = [trace1, trace2, trace3]
    fig = go.Figure(data=data, layout=layout)
    fig.update_layout(
        {
            "plot_bgcolor": "rgba(0,0,0,0)",
            "paper_bgcolor": "rgba(0,0,0,0)",
            "xaxis": {"showticklabels": False},
            "yaxis": {"showticklabels": False},
        }
    )
    return fig


def make_viz(analysis_name, prime_repo):

    """
    Receives file path and ID of prime repo
    Produces HTML file with net graph
    """

    print("making visualization...")
    infile_name = str(prime_repo) + "_query_results.json"
    infile_path = Path.joinpath(
        Path.cwd().parents[1], analysis_name, "outputs", infile_name
    )
    print(infile_path)
    outfile_name = "netgraph_{}.html".format(prime_repo)
    outfile_path = Path.joinpath(
        Path.cwd().parents[1], analysis_name, "outputs", outfile_name
    )
    print(outfile_path)

    with open(infile_path) as json_file:
        edges_nodes = json.load(json_file)
    coordinates = get_coords(edges_nodes, "fr")
    fig = make_plotly_scatter(coordinates, edges_nodes)
    outfile_path_str = str(outfile_path)
    fig.write_html(outfile_path_str)
