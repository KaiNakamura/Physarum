from geopy.point import Point


class City:
    def __init__(self, name: str, population: int, coordinates: Point):
        self.name = name
        self.population = population
        self.coordinates = coordinates

    def __str__(self):
        return f"{self.name} (Population: {self.population}, Coordinates: {self.coordinates})"

    def get_integer_coordinates(self):
        return (int(self.coordinates.latitude), int(self.coordinates.longitude))


cities = [
    City("Boston", 650706, Point("42.3601 N 71.0589 W")),
    City("Worcester", 205319, Point("42.2626 N 71.8023 W")),
]

if __name__ == "__main__":
    # Print all cities
    for city in cities:
        print(city)
