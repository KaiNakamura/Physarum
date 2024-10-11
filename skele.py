import math
import pickle
from skimage.morphology import skeletonize
import skimage as ski
import matplotlib.pyplot as plt
import networkx as nx
from pathlib import Path


class PictureToNetwork:
    def __init__(self, image_path):
        self.filename = Path(image_path).stem
        self.image_path = image_path
        self.image = ski.io.imread(image_path, as_gray=True)
        self.image = self.image > 0.5
        self.skeleton = skeletonize(self.image)
        self.G = nx.Graph()
        self.visited = set()

    def _construct_graph(self):
        for i in range(self.skeleton.shape[0]):
            for j in range(self.skeleton.shape[1]):
                if self.skeleton[i, j]:
                    node = (j, i)
                    self.G.add_node(node, pos=node)
                    self.visited.add(node)

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

                        if new_node in self.visited:
                            self.G.add_edge(node, new_node)

    def _remove_nodes(self):
        while True:
            disconnected = False

            for node in list(self.G.nodes()):
                if self.G.degree(node) == 0:
                    self.G.remove_node(node)
                elif self.G.degree(node) == 2:
                    neighbors = list(self.G.neighbors(node))
                    self.G.add_edge(neighbors[0], neighbors[1])
                    self.G.remove_node(node)

                    disconnected = True
                    break

            if not disconnected:
                break

    def _combine_nodes(self):
        while True:
            disconnected = False
            for node in list(self.G.nodes()):
                for neighbor in list(self.G.neighbors(node)):
                    if (
                        math.sqrt(
                            (node[0] - neighbor[0]) ** 2 + (node[1] - neighbor[1]) ** 2
                        )
                        < 2
                    ):
                        for neighbor_neighbor in list(self.G.neighbors(neighbor)):
                            if neighbor_neighbor != node:
                                self.G.add_edge(node, neighbor_neighbor)
                        self.G.remove_node(neighbor)
                        disconnected = True
                        break

                if disconnected:
                    break

            if not disconnected:
                break

    def run(self):
        self._construct_graph()
        self._remove_nodes()
        self._combine_nodes()

    def _prepare_plt(self):
        fig, axes = plt.subplots(
            nrows=1, ncols=3, figsize=(8, 4), sharex=True, sharey=True
        )

        ax = axes.ravel()

        ax[0].imshow(self.image, cmap=plt.cm.gray)
        ax[0].axis("off")
        ax[0].set_title("original", fontsize=20)

        ax[1].imshow(self.skeleton, cmap=plt.cm.gray)
        ax[1].axis("off")
        ax[1].set_title("skeleton", fontsize=20)

        pos = nx.get_node_attributes(self.G, "pos")
        nx.draw(self.G, pos, ax=ax[2], node_size=20, with_labels=False, edge_color="b")

        fig.tight_layout()

    def display_results(self):
        self._prepare_plt()
        plt.show()

    def dump_graph(self, path_dir="", dump_pickle=True, dump_png=True):
        directory = Path(path_dir)

        if dump_pickle:
            with open(directory / f"{self.filename}.pkl", "wb") as f:
                # convert network to dict
                pickle.dump(
                    {
                        node: {neighbor: 1 for neighbor in self.G.neighbors(node)}
                        for node in self.G.nodes()
                    },
                    f,
                )

        if dump_png:
            self._prepare_plt()
            plt.savefig(directory / f"{self.filename}.png")
            plt.close()
