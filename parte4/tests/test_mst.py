"""Tests for Prim, Kruskal, and UnionFind (Exercises 1 and 2)."""

import sys
import unittest
from pathlib import Path

import networkx as nx

sys.path.insert(0, str(Path(__file__).parent.parent))

from graphs import G1_EDGES, G1_NODES, G2_EDGES, G2_NODES
from mst import UnionFind, kruskal, prim


class TestUnionFind(unittest.TestCase):

    def test_find_self(self) -> None:
        """Each node is its own representative initially."""
        uf = UnionFind([1, 2, 3])
        for n in [1, 2, 3]:
            self.assertEqual(uf.find(n), n)

    def test_union_disjoint(self) -> None:
        """Union of two disjoint sets returns True."""
        uf = UnionFind([1, 2, 3])
        self.assertTrue(uf.union(1, 2))

    def test_union_same_component(self) -> None:
        """Union within the same component returns False."""
        uf = UnionFind([1, 2, 3])
        uf.union(1, 2)
        uf.union(2, 3)
        self.assertFalse(uf.union(1, 3))

    def test_path_compression(self) -> None:
        """find() returns the same representative for all nodes in a chain."""
        uf = UnionFind([1, 2, 3, 4])
        uf.union(1, 2)
        uf.union(2, 3)
        uf.union(3, 4)
        r = uf.find(1)
        self.assertEqual(uf.find(4), r)

    def test_transitivity(self) -> None:
        """Nodes connected transitively share the same representative."""
        uf = UnionFind(list(range(1, 6)))
        uf.union(1, 2)
        uf.union(3, 4)
        uf.union(2, 3)
        self.assertEqual(uf.find(1), uf.find(4))
        self.assertNotEqual(uf.find(1), uf.find(5))


class TestKruskalG1(unittest.TestCase):

    def setUp(self) -> None:
        self.result = kruskal(G1_EDGES, G1_NODES)

    def test_edge_count(self) -> None:
        """Kruskal MST for G1 has n-1 edges."""
        self.assertEqual(len(self.result["tree_edges"]), len(G1_NODES) - 1)

    def test_step_count(self) -> None:
        """Every edge is examined exactly once."""
        self.assertEqual(len(self.result["steps"]), len(G1_EDGES))

    def test_weight_matches_networkx(self) -> None:
        """MST total weight matches NetworkX minimum_spanning_tree."""
        G = nx.Graph()
        G.add_nodes_from(G1_NODES)
        for u, v, w in G1_EDGES:
            G.add_edge(u, v, weight=w)
        nx_weight = int(sum(d["weight"] for _, _, d in nx.minimum_spanning_tree(G).edges(data=True)))
        self.assertEqual(self.result["total_weight"], nx_weight)

    def test_total_weight_equals_sum_of_edges(self) -> None:
        """Reported total_weight matches sum of individual tree edge weights."""
        computed = sum(e[2] for e in self.result["tree_edges"])
        self.assertEqual(self.result["total_weight"], computed)


class TestPrimG1(unittest.TestCase):

    def setUp(self) -> None:
        self.result = prim(G1_EDGES, G1_NODES)

    def test_edge_count(self) -> None:
        """Prim MST for G1 has n-1 edges."""
        self.assertEqual(len(self.result["tree_edges"]), len(G1_NODES) - 1)

    def test_step_count(self) -> None:
        """Prim produces one step per node added (excluding the start node)."""
        self.assertEqual(len(self.result["steps"]), len(G1_NODES) - 1)

    def test_kruskal_prim_weight_equal(self) -> None:
        """Kruskal and Prim produce the same total weight for G1."""
        k = kruskal(G1_EDGES, G1_NODES)
        self.assertEqual(self.result["total_weight"], k["total_weight"])

    def test_custom_start_node(self) -> None:
        """Prim with a different start node yields the same total weight."""
        r5 = prim(G1_EDGES, G1_NODES, start=5)
        self.assertEqual(r5["total_weight"], self.result["total_weight"])
        self.assertEqual(r5["start_node"], 5)


class TestKruskalG2(unittest.TestCase):

    def setUp(self) -> None:
        self.result = kruskal(G2_EDGES, G2_NODES)

    def test_edge_count(self) -> None:
        """Kruskal MST for G2 has n-1 edges."""
        self.assertEqual(len(self.result["tree_edges"]), len(G2_NODES) - 1)

    def test_weight_matches_networkx(self) -> None:
        """MST total weight matches NetworkX for G2."""
        G = nx.Graph()
        G.add_nodes_from(G2_NODES)
        for u, v, w in G2_EDGES:
            G.add_edge(u, v, weight=w)
        nx_weight = int(sum(d["weight"] for _, _, d in nx.minimum_spanning_tree(G).edges(data=True)))
        self.assertEqual(self.result["total_weight"], nx_weight)


class TestPrimG2(unittest.TestCase):

    def test_edge_count(self) -> None:
        """Prim MST for G2 has n-1 edges."""
        result = prim(G2_EDGES, G2_NODES)
        self.assertEqual(len(result["tree_edges"]), len(G2_NODES) - 1)

    def test_kruskal_prim_weight_equal(self) -> None:
        """Kruskal and Prim produce the same total weight for G2."""
        k = kruskal(G2_EDGES, G2_NODES)
        p = prim(G2_EDGES, G2_NODES)
        self.assertEqual(k["total_weight"], p["total_weight"])


if __name__ == "__main__":
    unittest.main()
