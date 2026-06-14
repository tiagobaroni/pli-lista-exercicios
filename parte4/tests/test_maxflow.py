"""Tests for Edmonds-Karp max-flow, flow conservation, and min-cut (Exercise 3)."""

import sys
import unittest
from pathlib import Path

import networkx as nx

sys.path.insert(0, str(Path(__file__).parent.parent))

from graphs import G3_ARCS, G3_NODES, G3_SINK, G3_SOURCE
from maxflow import edmonds_karp


class TestEdmondsKarp(unittest.TestCase):

    def setUp(self) -> None:
        self.sol = edmonds_karp(G3_ARCS, G3_SOURCE, G3_SINK)

    def test_max_flow_matches_networkx(self) -> None:
        """Edmonds-Karp max flow equals NetworkX maximum_flow."""
        G = nx.DiGraph()
        G.add_nodes_from(G3_NODES)
        for u, v, c in G3_ARCS:
            G.add_edge(u, v, capacity=c)
        nx_flow, _ = nx.maximum_flow(G, G3_SOURCE, G3_SINK)
        self.assertEqual(self.sol["max_flow"], nx_flow)

    def test_flow_conservation(self) -> None:
        """Flow is conserved at every intermediate node."""
        flow_in: dict[int, int] = {n: 0 for n in G3_NODES}
        flow_out: dict[int, int] = {n: 0 for n in G3_NODES}
        for af in self.sol["arc_flows"]:
            flow_out[af["u"]] += af["flow"]
            flow_in[af["v"]] += af["flow"]
        for n in G3_NODES:
            if n in (G3_SOURCE, G3_SINK):
                continue
            self.assertEqual(
                flow_in[n],
                flow_out[n],
                msg=f"Node {n}: in={flow_in[n]}, out={flow_out[n]}",
            )

    def test_min_cut_equals_max_flow(self) -> None:
        """Sum of min-cut capacities equals max flow (max-flow min-cut theorem)."""
        mc = self.sol["min_cut"]
        self.assertEqual(mc["total_capacity"], self.sol["max_flow"])

    def test_arc_flows_nonnegative(self) -> None:
        """No arc carries negative flow."""
        for af in self.sol["arc_flows"]:
            self.assertGreaterEqual(
                af["flow"],
                0,
                msg=f"Negative flow on ({af['u']}, {af['v']}): {af['flow']}",
            )

    def test_arc_flows_within_capacity(self) -> None:
        """No arc exceeds its capacity."""
        for af in self.sol["arc_flows"]:
            self.assertLessEqual(
                af["flow"],
                af["capacity"],
                msg=(
                    f"Capacity exceeded on ({af['u']}, {af['v']}): "
                    f"flow={af['flow']}, cap={af['capacity']}"
                ),
            )

    def test_augmenting_paths_nonempty(self) -> None:
        """At least one augmenting path is found (network is not already saturated)."""
        self.assertGreater(len(self.sol["paths"]), 0)

    def test_source_not_in_sink_side(self) -> None:
        """Source node is in the source side of the min-cut."""
        self.assertIn(G3_SOURCE, self.sol["min_cut"]["source_side"])

    def test_sink_not_in_source_side(self) -> None:
        """Sink node is NOT in the source side of the min-cut."""
        self.assertNotIn(G3_SINK, self.sol["min_cut"]["source_side"])


if __name__ == "__main__":
    unittest.main()
