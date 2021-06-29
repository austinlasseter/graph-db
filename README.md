# Graph Database Project

## Folder structure

```
└──network_graph_app
      └──main.py
          ├──helpers
                  ├──    __init__.py
                  ├──setup_analysis.py
                  ├──process_json_files.py
                  ├──previz_prep.py
                  └──make_viz.py
          └──outputs
                  └──various html files
          ├──internal
                  └──various jupyter notebooks
          └──testing
                  └──various shell scripts for running `main.py`
└──gremlin_data_format
      └──main.py
          ├──helpers
                  ├──    __init__.py
                  ├──setup_analysis.py
                  ├──process_json_files.py
                  ├──load-csv-files.groovy
                  └──query-gremlin.groovy
          └──outputs
                  └──two csv files
          └──internal
                  └──various jupyter notebooks
```

## Project 1. Demonstrate network relationships in event data (#905)


This project corresponds to the `network_graph_app` directory. Folder structure is outlined above.

This python module is activated by running `main.py`.

- It receives as input a set of `json.gz` files downloaded from from [Github Arhive](https://api.github.com).
- It also receives the ID of a "prime" repo identified in the [Github API](https://api.github.com) that has been flagged for investigation.
- It produces an html file displaying a network graph of the relationships between repos and actors, starting with the prime repo, up to the third circle of connectivity. This html file is suitable for inclusion in a static website or other promotional material. Example html files are provided in the `outputs` file.

In the `testing` folder there is a script `covid19-calculator.sh` that demonstrates the process for one repository, ID #267690820 with name [covid19-calculator](https://api.github.com/repos/deptofdefense/covid19-calculator).

Inputs for the analysis are not stored in the `clonewars-datascience` directory. The expectation is that they are stored in a parent directory outside of the current directory, according to a file structure laid out in `setup_analysis.py`. The necessaryy `json.gz` files which are the initial inputs should be downloaded from [Github Achive](https://www.gharchive.org/) using a shell command from the appropriate `data` folder, such as:

```
wget https://data.gharchive.org/2015-01-{01..31}-{0..23}.json.gz
```




## Project 2. Demonstrate that event data can be transformed to Gremlin format (#906)

This project corresponds to the `gremlin_data_format` directory. Folder structure is outlined above.

This python module is activated by running `main.py`.

- It receives as input a set of `json.gz` files downloaded from from [Github Arhive](gharchive.org).
- It produces two CSV files, ready for uploading to AWS Neptune.
- It also produces example query results in Gremlin, designed for a use-case similar to our own.

As with the previous project, inputs for the analysis are not stored in the `clonewars-datascience` directory, but rather in the parent directory laid out in `setup_analysis.py`.

According the [AWS Neptune documentation](https://docs.aws.amazon.com/neptune/latest/userguide/bulk-load-tutorial-format-gremlin.html), to load Apache TinkerPop Gremlin data using the CSV format, you must specify the vertices and the edges in separate files, with names similar to `vertex.csv` and `edge.csv`. The required and allowed system column headers are different for vertex files and edge files, as follows:

- Vertex headers: id, label.
- Edge headers: id, from, to, label.
Example CSV files for one analysis are available in the `outputs` folder of the project directory.

### Apache Ecosystem

There are several different components to the graph database with Apache, and not all of them are necessary when you're getting set up with Amazon Neptune. Here's the full list of Apache tools:

- [Apache Tinkerpop](http://tinkerpop.apache.org/): an open source, vendor-agnostic, graph computing framework. It's one of the two frameworks supported by Neptune (the other is RDF).
- [TinkerGraph](https://github.com/tinkerpop/blueprints/wiki/TinkerGraph). A lightweight, in-memory graph engine that serves as a reference implementation of the TinkerPop3 API. People often [compare]((https://db-engines.com/en/system/JanusGraph%3BTinkerGraph)) JanusGraph and TinkerGraph with Neo4j, Amazon Neptune and ArangoDB.
- [Gremlin](https://tinkerpop.apache.org/gremlin.html) is the query language of Tinkerpop. Neptune supports this too.
- The [Gremlin Console](https://tinkerpop.apache.org/docs/current/tutorials/the-gremlin-console/) is one way (but not the only way) to interact with the Gremlin query language. You can skip the console and just write Python scripts with a connector. But doing so requires a server such as...
- The [Gremlin Server](https://tinkerpop.apache.org/docs/current/reference/#connecting-gremlin-server). This is provided by Apache but there are multiple competitor options instead. It definitely is not used by AWS, because Neptune is the direct competitor to Gremlin Server.

For the purposes of this project, I installed Tinkerpop, Gremlin and the Gremlin Console. I experimented with Gremlin Server, which is necessary for running the [GremlinPython](https://pypi.org/project/gremlinpython/) language, but ultimately did not use it.

## Setup for Project 2

Tinkerpop and the Gremlin console can be downloaded [from the Apache website](https://tinkerpop.apache.org/) They can also be installed using Docker:

```
docker pull tinkerpop/gremlin-console
docker run -it tinkerpop/gremlin-console
```

Note that there is not a brew formula per-se but for each of the client languages you can use their respective package managers to install the clients such as `pip install gremlinpython`. Read more about installation at the [Gremlin discussion board](https://groups.google.com/g/gremlin-users/c/uyvVjw5UecA/m/01TZjkx7AwAJ).

Add the gremlin console to PATH:

```
export PATH=/usr/local/apache-tinkerpop-gremlin-console-3.4.10/bin/gremlin.sh:$PATH
```

For the purpose of this project, I installed the Gremlin console in the parent directory of the `clonewars-datascience` directory. When you install the Gremlin console, it create a directory called `apache-tinkerpop-gremlin-console-3.4.10` which has a subdirectory called `data`. This is where I stored all data and outputs for my analysis.

Once installed, the Groovy console is initiated from the `apache-tinkerpop-gremlin-console-3.4.10` directory as follows:

```
bin/gremlin.sh
```

The Gremlin console is an adaptation of the [Groovy console](https://groovyconsole.appspot.com/) and expects inputs written in the [Groovy programming language](https://groovy-lang.org/). It is possible to load a groovy script in the console as follows:

```
:load /path/to/file/load-csv-files.groovy
```

I have provided two Groovy scripts in the `helpers` directory. These can be loaded in the Gremlin console, one after the other, using the syntax provided above.

- `load-csv-files.groovy`: initiates a graph traversal object `g` by combining the two CSV files `vertex.csv` and `edge.csv`.
- `query-gremlin.groovy`: using the graph traversal object `g`, conducts a series of queries into the github events data, exploring relationships between actors and repos.

Examples of additional Gremlin queries can be found in [this manual](https://dkuppitz.github.io/gremlin-cheat-sheet/101.html).

How does one [load data into a property-graph database](https://stackoverflow.com/questions/50043311/gremlin-server-create-a-graph-by-loading-data-from-csv-files-from-gremlin-python)? Basically 3 options for this:

- Write a Gremlin Script to execute in the Gremlin Console to load your data.
- If you have an especially large graph, then consider BulkLoaderVertexProgram and Hadoop/Spark
- Consider the bulk loading tools available to the graph database you have chosen.

## Additional Resources

- Several manuals and notes of internal meetings are saved in the [CW shared drive](https://drive.google.com/drive/folders/1hcbdBPz9fsMzf2Av_76KNN46BVZoDUFj?usp=sharing) on Google Docs.
- AWS Neptune: [Using Gremlin to Access the Graph](https://docs.aws.amazon.com/neptune/latest/userguide/get-started-graph-gremlin.html)
- AWS Neptune: [Gremlin Load Data Format](https://docs.aws.amazon.com/neptune/latest/userguide/bulk-load-tutorial-format-gremlin.html)
- AWS Neptune: [Gremlin Load Data Format](https://docs.aws.amazon.com/neptune/latest/userguide/bulk-load-tutorial-format-gremlin.html)
- Documentation for [Tinkerpop 2.0](http://gremlindocs.spmallette.documentup.com/)
- StackOverflow: [All Gremlin Posts](https://stackoverflow.com/search?q=gremlin&s=e7fc6177-dda7-4681-b3b7-16b6888d618a)
- StackOverflow: [All posts by Stephen Mallette](https://stackoverflow.com/users/1831717/stephen-mallette)
- StackOverflow: [All posts by Kelvin Lawrence](https://stackoverflow.com/users/5442034/kelvin-lawrence)
- Kelvin Lawrence's [Gremlin Guide](https://kelvinlawrence.net/book/Gremlin-Graph-Guide.html#stddev)
- Apache Tinkerpop [Installation Guide](https://drive.google.com/file/d/1w5BROGS5cs6O7EwmYD8wUSYqmVjNex8B/view?usp=sharing)
- Jason Plurad's [Guide to Loading Gremlin Data](https://drive.google.com/file/d/1058gSLPHkbsAbngsyaw1pmKmtImDZUPM/view?usp=sharing)
- Gremlin Users [Google Group](https://groups.google.com/g/gremlin-users/), which is full of many great questions and answers
- ACloudGuru Tutorial: [Go Serverless with a Graph Database](https://acloudguru.com/course/go-serverless-with-a-graph-database) - requires ACG subscription to access
- ACloudGuru Tutorial: [Loading and Retrieving Data in Neptune](https://acloudguru.com/hands-on-labs/loading-and-retrieving-data-in-neptune)
