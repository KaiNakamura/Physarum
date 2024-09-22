from city import City
from obstacle import Obstacle


class Map:
    def __init__(self, cities: list[City], obstacles: list[Obstacle] = []):
        self.cities = cities
        self.obstacles = obstacles
