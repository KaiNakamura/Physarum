import math
from skimage.morphology import skeletonize
import skimage as ski
import matplotlib.pyplot as plt
from skimage.util import invert
import networkx as nx
from search import UndirectedGraph

# open an example image as black and white
image = ski.io.imread("Figure_1.PNG", as_gray=True)
# image = ski.io.imread("output.PNG", as_gray=True

# convert all grey to black
image = image > 0.5

# Invert the horse image
# image = invert(ski.data.horse())
# perform skeletonization
skeleton = skeletonize(image)


# construct graph from skeleton
# a junction is a pixel with more than 2 neighbors
# a terminal is a pixel with only 1 neighbor

# make nodes from junctions and terminals
G = nx.Graph()

neighbors = []

for i in range(skeleton.shape[0]):
    for j in range(skeleton.shape[1]):
        if not (skeleton[i, j]):
            continue

        num_neighbors = 0

        for direction in [
            (0, 1),
            (0, -1),
            (1, 0),
            (-1, 0),
            (1, 1),
            (1, -1),
            (-1, 1),
            (-1, -1),
        ]:
            new_i = i + direction[0]
            new_j = j + direction[1]

            if (
                new_i < 0
                or new_i >= skeleton.shape[0]
                or new_j < 0
                or new_j >= skeleton.shape[1]
            ):
                continue

            if skeleton[new_i, new_j]:
                num_neighbors += 1

        # If num neighbors is greater than 3 kill nodes until only 3 neighbors are left
        if num_neighbors > 2:
            neighbors.append((i, j))
            # G.add_node((j, i), pos=(j, i), junction=True)

# remove nodes that are too close to each other by bucketing with a grid size of 3
# pick one node from each bucket

join_mapping = {}  # rev coord format

for i, j in neighbors:
    # Find all neighbors with distance less than 3
    close_neighbors = []
    for i2, j2 in neighbors:
        if i == i2 and j == j2:
            continue

        if math.sqrt((i - i2) ** 2 + (j - j2) ** 2) < 3:
            close_neighbors.append((i2, j2))
            join_mapping[(j2, i2)] = (j, i)
            # join_mapping[(j, i)] = (j, i)

    # Remove all close neighbors but prefer to keep
    # neighbors with highest bordering neighbors
    highest_bordering = 0
    highest_bordering_node = None

    for neighbor in close_neighbors + [(i, j)]:
        for direction in [
            (0, 1),
            (0, -1),
            (1, 0),
            (-1, 0),
        ]:
            new_i = i + direction[0]
            new_j = j + direction[1]

            if skeleton[new_i, new_j]:
                highest_bordering += 1
                highest_bordering_node = neighbor

    # remove all except the one with the highest bordering neighbors

    for neighbor in close_neighbors:
        if neighbor != highest_bordering_node:
            neighbors.remove(neighbor)


# add to graph
for i, j in neighbors:
    G.add_node((j, i), pos=(j, i), junction=True)


def to_exploreed_string(i, j):
    return str(i) + "." + str(j)


# iterate over all nodes and find connections to other nodes by "walking" in the skeleton to the next junction
for node in list(G.nodes()):
    i, j = node
    orig_i, orig_j = i, j

    print("junction", i, j)

    done = False
    didMove = False
    explored = set()

    explored.add(to_exploreed_string(i, j))
    reachable = []

    queue = [((orig_i, orig_j), (i, j))]

    # Perform BFS to find all reachable junctions
    while queue:
        from_node, current_node = queue.pop(0)

        for direction in [
            (0, 1),
            (0, -1),
            (1, 0),
            (-1, 0),
            (1, 1),
            (1, -1),
            (-1, 1),
            (-1, -1),
        ]:
            new_i = current_node[0] + direction[0]
            new_j = current_node[1] + direction[1]

            coord_str = to_exploreed_string(new_i, new_j)

            # Check bounds
            if (
                new_j < 0
                or new_j >= skeleton.shape[0]
                or new_i < 0
                or new_i >= skeleton.shape[1]
            ):
                continue
            # print("new", new_i, new_j, skeleton[new_i, new_j])

            skip = False

            if skeleton[new_j, new_i] and not coord_str in explored:
                print("exploring", new_i, new_j, skeleton[new_j, new_i])

                actual_node = (new_i, new_j)

                # actual_node = join_mapping.get((new_i, new_j), (new_i, new_j))
                if actual_node == from_node:
                    continue

                if G.nodes.get(actual_node, {}):
                    print("found junction", new_i, new_j)
                    if not G.has_edge(from_node, actual_node):
                        G.add_edge(from_node, actual_node)
                    explored.add(coord_str)
                    # queue.append((actual_node, actual_node))
                    continue

                explored.add(coord_str)
                queue.append((from_node, actual_node))


# display results
fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(8, 4), sharex=True, sharey=True)

ax = axes.ravel()

ax[0].imshow(image, cmap=plt.cm.gray)
ax[0].axis("off")
ax[0].set_title("original", fontsize=20)

ax[1].imshow(skeleton, cmap=plt.cm.gray)
ax[1].axis("off")
ax[1].set_title("skeleton", fontsize=20)

# draw the graph
pos = nx.get_node_attributes(G, "pos")
nx.draw(G, pos, ax=ax[2], node_size=20, with_labels=True, edge_color="b")


fig.tight_layout()
plt.show()

# romania_map = UndirectedGraph(
#     dict(
#         Arad=dict(Zerind=75, Sibiu=140, Timisoara=118),
#         Bucharest=dict(Urziceni=85, Pitesti=101, Giurgiu=90, Fagaras=211),
#         Craiova=dict(Drobeta=120, Rimnicu=146, Pitesti=138),
#         Drobeta=dict(Mehadia=75),
#         Eforie=dict(Hirsova=86),
#         Fagaras=dict(Sibiu=99),
#         Hirsova=dict(Urziceni=98),
#         Iasi=dict(Vaslui=92, Neamt=87),
#         Lugoj=dict(Timisoara=111, Mehadia=70),
#         Oradea=dict(Zerind=71, Sibiu=151),
#         Pitesti=dict(Rimnicu=97),
#         Rimnicu=dict(Sibiu=80),
#         Urziceni=dict(Vaslui=142),
#     )
# )

# dump graph dict to file
import pickle

with open("graph.pkl", "wb") as f:
    pickle.dump(
        {node: {neighbor: 1 for neighbor in G.neighbors(node)} for node in G.nodes()}, f
    )

# # Convert networkx graph to search graph
# graph = UndirectedGraph(
#     {node: {neighbor: 1 for neighbor in G.neighbors(node)} for node in G.nodes()}
# )
