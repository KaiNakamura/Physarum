import random
import heapq
from map import Map
from city import City
from geopy.point import Point
from geopy.distance import distance as geopy_distance
from tabulate import tabulate
import math

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
            for (b, dist) in self.graph_dict[a].items():
                self.connect1(b, a, dist)

    def connect(self, A, B, distance=1):
        """Add a link from A and B of given distance, and also add the inverse
        link if the graph is undirected."""
        self.connect1(A, B, distance)
        if not self.directed:
            self.connect1(B, A, distance)

    def connect1(self, A, B, distance):
        """Add a link from A to B of given distance, in one direction only."""
        self.graph_dict.setdefault(A, {})[B] = distance

    def get(self, a, b=None):
        """Return a link distance or a dict of {node: distance} entries."""
        links = self.graph_dict.setdefault(a, {})
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
    """Build a Graph where every edge (including future ones) goes both ways."""
    return Graph(graph_dict=graph_dict, directed=False)

def build_graph_from_cities(cities, k=2):
    """Build a graph by connecting each city to its k nearest neighbors."""
    graph = UndirectedGraph()
    for city in cities:
        distances = []
        for other_city in cities:
            if other_city != city:
                dist = geopy_distance(city.coordinates, other_city.coordinates).kilometers
                distances.append((other_city.name, dist))
        # Sort distances
        distances.sort(key=lambda x: x[1])
        # Get k nearest neighbors
        nearest_neighbors = distances[:k]
        # Connect to k nearest neighbors
        for neighbor_name, dist in nearest_neighbors:
            graph.connect(city.name, neighbor_name, dist)
    return graph

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

def fault_tolerance_metric(graph, city_populations, total_population):
    """Compute the fault tolerance metric as specified."""
    edges = get_edges(graph)
    fault_metrics = []
    num_edges = len(edges)
    for edge in edges:
        node_a, node_b = edge
        # Remove edge
        original_distance = graph.get(node_a)[node_b]
        del graph.graph_dict[node_a][node_b]
        del graph.graph_dict[node_b][node_a]
        # Get connected components
        connected_components = get_connected_components(graph)
        # Map each city to its connected component
        city_to_component = {}
        for component in connected_components:
            for city in component:
                city_to_component[city] = component
        # Compute the proportion of the population that each city can reach
        proportions = []
        for city in graph.nodes():
            component = city_to_component[city]
            component_population = sum(city_populations[member] for member in component)
            proportion = component_population / total_population
            proportions.append(proportion)
        # Compute the average of these proportions
        average_proportion = sum(proportions) / len(proportions)
        # Compute average shortest path length in the largest connected component
        largest_component = max(connected_components, key=len)
        subgraph = subgraph_induced(graph, largest_component)
        avg_shortest_path = average_shortest_path_length(subgraph)
        # Compute fault tolerance metric
        if average_proportion > 0:
            fault_metric = avg_shortest_path / math.sqrt(average_proportion)
        else:
            fault_metric = float('inf')
        fault_metrics.append(fault_metric)
        # Restore edge
        graph.connect(node_a, node_b, original_distance)
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

def main():
    # List of City objects
    cities = [
        City("Boston", 650706, Point("42.3601 N 71.0589 W")),
        City("Worcester", 205319, Point("42.2626 N 71.8023 W")),
        City("Springfield", 153337, Point("42.1015 N 72.5898 W")),
        City("Cambridge", 119008, Point("42.3736 N 71.1097 W")),
        City("Lowell", 114401, Point("42.6334 N 71.3162 W")),
        City("Brockton", 104889, Point("42.0834 N 71.0184 W")),
        City("New Bedford", 100757, Point("41.6362 N 70.9342 W")),
        City("Quincy", 101380, Point("42.2529 N 71.0023 W")),
        City("Lynn", 101603, Point("42.4668 N 70.9495 W")),
        City("Fall River", 94044, Point("41.7015 N 71.1550 W")),
    ]
    # Create a mapping from city names to populations
    city_populations = {city.name: city.population for city in cities}
    total_population = sum(city_populations.values())
    # Build the graphs from cities
    two_graph = build_graph_from_cities(cities, k=2)
    three_graph = build_graph_from_cities(cities, k=3)

    # Calculate metrics for both graphs
    metrics = {
        'Total Network Length (km)': {
            '2-Nearest Neighbors': total_network_length(two_graph),
            '3-Nearest Neighbors': total_network_length(three_graph)
        },
        'Average Shortest Path Length (km)': {
            '2-Nearest Neighbors': average_shortest_path_length(two_graph),
            '3-Nearest Neighbors': average_shortest_path_length(three_graph)
        },
        'Fault Tolerance Metric': {
            '2-Nearest Neighbors': fault_tolerance_metric(two_graph, city_populations, total_population),
            '3-Nearest Neighbors': fault_tolerance_metric(three_graph, city_populations, total_population)
        }
    }

    # Prepare data for tabulate
    table = []
    for metric_name, values in metrics.items():
        value_two = f"{values['2-Nearest Neighbors']:.2f}"
        value_three = f"{values['3-Nearest Neighbors']:.2f}"
        table.append([metric_name, value_two, value_three])

    # Print the table using tabulate
    headers = ['Metric', '2-Nearest Neighbors', '3-Nearest Neighbors']
    print("\nComparison of Graphs with 2 and 3 Nearest Neighbors:")
    print(tabulate(table, headers=headers, tablefmt="github"))

if __name__ == "__main__":
    main()
