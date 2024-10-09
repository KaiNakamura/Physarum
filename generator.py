import numpy as np
from matplotlib import pyplot as plt
import networkx as nx


def main():
    data = np.load("final_positions.npy")

    # Find min and max x, y values
    min_x = np.min(data[:, 0])
    max_x = np.max(data[:, 0])
    min_y = np.min(data[:, 1])
    max_y = np.max(data[:, 1])

    # Calculate density of each grid
    GRID_SIZE = 5

    x_grid = np.arange(min_x, max_x, GRID_SIZE)
    y_grid = np.arange(min_y, max_y, GRID_SIZE)
    density = np.zeros((len(x_grid), len(y_grid)))

    # for i in range(0, len(x_grid), GRID_SIZE):
    #     for j in range(0, len(y_grid), GRID_SIZE):
    #         x = x_grid[i]
    #         y = y_grid[j]
    #         density[i, j] = np.sum(
    #             (data[:, 0] >= x)
    #             & (data[:, 0] < x + GRID_SIZE)
    #             & (data[:, 1] >= y)
    #             & (data[:, 1] < y + GRID_SIZE)
    #         )

    #         print(i, j, density[i, j])

    # Create the edges for the bins based on the x_grid and y_grid
    x_edges = np.arange(x_grid[0], x_grid[-1] + GRID_SIZE, GRID_SIZE)
    y_edges = np.arange(y_grid[0], y_grid[-1] + GRID_SIZE, GRID_SIZE)

    # Use np.histogram2d to bin the data into a 2D grid
    density, _, _ = np.histogram2d(data[:, 0], data[:, 1], bins=[x_edges, y_edges])

    # Clamp the density to a maximum value
    density = np.minimum(density, 100)
    # threshold the density to make it binary
    density = density > 25

    # Plot the density
    plt.figure()
    plt.imshow(density.T, origin="lower", extent=[min_x, max_x, min_y, max_y])
    plt.colorbar()
    plt.title("Density of slime mold")
    plt.xlabel("x")
    plt.ylabel("y")

    plt.show()

    # # Generate a digraph of the slime mold based on density
    # x_len = len(x_grid) - 1
    # y_len = len(y_grid) - 1

    # G = nx.DiGraph()

    # for i in range(x_len):
    #     for j in range(y_len):
    #         G.add_node((i, j), pos=(x_grid[i], y_grid[j]))


if __name__ == "__main__":
    main()
