from typing import List, Tuple


class City:
    name: str
    population: int
    coordinates: Tuple[int, int]

    def __init__(self, name: str, population: str, coordinates) -> None:
        self.name = name
        self.population = population
        self.coordinates = coordinates


class Map:
    cities: List[City]
    size_x: int
    size_y: int

    def __init__(self, cities: List[City], size_x: int, size_y: int) -> None:
        self.cities = cities
        self.size_x = size_x
        self.size_y = size_y


class Particle:
    position: Tuple[int, int]  # x, y
    orientation: float
    sensor_angle: float
    sensor_distance: float


class Environment:
    particles: List[Particle]
    city_map: Map


class SimulationParameters:
    iterations: int
    diffusion_time: int


class Scheduler:
    pass


class GraphNode:
    name: str


class Graph:
    nodes: dict[str, GraphNode] = {}  # Mapping from string to node


class NetworkEvaluator:
    pass


c = City("Boston", 10000000, (0, 0))
print(c.name)

m1 = Map()
m2 = Map()
