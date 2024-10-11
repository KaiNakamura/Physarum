import math
from skimage.morphology import skeletonize
import skimage as ski
import matplotlib.pyplot as plt
from skimage.util import invert
import networkx as nx
from search import UndirectedGraph

# open an example image as black and white
image = ski.io.imread("Figure_2.PNG", as_gray=True)
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

# perform BFS to construct the graph
visited = set()

for i in range(skeleton.shape[0]):
    for j in range(skeleton.shape[1]):
        if skeleton[i, j]:
            node = (j, i)
            G.add_node(node, pos=node)
            visited.add(node)

            for direction in [
                (1, 0),
                (0, 1),
                (-1, 0),
                (0, -1),
                (1, 1),
                (-1, 1),
                (1, -1),
                (-1, -1),
            ]:
                new_node = (node[0] + direction[0], node[1] + direction[1])

                if new_node in visited:
                    G.add_edge(node, new_node)


print("Number of nodes:", len(G.nodes()))
# # While there are nodes that are not branchpoints/endpoints
# #     Select one of these nodes.
# #     Merge its two edges into one by removing the node.

while True:

    disconnected = False

    for node in list(G.nodes()):
        # print(i, node, len(list(G.neighbors(node))))
        # input()
        if G.degree(node) == 0:
            G.remove_node(node)

        elif G.degree(node) == 2:
            neighbors = list(G.neighbors(node))
            print(neighbors)
            G.add_edge(neighbors[0], neighbors[1])
            G.remove_node(node)

            disconnected = True
            break

    if not disconnected:
        break


print("Number of nodes:", len(G.nodes()))
input()

# Combine nodes less than 3 pixels apart

while True:
    disconnected = False
    for node in list(G.nodes()):
        for neighbor in list(G.neighbors(node)):
            if (
                math.sqrt((node[0] - neighbor[0]) ** 2 + (node[1] - neighbor[1]) ** 2)
                < 3
            ):
                # For all neighbors of the node, add an edge between the neighbor and the neighbor of the neighbor
                for neighbor_neighbor in list(G.neighbors(neighbor)):
                    if neighbor_neighbor != node:
                        G.add_edge(node, neighbor_neighbor)
                G.remove_node(neighbor)
                disconnected = True
                break

        if disconnected:
            break

    if not disconnected:
        break


print("Number of nodes:", len(G.nodes()))
input()

# for node in G.nodes():
#     if len(list(G.neighbors(node))) > 2:
#         parent = {node: None}
#         bfs(G, skeleton, node, parent, pos=node)
#         break

# # remove the node
# G.remove_node(node)


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
nx.draw(G, pos, ax=ax[2], node_size=20, with_labels=False, edge_color="b")


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
# import pickle

# with open("graph.pkl", "wb") as f:
#     pickle.dump(
#         {node: {neighbor: 1 for neighbor in G.neighbors(node)} for node in G.nodes()}, f
#     )

# # Convert networkx graph to search graph
# graph = UndirectedGraph(
#     {node: {neighbor: 1 for neighbor in G.neighbors(node)} for node in G.nodes()}
# )
