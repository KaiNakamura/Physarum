import numpy as np


class Particle:
    def __init__(self, position):
        self.position = position
        self.orientation = 2 * np.pi * np.random.random()
        self.sensor_distance = 9.0
        self.sensor_angle = np.pi / 8
        self.angular_speed = np.pi / 4

    def deposit_phermone_trail(self, arr, strength=1.0):
        """
        Applies a single trail of chemoattractant at current position
        """
        n, m = self.position
        arr[n, m] = strength

    def get_sensor_location(self, angle_offset: float) -> tuple[float, float]:
        """
        Returns the location of the sensor relative to the particle's position
        """
        angle = self.orientation + angle_offset
        x = round(self.sensor_distance * np.cos(angle))
        y = round(self.sensor_distance * np.sin(angle))
        return (x, y)

    def get_sensor_values(self, arr):
        """
        Finds the value of the chemoattractant at each of the 3 sensors
        Pass the TrailMap array as an argument
        """
        n, m = self.position
        row, col = arr.shape

        xL, yL = self.get_sensor_location(-self.sensor_angle)
        xC, yC = self.get_sensor_location(0)
        xR, yR = self.get_sensor_location(self.sensor_angle)

        # Implement periodic BCs
        valL = arr[(n - xL) % row, (m + yL) % col]
        valC = arr[(n - xC) % row, (m + yC) % col]
        valR = arr[(n - xR) % row, (m + yR) % col]

        return (valL, valC, valR)

    def sense(self, arr):
        """
        The particle reads from the trail map, rotates based on chemoattractant
        arr = trail map array
        """
        L, C, R = self.get_sensor_values(arr)

        # If center is not greater than both
        if C <= L and C <= R:
            # If left and right equal, turn randomly
            if L == R:
                self.orientation += (
                    self.angular_speed
                    if np.random.rand() > 0.5
                    else -self.angular_speed
                )
            # Otherwise, turn towards the higher value
            elif R > L:
                self.orientation += self.angular_speed
            elif L > R:
                self.orientation -= self.angular_speed
