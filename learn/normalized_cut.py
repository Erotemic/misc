import networkx as nx
import random
import numpy as np

# Ensure a connected random graph
graph = nx.generators.random_graphs.erdos_renyi_graph(1000, 0.5)
graph = graph.subgraph(list(nx.connected_components(graph))[0])

for u, v, d in graph.edges(data=True):
    d['capacity'] = 1

s = t = None
assert len(graph) >= 2
while s == t:
    s, t = random.choices(list(graph.nodes()), k=2)

# Min flow tends to just separate out one of the nodes
cost, (part1, part2) = nx.algorithms.flow.minimum_cut(graph, s, t)
print(f'Min Cut:  {len(part1)=} {len(part2)=}')


# Instead lets do a normalized cut
def normalized_cut(graph):
    """
    References:
        https://people.orie.cornell.edu/dpw/orie6334/Fall2016/lecture7.pdf
        https://courses.cs.washington.edu/courses/cse521/16sp/521-lecture-11.pdf
        https://en.wikipedia.org/wiki/Graph_partition
    """
    nodes = list(graph.nodes())
    # Adjacency matrix
    A = nx.to_numpy_array(graph)

    # Degree matrix
    degrees = A.sum(axis=1)

    # Computed normalized adjacency
    root_D = np.diag(1 / np.sqrt(degrees))
    norm_A = root_D @ A @ root_D

    # Compute laplacian matrix
    laplace = np.eye(len(norm_A)) - norm_A

    # Spectral analysis
    eig_vals, eig_vecs = np.linalg.eig(laplace)
    # eig_val2 = eig_vals[1]
    eig_vec2 = eig_vecs[1]

    # Sort verticies according to this eigenvector
    ordering = np.argsort(eig_vec2)

    best_cost = float('inf')
    best_parts = None
    for i in range(1, len(ordering) - 2):
        cand_idxs1 = ordering[:i]
        cand_idxs2 = ordering[i:]
        part1_cand = [nodes[idx] for idx in cand_idxs1]
        part2_cand = [nodes[idx] for idx in cand_idxs2]
        cost = nx.algorithms.cuts.normalized_cut_size(graph, part1_cand, part2_cand)
        if cost < best_cost:
            best_cost = cost
            best_parts = (part1_cand, part2_cand)
    return best_cost, best_parts


cost, (part1, part2) = normalized_cut(graph)
print(f'Norm Cut: {len(part1)=} {len(part2)=}')

part1, part2 = nx.algorithms.community.kernighan_lin_bisection(graph)
print(f'Kernigan-Lin Partition: {len(part1)=} {len(part2)=}')


# Or randomize
cost, (part1, part2) = nx.algorithms.approximation.randomized_partitioning(graph)
print(f'Random Partition: {len(part1)=} {len(part2)=}')
