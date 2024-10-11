import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from environment import Environment


class Scheduler:
    @staticmethod
    def run(
        N=200,
        M=200,
        pp=0.07,
        sigma=0.65,
        const=0.85,
        steps=500,
        intervals=8,
        plot=True,
        animate=True,
    ):
        """
        generates the environment (NxM) with pp% of environment populated
        particles: Sensor Offset, Sensor Angle, Rotation Angle
        chemoattractant: constant multiplier, sigma (gaussian filter)
        evolve simulation for 500 steps, grab plots at specific intervals
        choice to plot intervals OR animate the desired simulation
        """
        environment = Environment(N, M, pp)
        environment.populate()

        if plot == True:
            dt = int(steps / intervals)
            samples = np.linspace(0, dt * intervals, intervals + 1)  # integer samples
            for i in range(steps):
                environment.diffusion_operator(const, sigma)
                environment.motor_stage()
                environment.sensory_stage()
                if i in samples:
                    fig = plt.figure(figsize=(8, 8), dpi=200)
                    ax1 = fig.add_subplot(111)
                    ax1.imshow(environment.trail_map)
                    ax1.set_title("Chemoattractant Map, step={}".format(i))
                    plt.savefig("sim_t{}.png".format(i))
                    plt.clf()

        if animate == True:
            # this can take a while for large environments, high population
            # also generates very large .gif files, play with values to get smaller files
            ims = []
            fig = plt.figure(figsize=(8, 8), dpi=100)
            ax = fig.add_subplot(111)
            for i in range(steps):
                environment.diffusion_operator(const, sigma)
                environment.motor_stage()
                environment.sensory_stage()
                txt = plt.text(
                    0,
                    -10,
                    "iteration: {}".format(i),
                )
                im = plt.imshow(environment.trail_map, animated=True)
                ims.append([im, txt])
            fig.suptitle("Chemoattractant Map")
            ani = animation.ArtistAnimation(
                fig, ims, interval=50, blit=True, repeat_delay=1000
            )
            ani.save("sim.gif")
