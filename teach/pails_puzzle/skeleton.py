"""
A solver for the water pouring puzzle.

References:
    https://en.wikipedia.org/wiki/Water_pouring_puzzle
"""

import networkx as nx
from typing import Tuple, List, Set


class PailsPuzzleSolver:
    """
    A solver for water jug problems using graph traversal.

    Attributes:
        capacities (Tuple[int, ...]): Container sizes
        target (int): Desired amount to measure
        graph (nx.DiGraph): Complete state space graph

    Examples:
        >>> solver = PailsPuzzleSolver((3, 5), 4)
        >>> solution = solver.solve()
        >>> len(solution) > 0
        True
        >>> solver.target in solution[-1]
        True
    """

    def __init__(self, capacities: Tuple[int, ...], target: int):
        """
        Initialize solver with container capacities and target amount.

        Args:
            capacities: Container sizes (e.g., (3, 5) for 3 and 5 gallon jugs)
            target: Desired amount to measure
        """
        self.capacities = capacities
        self.target = target
        self.graph = nx.DiGraph()
        self.solution_path = None

    def get_next_states(self, state: Tuple[int, ...]) -> Set[Tuple[int, ...]]:
        """
        Generate all valid states reachable from current state in one move.

        Args:
            state: Current water amounts in containers

        Returns:
            Set of valid next states

        Examples:
            >>> solver = PailsPuzzleSolver((3, 5), 0)
            >>> sorted(solver.get_next_states((0, 0)))
            [(0, 5), (3, 0)]
            >>> sorted(solver.get_next_states((3, 2)))
            [(0, 2), (0, 5), (2, 3), (3, 0), (3, 5)]
            >>> solver = PailsPuzzleSolver((3, 5, 8), 0)
            >>> sorted(solver.get_next_states((0, 0, 8)))
        """
        next_states = set()

        raise NotImplementedError(
            '''
            IMPLEMENT ME!

            Given the current state, we need to enumerate all of the possible
            next states we could achive with a single action. This could be:

            1. Empty a bucket
            2. Fill a bucket
            3. Transfer water from one bucket to another bucket.
               (Cannot spill any water, i.e.
                cannot pour more than the destination bucket can hold,
                We need a precices measurement, so no fractional pours, i.e.
                can only stop if the source bucket is empty or the destination
                bucket is full.)

            ''')

        return next_states

    def build_graph(self) -> None:
        """
        Build complete state space graph.

        Examples:
            >>> solver = PailsPuzzleSolver((2, 2), 0)
            >>> solver.build_graph()
            >>> len(solver.graph.nodes())
            4
        """
        start = tuple([0] * len(self.capacities))
        queue = [start]
        self.graph.add_node(start)

        while queue:
            current = queue.pop()
            for neighbor in self.get_next_states(current):
                if neighbor not in self.graph.nodes:
                    self.graph.add_node(neighbor)
                    queue.append(neighbor)
                self.graph.add_edge(current, neighbor)

    def solve(self) -> List[Tuple[int, ...]]:
        """
        Find shortest solution path.


        Returns:
            List of states from start to target, or empty list if no solution

        Examples:
            >>> solver = PailsPuzzleSolver((3, 5), 4)
            >>> solution = solver.solve()
            >>> len(solution) > 0 and solver.target in solution[-1]
            True
            >>> solver = PailsPuzzleSolver((2, 4), 5)
            >>> solver.solve()
            []
        """
        if not self.graph.nodes():
            self.build_graph()

        start = tuple([0] * len(self.capacities))

        if self.target not in self.graph.nodes:
            raise nx.NetworkXNoPath('Target is not possible')

        try:
            self.solution_path = nx.shortest_path(self.graph, start, self.target)
        except nx.NetworkXNoPath:
            self.solution_path = []
        return self.solution_path

    def visualize_solution(self):
        """
        Visualize the solution path using matplotlib (if solution exists).
        """
        import matplotlib.pyplot as plt

        if not self.solution_path:
            print("No solution found!")
            return

        print(f"Solution found in {len(self.solution_path) - 1} steps:")
        for i, state in enumerate(self.solution_path):
            print(f"Step {i}: {state}")

        # Create a subgraph containing just the solution path
        path_edges = list(zip(self.solution_path[:-1], self.solution_path[1:]))
        solution_graph = nx.DiGraph()
        solution_graph.add_nodes_from(self.solution_path)
        solution_graph.add_edges_from(path_edges)

        # Draw the solution graph
        plt.figure(figsize=(10, 8))
        pos = nx.spring_layout(solution_graph)

        # Draw nodes and edges
        nx.draw_networkx_nodes(
            solution_graph, pos, node_size=1500, node_color="lightblue"
        )
        nx.draw_networkx_edges(
            solution_graph, pos, edge_color="gray", width=1, arrows=True
        )

        # Highlight the path
        nx.draw_networkx_edges(
            solution_graph,
            pos,
            edgelist=path_edges,
            edge_color="r",
            width=2,
            arrows=True,
        )
        nx.draw_networkx_nodes(
            solution_graph,
            pos,
            nodelist=self.solution_path,
            node_color="r",
            node_size=1500,
        )

        # Add labels
        labels = {
            state: "\n".join(
                [f"Jug {i + 1}: {amount}" for i, amount in enumerate(state)]
            )
            for state in self.solution_path
        }
        nx.draw_networkx_labels(solution_graph, pos, labels, font_size=10)

        plt.title(
            f"Solution Path for {len(self.capacities)} Jugs Problem (Target: {self.target})"
        )
        plt.axis("off")
        plt.tight_layout()
        plt.show()


def main():

    # Example usage with visualization
    solver = PailsPuzzleSolver(
        capacities=(3, 5, 8),
        target=(0, 4, 4),
    )
    solver.build_graph()

    print("\nComplete State Graph:")
    nx.write_network_text(solver.graph)

    solver.solve()
    print(solver.solution_path)

    if 0:
        solver.visualize_solution()

if __name__ == '__main__':
    main()
