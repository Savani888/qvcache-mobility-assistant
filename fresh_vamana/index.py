from __future__ import annotations

from dataclasses import dataclass, field
from heapq import heappop, heappush
from math import sqrt
from threading import RLock
from typing import Callable, Iterable, Sequence

Vector = Sequence[float]
DistanceFn = Callable[[Vector, Vector], float]


def _l2_distance(left: Vector, right: Vector) -> float:
    return sqrt(sum((float(a) - float(b)) ** 2 for a, b in zip(left, right)))


def _cosine_distance(left: Vector, right: Vector) -> float:
    dot = 0.0
    left_norm = 0.0
    right_norm = 0.0
    for a, b in zip(left, right):
        fa = float(a)
        fb = float(b)
        dot += fa * fb
        left_norm += fa * fa
        right_norm += fb * fb
    if left_norm == 0.0 or right_norm == 0.0:
        return 1.0
    return 1.0 - dot / (left_norm ** 0.5 * right_norm ** 0.5)


@dataclass(slots=True)
class Node:
    vector: tuple[float, ...]
    neighbors: list[int] = field(default_factory=list)
    deleted: bool = False


class FreshVamana:
    """A compact dynamic ANN graph inspired by the FreshVamana paper.

    The implementation focuses on the behavior QVCache needs from a dynamic
    in-memory ANN index:
    - incremental insertion
    - approximate search
    - lazy deletion
    - periodic consolidation

    It uses a greedy graph traversal and a Vamana-style pruning heuristic to
    keep the graph bounded and navigable.
    """

    def __init__(
        self,
        *,
        max_degree: int = 32,
        build_ef: int = 64,
        search_ef: int = 64,
        alpha: float = 1.2,
        metric: str = "l2",
    ) -> None:
        if max_degree < 1:
            raise ValueError("max_degree must be at least 1")
        if build_ef < 1:
            raise ValueError("build_ef must be at least 1")
        if search_ef < 1:
            raise ValueError("search_ef must be at least 1")
        if alpha < 1.0:
            raise ValueError("alpha must be at least 1.0")

        metric = metric.lower()
        if metric == "l2":
            self._distance: DistanceFn = _l2_distance
        elif metric == "cosine":
            self._distance = _cosine_distance
        else:
            raise ValueError(f"Unsupported metric: {metric}")

        self.max_degree = max_degree
        self.build_ef = build_ef
        self.search_ef = search_ef
        self.alpha = alpha
        self.metric = metric

        self._nodes: list[Node] = []
        self._entrypoint: int | None = None
        self._lock = RLock()

    def __len__(self) -> int:
        return sum(1 for node in self._nodes if not node.deleted)

    @property
    def node_count(self) -> int:
        return len(self._nodes)

    @property
    def active_count(self) -> int:
        return len(self)

    @property
    def deleted_count(self) -> int:
        return sum(1 for node in self._nodes if node.deleted)

    def insert(self, vector: Vector) -> int:
        with self._lock:
            vector_tuple = self._normalize_vector(vector)
            node_id = len(self._nodes)
            self._nodes.append(Node(vector=vector_tuple))

            if self._entrypoint is None:
                self._entrypoint = node_id
                return node_id

            if self.active_count == 1:
                self._entrypoint = 0

            candidates = self._search_candidates(vector_tuple, self.build_ef, allow_deleted=False)
            candidates = [candidate for candidate in candidates if candidate != node_id]
            chosen_neighbors = self._prune_candidates(node_id, candidates)
            self._nodes[node_id].neighbors = chosen_neighbors

            for neighbor_id in chosen_neighbors:
                if neighbor_id == node_id:
                    continue
                neighbor = self._nodes[neighbor_id]
                if node_id not in neighbor.neighbors:
                    neighbor.neighbors.append(node_id)
                    neighbor.neighbors = self._prune_candidates(neighbor_id, neighbor.neighbors)

            self._ensure_entrypoint()
            return node_id

    def search(self, query: Vector, k: int = 10, ef: int | None = None) -> list[tuple[int, float]]:
        if k < 1:
            raise ValueError("k must be at least 1")
        with self._lock:
            active_ids = [node_id for node_id, node in enumerate(self._nodes) if not node.deleted]
            if not active_ids:
                return []
            query_tuple = self._normalize_vector(query)
            ef = max(k, ef or self.search_ef)
            return self._beam_search(query_tuple, k=k, ef=ef, allow_deleted=False)

    def delete(self, node_id: int) -> None:
        with self._lock:
            self._validate_node_id(node_id)
            self._nodes[node_id].deleted = True
            if self._entrypoint == node_id:
                self._entrypoint = self._ensure_entrypoint()

    def consolidate(self) -> dict[int, int]:
        """Rebuild the graph without deleted nodes.

        Returns a mapping from old node IDs to new node IDs.
        """

        with self._lock:
            id_mapping: dict[int, int] = {}
            rebuilt = FreshVamana(
                max_degree=self.max_degree,
                build_ef=self.build_ef,
                search_ef=self.search_ef,
                alpha=self.alpha,
                metric=self.metric,
            )
            for old_id, node in enumerate(self._nodes):
                if node.deleted:
                    continue
                new_id = rebuilt.insert(node.vector)
                id_mapping[old_id] = new_id

            self._nodes = rebuilt._nodes
            self._entrypoint = rebuilt._entrypoint
            return id_mapping

    def get_node(self, node_id: int) -> Node:
        with self._lock:
            self._validate_node_id(node_id)
            return self._nodes[node_id]

    def adjacency_list(self) -> list[list[int]]:
        with self._lock:
            return [list(node.neighbors) for node in self._nodes]

    def _normalize_vector(self, vector: Vector) -> tuple[float, ...]:
        values = tuple(float(component) for component in vector)
        if not values:
            raise ValueError("vectors must contain at least one dimension")
        if self._nodes and len(values) != len(self._nodes[0].vector):
            raise ValueError("vector dimensionality must stay consistent")
        return values

    def _validate_node_id(self, node_id: int) -> None:
        if node_id < 0 or node_id >= len(self._nodes):
            raise IndexError(f"node id {node_id} is out of range")

    def _ensure_entrypoint(self) -> int | None:
        if self._entrypoint is not None and self._entrypoint < len(self._nodes) and not self._nodes[self._entrypoint].deleted:
            return self._entrypoint
        for node_id, node in enumerate(self._nodes):
            if not node.deleted:
                self._entrypoint = node_id
                return node_id
        self._entrypoint = None
        return None

    def _search_candidates(self, query: Vector, limit: int, *, allow_deleted: bool) -> list[int]:
        return [node_id for node_id, _ in self._beam_search(query, k=limit, ef=limit, allow_deleted=allow_deleted)]

    def _beam_search(
        self,
        query: Vector,
        *,
        k: int,
        ef: int,
        allow_deleted: bool,
    ) -> list[tuple[int, float]]:
        entrypoint = self._ensure_entrypoint()
        if entrypoint is None:
            return []

        query_vector = tuple(float(component) for component in query)
        candidate_heap: list[tuple[float, int]] = []
        result_heap: list[tuple[float, int]] = []
        visited: set[int] = {entrypoint}

        entry_distance = self._distance(query_vector, self._nodes[entrypoint].vector)
        heappush(candidate_heap, (entry_distance, entrypoint))

        while candidate_heap:
            best_candidate_distance, _ = candidate_heap[0]
            worst_result_distance = -result_heap[0][0] if result_heap else float("inf")
            if len(result_heap) >= ef and best_candidate_distance > worst_result_distance:
                break

            current_distance, current_id = heappop(candidate_heap)
            current_node = self._nodes[current_id]

            if allow_deleted or not current_node.deleted:
                heappush(result_heap, (-current_distance, current_id))
                if len(result_heap) > ef:
                    heappop(result_heap)

            if current_node.deleted and not allow_deleted:
                continue

            for neighbor_id in current_node.neighbors:
                if neighbor_id in visited:
                    continue
                visited.add(neighbor_id)
                neighbor = self._nodes[neighbor_id]
                heappush(candidate_heap, (self._distance(query_vector, neighbor.vector), neighbor_id))

        results = [
            (node_id, -distance)
            for distance, node_id in result_heap
            if allow_deleted or not self._nodes[node_id].deleted
        ]
        results.sort(key=lambda item: item[1])
        return results[:k]

    def _prune_candidates(self, base_id: int, candidate_ids: Iterable[int]) -> list[int]:
        base_vector = self._nodes[base_id].vector
        filtered = [candidate_id for candidate_id in candidate_ids if candidate_id != base_id and not self._nodes[candidate_id].deleted]
        filtered.sort(key=lambda candidate_id: self._distance(base_vector, self._nodes[candidate_id].vector))

        selected: list[int] = []
        for candidate_id in filtered:
            candidate_vector = self._nodes[candidate_id].vector
            candidate_distance = self._distance(base_vector, candidate_vector)
            if candidate_distance == 0.0:
                selected.append(candidate_id)
                continue
            keep = True
            for selected_id in selected:
                selected_vector = self._nodes[selected_id].vector
                if self._distance(candidate_vector, selected_vector) <= self.alpha * candidate_distance:
                    keep = False
                    break
            if keep:
                selected.append(candidate_id)
            if len(selected) >= self.max_degree:
                break

        if not selected and filtered:
            selected = filtered[: self.max_degree]
        return selected
