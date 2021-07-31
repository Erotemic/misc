
def collatz(x):
    while x > 1:
        if x % 2 == 0:
            x = x // 2
        else:
            x = 3 * x + 1
        yield x


def test_last_digits():

    mapping = {}
    tail_edge_hist = ub.ddict(lambda: 0)

    for x in ub.ProgIter(range(1, int(1e5))):
        import ubelt as ub
        for y in collatz(x):
            if x in mapping:
                break
            x_tail = x - (10 * (x // 10))
            y_tail = y - (10 * (y // 10))
            mapping[x] = y
            tail_edge_hist[(str(x_tail), str(y_tail))] += 1
            x = y

    import kwarray
    print(kwarray.stats_dict(np.array(list(tail_edge_hist.values()))))

    import networkx as nx
    tail_g = nx.DiGraph()
    tail_g.add_edges_from(tail_edge_hist.keys())

    for cycle in nx.simple_cycles(tail_g):
        print('cycle = {!r}'.format(cycle))


    print('tail_g.adj = {!r}'.format(tail_g.adj))

    for n in sorted(tail_g.nodes, key=int):
        pred = tuple(tail_g.pred[n].keys())
        succ = tuple(tail_g.succ[n].keys())
        in_d = tail_g.in_degree(n)
        out_d = tail_g.out_degree(n)
        print(f'{str(pred):>15} -> {n:>2} -> {str(succ):<15} : {out_d:<2} {in_d:<2}')

    import kwplot
    import graphid
    plt = kwplot.autoplt()
    sccs = list(nx.strongly_connected_components(tail_g))
    nx.draw_networkx(tail_g)
    # nx.draw_circular(tail_g)

    ax = plt.gca()
    ax.cla()
    # nx.draw_networkx(tail_g)
    graphid.util.util_graphviz.show_nx(tail_g)


    CCs = list(nx.connected_components(tail_g.to_undirected()))

