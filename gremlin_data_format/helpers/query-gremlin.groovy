// List all nodes
g.V().count()

// one node & its label
g.V("37729206")
g.V("37729206").label()

// assign that to a variable
v1 = g.V("37729206").next()
v1.label()

// get a list of all node labels
g.V().group().by(label).by(properties().label().dedup().fold())

// get a count of all repos & actors
g.V().hasLabel("repo").count()
g.V().hasLabel("actor").count()

// save the first result as a new variable
v2 = g.V().hasLabel("actor").limit(1).next()
v2.label()

// List all edges
g.E().count()

// Show one edge
g.E().limit(1)

// Show the first 5 Pull Requests
g.E().hasLabel("PullRequestEvent").limit(5)

// get all adjacent vertices connected by outgoing edges with the specified label
g.V("4046447").out("PullRequestEvent")

// Choose a repository and find all of its contributors
g.V().hasLabel("repo").limit(1).bothE().otherV().path()

// Choose an actor and find all of their contributions
g.V().hasLabel("actor").limit(1).bothE().otherV().path()
