def _devcheck_topo_sorts():

    def is_topological_order_vertex_approch(graph, node_order):
        """
        From Ben Cooper

        Runtime:
            O(V * V * E)

        References:
            https://stackoverflow.com/questions/54174116/checking-validity-of-topological-sort
        """
        preceding = set()
        # Iterate through the vertices in your ordering.
        for node in node_order:
            # retrieve its list of outgoing edges.
            out_edges = graph.out_edges(node)
            # If any of those edges end in a vertex that precedes
            # the current vertex in the ordering, return false.
            if any(v in preceding for u, v in out_edges):
                return False
            preceding.add(node)
        # If you iterate through all the vertices without returning false,
        # return true.
        return True

    def is_topological_order_edge_approch(graph, node_order):
        """
        From Ben Cooper

        Runtime:
            O(V * E)

        References:
            https://stackoverflow.com/questions/54174116/checking-validity-of-topological-sort
        """
        # Iterate through the edges in G.
        node_to_index = {n: idx for idx, n in enumerate(node_order)}
        for u, v in graph.edges:
            # For each edge, retrieve the index of each of its vertices in the ordering.
            ux = node_to_index[u]
            vx = node_to_index[v]
            # Compared the indices. If the origin vertex isn't earlier than
            # the destination vertex, return false.
            if ux >= vx:
                # raise Exception
                return False
        # If you iterate through all of the edges without returning false,
        # return true.
        return True

    def is_topological_sort_fast_approch(graph, node_order):
        """
        A topological ordering of nodes is an ordering of the nodes such that
        for every edge (u,v) in G, u appears earlier than v in the ordering

        From zohar.kom

        Runtime:
            O(V + E)
        """
        # First, do a graph traversal to get the incoming degree of each vertex.
        in_degree = dict(graph.in_degree)
        preceding = set()
        # Then start from the first vertex in your list.
        for node in node_order:
            # Every time, when we look at a vertex, we want to check two things
            # 1) is the incoming degree of this vertex is 0?
            # 2) is this vertex a neighbor of the previous vertex?
            # If we got a no from the previous questions at some point, we
            # know that this is not a valid topological order.
            neighbors = set(graph.neighbors(node))
            if in_degree[node] != 0 and not (neighbors & preceding):
                # print(f'node={node}')
                # raise Exception
                return False

            # We also want to decrement all its neighbors' incoming degree,
            # as if we cut all edges.
            for n in neighbors:
                in_degree[n] -= 1

            preceding.add(node)

        # Otherwise, it is.
        return True

    # def tests_topo_sorts():
    import networkx as nx
    import tqdm
    from itertools import permutations

    for N in range(10):
        for f in [0, 0.1, 0.2, 0.5, 0.9]:
            # Random DAG
            raw = nx.erdos_renyi_graph(N, f, directed=True)
            graph = nx.DiGraph(nodes=raw.nodes())
            graph.add_edges_from([(u, v) for u, v in raw.edges() if u < v])
            all_topo_sorts = set(map(tuple, nx.all_topological_sorts(graph)))
            all_perms = list(permutations(graph.nodes()))

            for node_order in tqdm.tqdm(all_perms):
                f0 = node_order in all_topo_sorts
                f1 = is_topological_order_edge_approch(graph, node_order)
                f2 = is_topological_order_vertex_approch(graph, node_order)
                f3 = is_topological_sort_fast_approch(graph, node_order)
                assert f0 == f1 == f2 == f3

    def is_topological_order(graph, node_order):
        """
        A topological ordering of nodes is an ordering of the nodes such that for
        every edge (u,v) in G, u appears earlier than v in the ordering

        Runtime:
            O(V * E)

        References:
            https://stackoverflow.com/questions/54174116/checking-validity-of-topological-sort
        """
        # Iterate through the edges in G.

        node_to_index = {n: idx for idx, n in enumerate(node_order)}
        return all(node_to_index[u] < node_to_index[v] for u, v in graph.edges)

    raw = nx.erdos_renyi_graph(100, 0.5, directed=True)
    graph = nx.DiGraph(nodes=raw.nodes())
    graph.add_edges_from([(u, v) for u, v in raw.edges() if u < v])

    import kwarray
    node_order = kwarray.shuffle(list(graph.nodes()))

    import timerit
    ti = timerit.Timerit(1000, bestof=10, verbose=2)
    for timer in ti.reset('4'):
        with timer:
            f4 = is_topological_order(graph, node_order)
    for timer in ti.reset('1'):
        with timer:
            f1 = is_topological_order_edge_approch(graph, node_order)
    assert f1 == f4
