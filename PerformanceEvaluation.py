import random
import heapq

class Graph:
    """A graph connects nodes (vertices) by edges (links). Each edge can also
    have a length associated with it. The constructor call is something like:
        g = Graph({'A': {'B': 1, 'C': 2})
    this makes a graph with 3 nodes, A, B, and C, with an edge of length 1 from
    A to B,  and an edge of length 2 from A to C. You can also do:
        g = Graph({'A': {'B': 1, 'C': 2}, directed=False)
    This makes an undirected graph, so inverse links are also added. The graph
    stays undirected; if you add more links with g.connect('B', 'C', 3), then
    inverse link is also added. You can use g.nodes() to get a list of nodes,
    g.get('A') to get a dict of links out of A, and g.get('A', 'B') to get the
    length of the link from A to B. 'Lengths' can actually be any object at
    all, and nodes can be any hashable object."""

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
        """Return a link distance or a dict of {node: distance} entries.
        .get(a,b) returns the distance or None;
        .get(a) returns a dict of {node: distance} entries, possibly {}."""
        links = self.graph_dict.setdefault(a, {})
        if b is None:
            return links
        else:
            return links.get(b)

    def nodes(self):
        """Return a list of nodes in the graph."""
        s1 = set([k for k in self.graph_dict.keys()])
        s2 = set([k2 for v in self.graph_dict.values() for k2, v2 in v.items()])
        nodes = s1.union(s2)
        return list(nodes)


def UndirectedGraph(graph_dict=None):
    """Build a Graph where every edge (including future ones) goes both ways."""
    return Graph(graph_dict=graph_dict, directed=False)


def create_massachusetts_graph():
    """Create a sample graph representing major cities in Massachusetts."""
    g = UndirectedGraph()
    g.connect('Boston', 'Cambridge', 3)
    g.connect('Boston', 'Quincy', 10)
    g.connect('Boston', 'Worcester', 40)
    g.connect('Boston', 'Lynn', 12)
    g.connect('Boston', 'Brockton', 25)
    g.connect('Cambridge', 'Lowell', 25)
    g.connect('Lowell', 'Lawrence', 10)
    g.connect('Worcester', 'Springfield', 52)
    g.connect('Worcester', 'Lowell', 50)
    g.connect('Springfield', 'Chicopee', 5)
    g.connect('Quincy', 'Brockton', 15)
    g.connect('Brockton', 'Fall River', 35)
    g.connect('Fall River', 'New Bedford', 15)
    g.connect('New Bedford', 'Brockton', 30)
    return g

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
        (current_distance, current_node) = heapq.heappop(priority_queue)
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
    average_distance = total_distance / num_pairs if num_pairs > 0 else 0
    return average_distance

def get_edges(graph):
    """Return a list of unique edges in the graph."""
    edges = set()
    for node in graph.nodes():
        for neighbor in graph.get(node).keys():
            edge = tuple(sorted((node, neighbor)))
            edges.add(edge)
    return list(edges)

def is_connected(graph):
    """Check if the graph is connected."""
    start_node = next(iter(graph.nodes()))
    visited = set()
    stack = [start_node]
    while stack:
        node = stack.pop()
        if node not in visited:
            visited.add(node)
            neighbors = graph.get(node).keys()
            stack.extend(neighbors)
    return len(visited) == len(graph.nodes())

def fault_tolerance_analysis(graph):
    """Analyze the effect of removing each edge on the average shortest path length."""
    edges = get_edges(graph)
    results = []
    for edge in edges:
        node_a, node_b = edge
        # Remove edge
        original_distance = graph.get(node_a)[node_b]
        del graph.graph_dict[node_a][node_b]
        del graph.graph_dict[node_b][node_a]
        # Check if the graph is connected
        if is_connected(graph):
            # Recompute average shortest path length
            new_average = average_shortest_path_length(graph)
            results.append((edge, new_average))
        else:
            results.append((edge, float('inf')))  # Indicate that graph is disconnected
        # Restore edge
        graph.connect(node_a, node_b, original_distance)
    return results

def main():
    graph = create_massachusetts_graph()
    total_length = total_network_length(graph)
    print(f"Total network length: {total_length}")
    avg_distance = average_shortest_path_length(graph)
    print(f"Average shortest path length: {avg_distance}")
    fault_results = fault_tolerance_analysis(graph)
    print("\nFault tolerance analysis:")
    for edge, new_avg in fault_results:
        if new_avg == float('inf'):
            print(f"Removing edge {edge} disconnects the graph.")
        else:
            print(f"Removing edge {edge} increases average shortest path length to: {new_avg}")

if __name__ == "__main__":
    main()
