
graph = TinkerGraph.open()
g = graph.traversal()

// Vertex
new File("data/gremlin_data_20210512_nodes_processed.csv").eachLine{
  l,idx->
      if (idx!=1) {
        p=l.split(",");
        graph.addVertex(id, p[0], label, p[1]).property('type',p[2])
}}

// Edge
new File("data/gremlin_data_20210512_edges_processed.csv").eachLine{
  l,idx->
    if (idx!=1) {
        o=l.split(",")[1];
        p=l.split(",")[2];
        q=l.split(",")[3];
        v1=g.V(p).next()
        v2=g.V(q).next()
        v1.addEdge(o, v2)
}}
