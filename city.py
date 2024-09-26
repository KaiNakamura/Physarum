from geopy.point import Point
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.widgets import CheckButtons, Slider

matplotlib.use("TkAgg")


class City:
    def __init__(self, name: str, population: int, coordinates: Point):
        self.name = name
        self.population = population
        self.coordinates = coordinates
        self.size = 0  # Initialize size to zero

    def __str__(self):
        return f"{self.name} (Population: {self.population}, Coordinates: {self.coordinates} Size: {self.size:.2f})"

    def get_integer_coordinates(self):
        return (int(self.coordinates.latitude), int(self.coordinates.longitude))


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

selected_cities = cities[:]


# Function to update city sizes based on the selected cities and their populations
def update_city_sizes():
    # for all selected cities calculate the total population normalize the their population to get their size
    city_populations = [city.population for city in selected_cities]
    total_population = sum(city_populations) if city_populations else 1
    city_sizes = [
        (city.population / total_population) * 100 for city in selected_cities
    ]  # Normalize out of 100
    return city_sizes


# Makes cities have correctly normalized sizes
print("All Cities Selected: ")
for city in selected_cities:
    total_population = sum(city.population for city in selected_cities)
    city.size = (city.population / total_population) * 100
    print(f"{city.name}: Population = {city.population}, Size = {city.size:.2f}")


# Function to plot cities on the map image
def plot_cities_on_map(cities, map_image_path):

    # Load the map image of Massachusetts
    img = plt.imread(map_image_path)

    # Latitude and longitude Bounds of the map
    lat_min, lat_max = 41.00, 43.00
    lon_min, lon_max = -73.50, -69.90

    fig, ax = plt.subplots(figsize=(10, 8))

    # Massachusetts map on plot as background
    ax.imshow(img, extent=[lon_min, lon_max, lat_min, lat_max])

    city_scatter_plots = {}
    city_labels = []

    # Plot each city on the map with the initial size (considering all cities in cities list)
    for city in selected_cities:
        lat, lon = city.coordinates.latitude, city.coordinates.longitude
        scatter_plot = ax.scatter(lon, lat, color="red", s=city.size, label=city.name)
        text_plot = ax.text(
            lon, lat, f"{city.name}\nSize: {city.size:.2f}", color="black", fontsize=7
        )
        city_scatter_plots[city.name] = (scatter_plot, text_plot)
        city_labels.append(city.name)

    # Update plot sizes
    def update_plot():
        city_sizes = (
            update_city_sizes()
        )  # Calculate new city sizes based on selected cities lists
        print("\nSelected cities: ")

        # update new sizes for selected cities
        for city, size in zip(selected_cities, city_sizes):
            scatter_plot, text_plot = city_scatter_plots[city.name]
            city.size = size
            scatter_plot.set_sizes([size])

            lat, lon = city.coordinates.latitude, city.coordinates.longitude
            text_plot.set_position((lon, lat))
            text_plot.set_text(f"{city.name}\nSize: {city.size:.2f}")

            print(
                f"{city.name}: Population = {city.population}, size = {city.size:.2f}"
            )

        plt.draw()  # Redraw the plot

    # Create checkboxes to select cities
    rax = plt.axes([0.01, 0.4, 0.15, 0.2], frameon=False)

    check = CheckButtons(
        rax, city_labels, [True] * len(city_labels)
    )  # All cities selected on initialization

    # Selection toggle
    def toggle_visibility(label):
        scatter, text = city_scatter_plots[label]
        visible = not scatter.get_visible()
        scatter.set_visible(visible)
        text.set_visible(visible)

        # Update the selected cities list
        if visible:
            selected_cities.append(next(city for city in cities if city.name == label))
        else:
            selected_cities[:] = [
                city for city in selected_cities if city.name != label
            ]

        update_plot()  # Recalculate sizes and update the plot

    check.on_clicked(
        toggle_visibility
    )  # Call toggle_visibility when checkbox is clicked

    # Slider code
    ax_slider_iterations = plt.axes(
        [0.25, 0.02, 0.65, 0.02], facecolor="lightgoldenrodyellow"
    )  # Create new axis with the iterations sliders
    ax_slider_flow = plt.axes(
        [0.25, 0.05, 0.65, 0.02], facecolor="lightgoldenrodyellow"
    )  # Create new axis for the flow rate slider
    ax_slider_diffusion = plt.axes(
        [0.25, 0.08, 0.65, 0.02], facecolor="lightgoldenrodyellow"
    )  # Create new axis for the diffusion slider

    slider_iterations = Slider(
        ax_slider_iterations, "Iterations", 1, 1000, valinit=100, valstep=1
    )  # Create slider for iterations
    slider_flow = Slider(
        ax_slider_flow, "Flow Rate", 1, 1000, valinit=100, valstep=1
    )  # Create slider for flow rate
    slider_diffusion = Slider(
        ax_slider_diffusion, "Trail Diffusion", 1, 1000, valinit=100, valstep=1
    )  # create slider for diffusion

    # Function for slider changes
    def edit_sliders(val):
        iterations = slider_iterations.val  # store value in the iterations
        flow_rate = slider_flow.val  # store values in the flow rate
        diffusion_time = slider_diffusion.val  # store values in the diffusion
        print(
            f"Slider Values: Iterations- {iterations} Flow Rate- {flow_rate} Trail Diffusion- {diffusion_time}"
        )

    slider_iterations.on_changed(
        edit_sliders
    )  # run the slider function on iteration change
    slider_flow.on_changed(edit_sliders)  # run the slider function on flow rate change
    slider_diffusion.on_changed(
        edit_sliders
    )  # run the slider function on diffusion change

    plt.show()


if __name__ == "__main__":
    # Path to the map image
    map_image_path = "mass.jpg"

    # Print cities
    for city in cities:
        print(f"{city.name}: Population = {city.population}, Size = {city.size:.2f}")

    # Plot the cities on the map
    plot_cities_on_map(cities, map_image_path)
