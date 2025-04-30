import time
from typing import Tuple, List, Optional
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from itertools import zip_longest


class PailsPuzzleAnimator:
    """
    Animates the solution to a pails puzzle using Rich for beautiful console output.

    Attributes:
        capacities (Tuple[int, ...]): Container sizes
        solution_path (List[Tuple[int, ...]]): Sequence of states
    """

    def __init__(
        self, capacities: Tuple[int, ...], solution_path: List[Tuple[int, ...]]
    ):
        self.capacities = capacities
        self.solution_path = solution_path
        self.main_layout = Layout(name="main")
        self.buckets_layout = Layout(name="buckets")
        self.action_layout = Layout(name="action", size=3)

        # Setup main layout structure
        self.main_layout.split_column(self.buckets_layout, self.action_layout)

        # Setup buckets in a row
        self.buckets_layout.split_row(
            *[Layout(name=f"Bucket {i + 1}") for i in range(len(capacities))]
        )

    def _create_bucket_panel(
        self, amount: int, capacity: int, highlight: bool = False
    ) -> Panel:
        """Create a rich Panel showing a single bucket"""
        bucket_lines = []

        # Top of bucket
        bucket_lines.append("┌────┐")

        # Empty space first (so water appears at bottom)
        empty_space = capacity - amount
        for _ in range(empty_space):
            bucket_lines.append("│    │")

        # Water (blue colored)
        water_color = "bright_blue" if highlight else "blue"
        for _ in range(amount):
            water = Text("│~~~~│", style=water_color)
            bucket_lines.append(water)

        # Bottom of bucket
        bucket_lines.append("└────┘")

        # Add capacity label
        label = Text(f"{amount}/{capacity} gal", justify="center")
        bucket_lines.append(label)

        return Panel("\n".join(str(line) for line in bucket_lines), height=capacity + 3)

    def _get_action_text(self, prev: Tuple[int, ...], curr: Tuple[int, ...]) -> Text:
        """Generate rich Text describing the action between states"""
        if not prev:
            return Text("Initial state", style="bold green")

        # Check for fill
        for i in range(len(prev)):
            if curr[i] == self.capacities[i] and prev[i] != self.capacities[i]:
                return Text(f"Filled bucket {i + 1}", style="bold yellow")

        # Check for empty
        for i in range(len(prev)):
            if curr[i] == 0 and prev[i] != 0:
                return Text(f"Emptied bucket {i + 1}", style="bold red")

        # Check for transfer
        for src in range(len(prev)):
            for dst in range(len(prev)):
                if src == dst:
                    continue
                transferred = prev[src] - curr[src]
                if transferred > 0 and curr[dst] - prev[dst] == transferred:
                    return Text(
                        f"Poured {transferred} gal from bucket {src + 1} → {dst + 1}",
                        style="bold cyan",
                    )

        return Text("Unknown action", style="bold")

    def _update_display(
        self,
        state: Tuple[int, ...],
        action: Text,
        pouring_from: Optional[int] = None,
        pouring_to: Optional[int] = None,
    ) -> None:
        """Update the display with current state and action"""
        # Update bucket panels
        for i, (amount, capacity) in enumerate(zip(state, self.capacities)):
            highlight = i in (pouring_from, pouring_to)
            panel = self._create_bucket_panel(amount, capacity, highlight)
            self.buckets_layout[f"Bucket {i + 1}"].update(panel)

        # Update action panel
        self.action_layout.update(Panel(action, title="Action"))

    def animate(self, step_delay: float = 1.5, pour_frames: int = 5) -> None:
        """
        Animate the solution with Rich Live display.

        Args:
            step_delay: Seconds between steps
            pour_frames: Number of animation frames for pouring
        """
        if not self.solution_path:
            print("No solution to animate")
            return

        with Live(self.main_layout, refresh_per_second=10, screen=False) as live:
            # Initial state
            self._update_display(
                self.solution_path[0], self._get_action_text([], self.solution_path[0])
            )
            live.refresh()
            time.sleep(step_delay)

            # Animate each transition
            for i in range(1, len(self.solution_path)):
                prev = self.solution_path[i - 1]
                curr = self.solution_path[i]
                action = self._get_action_text(prev, curr)

                # Special handling for pouring animation
                if "Poured" in action.plain:
                    src, dst = None, None
                    for j in range(len(prev)):
                        if prev[j] > curr[j]:
                            src = j
                        elif prev[j] < curr[j]:
                            dst = j

                    if src is not None and dst is not None:
                        amount = prev[src] - curr[src]
                        for frame in range(1, pour_frames + 1):
                            temp_state = list(prev)
                            transferred = (amount * frame) // pour_frames
                            temp_state[src] = prev[src] - transferred
                            temp_state[dst] = prev[dst] + transferred

                            self._update_display(
                                temp_state,
                                Text(
                                    f"{action.plain} ({frame}/{pour_frames})",
                                    style=action.style,
                                ),
                                src,
                                dst,
                            )
                            live.refresh()
                            time.sleep(step_delay / pour_frames)

                # Regular state update
                self._update_display(curr, action)
                live.refresh()
                time.sleep(step_delay)


# Example usage
if __name__ == "__main__":
    from rich.console import Console

    capacities = (3, 5, 8)
    solution_path = [(0, 0, 0), (0, 5, 0), (3, 2, 0), (0, 2, 3), (2, 0, 3), (2, 5, 3), (3, 4, 3)]


    console = Console()
    console.print("[bold]Pail Puzzle Solver Animation[/bold]", justify="center")

    animator = PailsPuzzleAnimator(capacities, solution_path)
    animator.animate(step_delay=1.0, pour_frames=5)
