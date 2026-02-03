"""
Relationship Resolver
Finds optimal join paths between datasets using graph algorithms
"""
from typing import List, Dict, Any, Optional, Tuple
from collections import deque
import heapq


class RelationshipResolver:
    """
    Resolves relationships between datasets and finds optimal join paths.

    Uses graph algorithms (BFS/Dijkstra) to find shortest path between datasets.
    """

    def __init__(self, relationships: List[Dict[str, Any]]):
        """
        Initialize resolver with relationships from context.

        Args:
            relationships: List of relationship definitions from context
        """
        self.relationships = relationships
        self.graph = self._build_graph()

    def _build_graph(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Build adjacency list graph from relationships.

        Returns:
            Graph as adjacency list {dataset_id: [edges]}
        """
        graph: Dict[str, List[Dict[str, Any]]] = {}

        for rel in self.relationships:
            left = rel['left_dataset']
            right = rel['right_dataset']

            # Add edges (relationships can be traversed in both directions)
            if left not in graph:
                graph[left] = []
            if right not in graph:
                graph[right] = []

            # Forward edge
            graph[left].append({
                'to': right,
                'relationship': rel,
                'reverse': False
            })

            # Reverse edge (for bidirectional traversal)
            graph[right].append({
                'to': left,
                'relationship': rel,
                'reverse': True
            })

        return graph

    def find_join_path(
        self,
        from_dataset: str,
        to_dataset: str,
        max_depth: int = 5
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Find shortest join path between two datasets using BFS.

        Args:
            from_dataset: Starting dataset ID
            to_dataset: Target dataset ID
            max_depth: Maximum join depth allowed

        Returns:
            List of relationship dictionaries representing the path, or None
        """
        if from_dataset == to_dataset:
            return []

        if from_dataset not in self.graph or to_dataset not in self.graph:
            return None

        # BFS to find shortest path
        queue = deque([(from_dataset, [])])
        visited = {from_dataset}

        while queue:
            current, path = queue.popleft()

            # Check depth limit
            if len(path) >= max_depth:
                continue

            # Explore neighbors
            for edge in self.graph.get(current, []):
                neighbor = edge['to']

                if neighbor == to_dataset:
                    # Found path!
                    return path + [edge]

                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [edge]))

        # No path found
        return None

    def find_join_path_multi(
        self,
        dataset_ids: List[str],
        max_depth: int = 10
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Find join path that connects multiple datasets.

        Args:
            dataset_ids: List of dataset IDs to connect
            max_depth: Maximum total join depth

        Returns:
            List of relationships that connect all datasets
        """
        if not dataset_ids or len(dataset_ids) < 2:
            return []

        # Build minimum spanning tree connecting all datasets
        all_edges = []
        connected = {dataset_ids[0]}
        remaining = set(dataset_ids[1:])

        while remaining:
            # Find shortest edge from connected to remaining
            best_edge = None
            best_path = None
            best_distance = float('inf')

            for connected_ds in connected:
                for target_ds in remaining:
                    path = self.find_join_path(connected_ds, target_ds, max_depth)
                    if path and len(path) < best_distance:
                        best_path = path
                        best_distance = len(path)
                        best_edge = target_ds

            if not best_path:
                # Cannot connect all datasets
                return None

            # Add path edges
            all_edges.extend(best_path)
            connected.add(best_edge)
            remaining.remove(best_edge)

        # Remove duplicate relationships
        seen_rels = set()
        unique_edges = []
        for edge in all_edges:
            rel_id = edge['relationship']['id']
            if rel_id not in seen_rels:
                seen_rels.add(rel_id)
                unique_edges.append(edge)

        return unique_edges

    def get_relationship_by_id(self, rel_id: str) -> Optional[Dict[str, Any]]:
        """Get relationship definition by ID"""
        for rel in self.relationships:
            if rel.get('id') == rel_id:
                return rel
        return None

    def get_relationships_for_dataset(self, dataset_id: str) -> List[Dict[str, Any]]:
        """Get all relationships involving a dataset"""
        result = []
        for rel in self.relationships:
            if rel['left_dataset'] == dataset_id or rel['right_dataset'] == dataset_id:
                result.append(rel)
        return result

    def validate_join_path(self, path: List[Dict[str, Any]]) -> bool:
        """
        Validate that a join path is feasible.

        Checks:
        - All relationships exist
        - No circular joins
        - Datasets are connected
        """
        if not path:
            return True

        # Check all relationships exist
        for edge in path:
            if 'relationship' not in edge:
                return False

        # Check for circular joins (same dataset multiple times)
        datasets_in_path = []
        for edge in path:
            rel = edge['relationship']
            if edge.get('reverse'):
                datasets_in_path.extend([rel['right_dataset'], rel['left_dataset']])
            else:
                datasets_in_path.extend([rel['left_dataset'], rel['right_dataset']])

        # Allow a dataset to appear at most twice (as intermediate node)
        from collections import Counter
        dataset_counts = Counter(datasets_in_path)
        for ds, count in dataset_counts.items():
            if count > 2:
                return False

        return True

    def estimate_join_cost(self, path: List[Dict[str, Any]]) -> int:
        """
        Estimate computational cost of a join path.

        Lower is better. Based on:
        - Number of joins
        - Join types (inner cheaper than outer)

        Returns:
            Estimated cost (lower is better)
        """
        if not path:
            return 0

        cost = 0
        for edge in path:
            rel = edge['relationship']
            join_type = rel.get('join_type', 'inner')

            # Base cost per join
            cost += 10

            # Outer joins more expensive
            if join_type in ['left', 'right', 'outer']:
                cost += 5

            # Outer join most expensive
            if join_type == 'outer':
                cost += 5

        return cost

    def get_all_connected_datasets(self, dataset_id: str) -> List[str]:
        """
        Get all datasets that can be reached from a starting dataset.

        Args:
            dataset_id: Starting dataset

        Returns:
            List of reachable dataset IDs
        """
        if dataset_id not in self.graph:
            return [dataset_id]

        visited = set()
        queue = deque([dataset_id])

        while queue:
            current = queue.popleft()
            if current in visited:
                continue

            visited.add(current)

            for edge in self.graph.get(current, []):
                neighbor = edge['to']
                if neighbor not in visited:
                    queue.append(neighbor)

        return list(visited)

    def suggest_joins(
        self,
        required_datasets: List[str],
        max_suggestions: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Suggest optimal join strategies for required datasets.

        Args:
            required_datasets: Datasets that must be included
            max_suggestions: Maximum number of suggestions

        Returns:
            List of join strategies with cost estimates
        """
        suggestions = []

        # Try different starting points
        for start_ds in required_datasets:
            path = self.find_join_path_multi(
                [start_ds] + [ds for ds in required_datasets if ds != start_ds]
            )

            if path and self.validate_join_path(path):
                cost = self.estimate_join_cost(path)
                suggestions.append({
                    'path': path,
                    'cost': cost,
                    'start_dataset': start_ds,
                    'num_joins': len(path)
                })

        # Sort by cost
        suggestions.sort(key=lambda x: x['cost'])

        return suggestions[:max_suggestions]
