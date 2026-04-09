import unittest

from fresh_vamana import FreshVamana


class FreshVamanaTests(unittest.TestCase):
    def test_insert_and_search_returns_nearest_neighbors(self) -> None:
        index = FreshVamana(max_degree=4, build_ef=8, search_ef=8)
        points = [
            (0.0, 0.0),
            (1.0, 0.0),
            (0.0, 1.0),
            (5.0, 5.0),
            (5.0, 6.0),
        ]
        ids = [index.insert(point) for point in points]

        results = index.search((0.1, 0.1), k=2)

        self.assertEqual(results[0][0], ids[0])
        self.assertLess(results[0][1], results[1][1])

    def test_delete_excludes_node_from_results(self) -> None:
        index = FreshVamana(max_degree=4, build_ef=8, search_ef=8)
        near_id = index.insert((0.0, 0.0))
        far_id = index.insert((10.0, 10.0))

        index.delete(near_id)
        results = index.search((0.0, 0.0), k=2)

        self.assertEqual([node_id for node_id, _ in results], [far_id])

    def test_consolidate_removes_deleted_nodes(self) -> None:
        index = FreshVamana(max_degree=4, build_ef=8, search_ef=8)
        first = index.insert((0.0, 0.0))
        second = index.insert((1.0, 1.0))
        third = index.insert((2.0, 2.0))

        index.delete(second)
        mapping = index.consolidate()

        self.assertEqual(index.active_count, 2)
        self.assertEqual(set(mapping.keys()), {first, third})
        self.assertEqual(index.search((0.0, 0.0), k=1)[0][0], mapping[first])

    def test_cosine_distance_metric(self) -> None:
        index = FreshVamana(metric="cosine", max_degree=4, build_ef=8, search_ef=8)
        a = index.insert((1.0, 0.0))
        b = index.insert((0.0, 1.0))
        results = index.search((0.9, 0.1), k=1)
        self.assertEqual(results[0][0], a)
        self.assertNotEqual(a, b)


if __name__ == "__main__":
    unittest.main()
