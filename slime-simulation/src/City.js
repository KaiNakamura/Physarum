class Point {
  constructor(latitude, longitude) {
    this.latitude = latitude;
    this.longitude = longitude;
  }

  toString() {
    return `${this.latitude}, ${this.longitude}`;
  }
}

class City {
  constructor(name, population, coordinates) {
    this.name = name;
    this.population = population;
    this.coordinates = coordinates;
    this.size = 0; // Initialize size to zero
  }

  toString() {
    return `${this.name} (Population: ${this.population}, Coordinates: ${this.coordinates.toString()}, Size: ${this.size.toFixed(2)})`;
  }

  getIntegerCoordinates() {
    return {
      latitude: parseInt(this.coordinates.latitude),
      longitude: parseInt(this.coordinates.longitude),
    };
  }

  static fromJSON(json) {
    const coordinates = new Point(
      json.coordinates.latitude,
      json.coordinates.longitude,
    );
    return new City(json.name, json.population, coordinates);
  }
}

function loadCitiesFromFile() {
  const citiesJSON = require("../cities.json");
  return citiesJSON.map((cityJSON) => City.fromJSON(cityJSON));
}

const cities = loadCitiesFromFile();

function interp(value, fromMin, fromMax, toMin, toMax) {
  return toMin + ((value - fromMin) * (toMax - toMin)) / (fromMax - fromMin);
}

const latMin = 41.0,
  latMax = 43.0;
const lonMin = -73.5,
  lonMax = -69.9;

function coordToPixel(coord, width, height) {
  const x = Math.floor(interp(coord.latitude, latMin, latMax, 0, width));
  const y = Math.floor(interp(coord.longitude, lonMin, lonMax, 0, height));

  return [x, y];
}

function coordToUV(coord) {
  const u = interp(coord.latitude, latMin, latMax, 0, 1);
  const v = interp(coord.longitude, lonMin, lonMax, 0, 1);

  return [u, v];
}

module.exports = { City, Point, cities, coordToPixel, coordToUV };
