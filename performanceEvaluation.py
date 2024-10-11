import heapq
import math
import pickle
import os
from tabulate import tabulate

class Graph:
    """A graph connects nodes (vertices) by edges (links). Each edge can also
    have a length associated with it."""

    def __init__(self, graph_dict=None, directed=True):
        self.graph_dict = graph_dict or {}
        self.directed = directed
        if not directed:
            self.make_undirected()

    def make_undirected(self):
        """Make a digraph into an undirected graph by adding symmetric edges."""
        for a in list(self.graph_dict.keys()):
            for (b, dist) in list(self.graph_dict[a].items()):
                self.connect1(b, a, dist)

    def connect(self, A, B, distance=1):
        """Add a link from A to B of given distance, and also add the inverse
        link if the graph is undirected."""
        self.connect1(A, B, distance)
        if not self.directed:
            self.connect1(B, A, distance)

    def connect1(self, A, B, distance):
        """Add a link from A to B of given distance, in one direction only."""
        self.graph_dict.setdefault(A, {})[B] = distance

    def get(self, a, b=None):
        """Return a link distance or a dict of {node: distance} entries."""
        links = self.graph_dict.get(a, {})
        if b is None:
            return links
        else:
            return links.get(b)

    def nodes(self):
        """Return a list of nodes in the graph."""
        s1 = set(self.graph_dict.keys())
        s2 = set(k for v in self.graph_dict.values() for k in v.keys())
        nodes = s1.union(s2)
        return list(nodes)

def UndirectedGraph(graph_dict=None):
    """Build a Graph where every edge goes both ways."""
    return Graph(graph_dict=graph_dict, directed=False)

def build_graph_from_positions(node_positions, k=2):
    """Build a graph by connecting each node to its k nearest neighbors."""
    graph = UndirectedGraph()
    nodes = list(node_positions.keys())
    for node in nodes:
        distances = []
        x1, y1 = node_positions[node]
        for other_node in nodes:
            if other_node != node:
                x2, y2 = node_positions[other_node]
                dist = math.hypot(x2 - x1, y2 - y1)
                distances.append((other_node, dist))
        # Sort distances
        distances.sort(key=lambda x: x[1])
        # Get k nearest neighbors
        nearest_neighbors = distances[:k]
        # Connect to k nearest neighbors
        for neighbor_node, dist in nearest_neighbors:
            graph.connect(node, neighbor_node, dist)
    return graph

def build_mst(node_positions):
    """Build a Minimum Spanning Tree (MST) from the nodes using Kruskal's algorithm."""
    parent = {}
    rank = {}
    def find(node):
        while parent[node] != node:
            parent[node] = parent[parent[node]]
            node = parent[node]
        return node
    def union(u, v):
        u_root = find(u)
        v_root = find(v)
        if u_root == v_root:
            return
        if rank[u_root] < rank[v_root]:
            parent[u_root] = v_root
        else:
            parent[v_root] = u_root
            if rank[u_root] == rank[v_root]:
                rank[u_root] += 1
    edges = []
    nodes = list(node_positions.keys())
    # Create all possible edges
    for i, node in enumerate(nodes):
        x1, y1 = node_positions[node]
        for j in range(i+1, len(nodes)):
            other_node = nodes[j]
            x2, y2 = node_positions[other_node]
            dist = math.hypot(x2 - x1, y2 - y1)
            edges.append((dist, node, other_node))
    # Initialize disjoint sets
    for node in nodes:
        parent[node] = node
        rank[node] = 0
    # Kruskal's algorithm
    edges.sort()
    mst = UndirectedGraph()
    for dist, u, v in edges:
        if find(u) != find(v):
            union(u, v)
            mst.connect(u, v, dist)
    return mst

def total_network_length(graph):
    """Calculate the total length of all edges in the network."""
    total_length = 0
    seen_edges = set()
    for node in graph.nodes():
        for neighbor, distance in graph.get(node).items():
            edge = tuple(sorted((node, neighbor)))
            if edge not in seen_edges:
                total_length += distance
                seen_edges.add(edge)
    return total_length

def dijkstra(graph, start):
    """Compute the shortest paths from start node to all other nodes in the graph."""
    distances = {node: float('inf') for node in graph.nodes()}
    distances[start] = 0
    priority_queue = [(0, start)]
    while priority_queue:
        current_distance, current_node = heapq.heappop(priority_queue)
        if current_distance > distances[current_node]:
            continue
        for neighbor, weight in graph.get(current_node).items():
            distance = current_distance + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                heapq.heappush(priority_queue, (distance, neighbor))
    return distances

def average_shortest_path_length(graph):
    """Compute the average shortest path length between all pairs of nodes."""
    nodes = graph.nodes()
    total_distance = 0
    num_pairs = 0
    node_list = list(nodes)
    n = len(node_list)
    for i in range(n):
        node_i = node_list[i]
        distances = dijkstra(graph, node_i)
        for j in range(i+1, n):
            node_j = node_list[j]
            distance = distances[node_j]
            if distance < float('inf'):
                total_distance += distance
                num_pairs += 1
    average_distance = total_distance / num_pairs if num_pairs > 0 else float('inf')
    return average_distance

def get_edges(graph):
    """Return a list of unique edges in the graph."""
    edges = set()
    for node in graph.nodes():
        for neighbor in graph.get(node).keys():
            edge = tuple(sorted((node, neighbor)))
            edges.add(edge)
    return list(edges)

def get_connected_components(graph):
    """Get the list of connected components in the graph."""
    visited = set()
    nodes = set(graph.nodes())
    components = []
    while nodes:
        start_node = nodes.pop()
        stack = [start_node]
        component = set()
        while stack:
            node = stack.pop()
            if node not in visited:
                visited.add(node)
                component.add(node)
                neighbors = graph.get(node).keys()
                for neighbor in neighbors:
                    if neighbor not in visited:
                        stack.append(neighbor)
        components.append(component)
        nodes -= component
    return components

def fault_tolerance_metric(graph):
    """Compute the fault tolerance metric based on number of nodes reachable."""
    import copy
    graph_copy = copy.deepcopy(graph)
    edges = get_edges(graph_copy)
    fault_metrics = []
    num_edges = len(edges)
    total_nodes = len(graph_copy.nodes())
    for edge in edges:
        node_a, node_b = edge
        # Remove edge
        original_distance = graph_copy.get(node_a)[node_b]
        del graph_copy.graph_dict[node_a][node_b]
        del graph_copy.graph_dict[node_b][node_a]
        # Get connected components
        connected_components = get_connected_components(graph_copy)
        # Map each node to its connected component
        node_to_component = {}
        for component in connected_components:
            for node in component:
                node_to_component[node] = component
        # Compute the proportion of nodes that each node can reach
        proportions = []
        for node in graph_copy.nodes():
            component = node_to_component[node]
            component_size = len(component)
            proportion = component_size / total_nodes
            proportions.append(proportion)
        # Compute the average of these proportions
        average_proportion = sum(proportions) / len(proportions)
        # Compute average shortest path length in the largest connected component
        largest_component = max(connected_components, key=len)
        subgraph = subgraph_induced(graph_copy, largest_component)
        avg_shortest_path = average_shortest_path_length(subgraph)
        # Compute fault tolerance metric
        if average_proportion > 0:
            fault_metric = avg_shortest_path / math.sqrt(average_proportion)
        else:
            fault_metric = float('inf')
        fault_metrics.append(fault_metric)
        # Restore edge
        graph_copy.connect(node_a, node_b, original_distance)
    # Compute the average of fault metrics
    fault_tolerance_value = sum(fault_metrics) / num_edges if num_edges > 0 else float('inf')
    return fault_tolerance_value

def subgraph_induced(graph, nodes_set):
    """Return the subgraph induced by nodes_set."""
    new_graph_dict = {}
    for node in nodes_set:
        new_graph_dict[node] = {}
        for neighbor, distance in graph.get(node).items():
            if neighbor in nodes_set:
                new_graph_dict[node][neighbor] = distance
    new_graph = UndirectedGraph(new_graph_dict)
    return new_graph

def update_edge_lengths(graph):
    """Update the edge lengths in the graph to be the Euclidean distance between nodes."""
    for node in graph.nodes():
        neighbors = list(graph.get(node).keys())
        x1, y1 = node  # Node is a tuple of (x, y)
        for neighbor in neighbors:
            x2, y2 = neighbor  # Neighbor is also a tuple of (x, y)
            distance = math.hypot(x2 - x1, y2 - y1)
            graph.graph_dict[node][neighbor] = distance
    return graph

def main():
    base_path = "/Results Graphs/"
    metrics_per_graph = {}

    for i in range(1, 11):
        file_path = os.path.join(base_path, f"{i}.pkl")
        if not os.path.exists(file_path):
            print(f"File {file_path} does not exist.")
            continue

        with open(file_path, "rb") as f:
            graph_dict = pickle.load(f)
            graph = UndirectedGraph(graph_dict)

            # Since nodes are positions, we can use them directly
            node_positions = {node: node for node in graph.nodes()}

            # Update edge lengths in the Slime graph
            graph = update_edge_lengths(graph)

            # Build 2-nearest and 3-nearest neighbor graphs
            two_graph = build_graph_from_positions(node_positions, k=2)
            three_graph = build_graph_from_positions(node_positions, k=3)

            # Build Minimum Spanning Tree
            mst_graph = build_mst(node_positions)

            # Calculate metrics for all graphs
            metrics = {
                'Total Network Length': {
                    '2-Nearest Neighbors': total_network_length(two_graph),
                    '3-Nearest Neighbors': total_network_length(three_graph),
                    'Slime graph': total_network_length(graph),
                    'Shortest Path graph': total_network_length(mst_graph)
                },
                'Average Shortest Path Length': {
                    '2-Nearest Neighbors': average_shortest_path_length(two_graph),
                    '3-Nearest Neighbors': average_shortest_path_length(three_graph),
                    'Slime graph': average_shortest_path_length(graph),
                    'Shortest Path graph': average_shortest_path_length(mst_graph)
                },
                'Fault Tolerance Metric': {
                    '2-Nearest Neighbors': fault_tolerance_metric(two_graph),
                    '3-Nearest Neighbors': fault_tolerance_metric(three_graph),
                    'Slime graph': fault_tolerance_metric(graph),
                    'Shortest Path graph': fault_tolerance_metric(mst_graph)
                }
            }

            metrics_per_graph[f"Graph {i}"] = metrics

    # Prepare data for tabulate
    graph_types = ['2-Nearest Neighbors', '3-Nearest Neighbors', 'Slime graph', 'Shortest Path graph']
    for metric_name in ['Total Network Length', 'Average Shortest Path Length', 'Fault Tolerance Metric']:
        table = []
        headers = ['Graph'] + graph_types
        sum_values = {graph_type: 0.0 for graph_type in graph_types}
        count = 0
        for graph_name, metrics in metrics_per_graph.items():
            values = metrics[metric_name]
            row = [graph_name]
            for graph_type in graph_types:
                value = values[graph_type]
                sum_values[graph_type] += value
                row.append(f"{value:.2f}")
            count += 1
            table.append(row)

        # Compute averages
        avg_row = ['Average']
        for graph_type in graph_types:
            avg_value = sum_values[graph_type] / count if count > 0 else float('inf')
            avg_row.append(f"{avg_value:.2f}")
        table.append(avg_row)

        print(f"\n{metric_name}:")
        print(tabulate(table, headers=headers, tablefmt="github"))

if __name__ == "__main__":
    main()
