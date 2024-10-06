import math
import pathlib
import moderngl_window as mglw
from moderngl_window.capture.ffmpeg import FFmpegCapture
from moderngl_window.geometry import quad_fs
import moderngl as mgl
import numpy as np
import imgui
from moderngl_window.integrations.imgui import ModernglWindowRenderer
from city import cities


def coord_to_pixel(coord, size):
    lat_min, lat_max = 41.00, 43.00
    lon_min, lon_max = -73.50, -69.90

    x = np.interp(coord.latitude, [lat_min, lat_max], [0, size[0]])
    y = np.interp(coord.longitude, [lon_min, lon_max], [0, size[1]])

    return x, y


def generate_food_data(size):
    food_data = np.zeros((len(cities), 4), dtype="f4")

    for i, city in enumerate(cities):
        x, y = coord_to_pixel(city.coordinates, size)
        # Map the latitude and longitude to the image coordinates
        food_data[i, 0] = x
        food_data[i, 1] = y
        # food_data[i, 2] = np.sqrt(city.population / np.pi) / 10.0
        food_data[i, 2] = 10
        food_data[i, 3] = 0

    return np.c_[food_data[:, 0], food_data[:, 1], food_data[:, 2], food_data[:, 3]]


def generate_slime_data(N, food_data, size):
    # Randomly select a food to start at for each slime particle
    city_indices = np.random.choice(len(food_data), N)
    x = food_data[city_indices, 0]
    y = food_data[city_indices, 1]

    # Generate random angles for the slime particles
    angles = np.random.uniform(0, 2 * np.pi, N)

    return np.c_[x, y, angles, np.empty(N)]

    # # Generate random x and y coordinates within the bounds of the size
    # x = np.random.uniform(0, size[0], N)
    # y = np.random.uniform(0, size[1], N)

    # # Generate random angles for the slime particles
    # angles = np.random.uniform(0, 2 * np.pi, N)

    # return np.c_[x, y, angles, np.empty(N)]


class SlimeConfig:
    num_slimes = 1000000

    move_speed = 50.0
    angular_speed = 50.0

    sensor_distance = 10.0
    sensor_angle = 0.83

    evaporation_speed = 5.0
    diffusion_speed = 10.0


class SlimeWindow(mglw.WindowConfig):
    title = "Physarum Simulation"
    gl_version = (4, 6)
    window_size = (1280, 720)
    resource_dir = (pathlib.Path(__file__).parent / "shaders").resolve()
    map_size = (2560, 1440)
    aspect_ratio = None
    local_size = 1024
    vsync = False
    samples = 16

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        imgui.create_context()

        self.imgui = ModernglWindowRenderer(self.wnd)

        self.current_texture = None
        self.next_texture = None
        self.food = None
        self.slimes = None

        self.create_textures()
        self.generate_data()
        self.load_programs()
        self.update_uniforms()

        self.quad_fs = quad_fs(normals=False)

        self.videocapture = mglw.capture.FFmpegCapture(source=self.wnd.fbo)

    def restart_sim(self):
        self.create_textures()
        self.generate_data()

    def create_textures(self):
        if not self.current_texture is None:
            self.current_texture.release()

        if not self.next_texture is None:
            self.next_texture.release()

        self.current_texture = self.ctx.texture(self.map_size, 4)
        self.current_texture.repeat_x, self.current_texture.repeat_y = False, False
        self.current_texture.filter = mgl.NEAREST, mgl.NEAREST

        self.next_texture = self.ctx.texture(self.map_size, 4)
        self.next_texture.repeat_x, self.next_texture.repeat_y = False, False
        self.next_texture.filter = mgl.NEAREST, mgl.NEAREST

    def generate_data(self):
        food_data = generate_food_data(self.map_size).astype("f4")
        if self.food is None:
            self.food = self.ctx.buffer(food_data)
        else:
            self.food.orphan(len(cities) * 4 * 4)
            self.food.write(food_data)

        slime_data = generate_slime_data(
            SlimeConfig.num_slimes, food_data, self.map_size
        ).astype("f4")
        if self.slimes is None:
            self.slimes = self.ctx.buffer(slime_data)
        else:
            self.slimes.orphan(SlimeConfig.num_slimes * 4 * 4)
            self.slimes.write(slime_data)

    def update_uniforms(self):
        self.blur_shader["diffuseSpeed"] = SlimeConfig.diffusion_speed
        self.blur_shader["evaporateSpeed"] = SlimeConfig.evaporation_speed

        self.food_shader["numFood"] = len(cities)

        self.slime_shader["numSlimes"] = SlimeConfig.num_slimes

        self.slime_shader["moveSpeed"] = SlimeConfig.move_speed
        self.slime_shader["angularSpeed"] = SlimeConfig.angular_speed

        self.slime_shader["sensorDistance"] = SlimeConfig.sensor_distance
        self.slime_shader["sensorAngle"] = SlimeConfig.sensor_angle

    def load_programs(self):
        self.render_program = self.load_program("render_texture.glsl")
        self.render_program["texture0"] = 0
        self.food_shader = self.load_compute_shader(
            "food.glsl",
            {
                "width": self.map_size[0],
                "height": self.map_size[1],
                "local_size": self.local_size,
            },
        )
        self.slime_shader = self.load_compute_shader(
            "slime.glsl",
            {
                "width": self.map_size[0],
                "height": self.map_size[1],
                "local_size": self.local_size,
            },
        )
        self.blur_shader = self.load_compute_shader("blur.glsl")

    def render(self, time: float, frame_time: float):
        # Run the food shader
        self.current_texture.bind_to_image(0, read=True, write=False)
        self.next_texture.bind_to_image(1, read=False, write=True)
        self.food.bind_to_storage_buffer(2)
        group_size = int(math.ceil(len(cities) / self.local_size))
        self.food_shader.run(group_size, 1, 1)

        # Run the slime shader
        self.current_texture.bind_to_image(0, read=True, write=False)
        self.next_texture.bind_to_image(1, read=False, write=True)
        self.slimes.bind_to_storage_buffer(2)
        group_size = int(math.ceil(SlimeConfig.num_slimes / self.local_size))
        self.slime_shader.run(group_size, 1, 1)

        # Run the blur shader
        self.current_texture.bind_to_image(0, read=True, write=False)
        self.next_texture.bind_to_image(1, read=True, write=True)
        self.blur_shader.run(self.map_size[0] // 16 + 1, self.map_size[1] // 16 + 1)

        # Renders the world texture to the screen
        self.next_texture.use(0)
        self.quad_fs.render(self.render_program)

        self.current_texture, self.next_texture = (
            self.next_texture,
            self.current_texture,
        )

        self.videocapture.save()

        self.render_ui()

    def render_ui(self):
        imgui.new_frame()
        if imgui.begin("Settings"):
            imgui.push_item_width(imgui.get_window_width() * 0.33)
            changed = False
            c, SlimeConfig.move_speed = imgui.slider_float(
                "Movement speed", SlimeConfig.move_speed, 0.1, 100
            )
            changed = changed or c
            c, SlimeConfig.angular_speed = imgui.slider_float(
                "Angular speed",
                SlimeConfig.angular_speed,
                0.1,
                100,
            )
            c, SlimeConfig.sensor_distance = imgui.slider_int(
                "Sensor distance",
                SlimeConfig.sensor_distance,
                1,
                100,
            )
            changed = changed or c
            c, SlimeConfig.sensor_angle = imgui.slider_float(
                "Sensor angle",
                SlimeConfig.sensor_angle,
                0,
                np.pi,
            )
            changed = changed or c
            changed = changed or c
            c, SlimeConfig.evaporation_speed = imgui.slider_float(
                "Evaporation speed", SlimeConfig.evaporation_speed, 0.01, 5
            )
            changed = changed or c
            c, SlimeConfig.diffusion_speed = imgui.slider_float(
                "Diffusion speed",
                SlimeConfig.diffusion_speed,
                0.1,
                100,
            )
            changed = changed or c
            if changed:
                self.update_uniforms()
            imgui.pop_item_width()

        imgui.end()

        if imgui.begin("Actions"):
            imgui.push_item_width(imgui.get_window_width() * 0.33)
            changed, SlimeConfig.num_slimes = imgui.input_int(
                "Number of Slimes", SlimeConfig.num_slimes, step=1024, step_fast=2**15
            )
            SlimeConfig.num_slimes = min(max(2048, SlimeConfig.num_slimes), 2**24)

            if imgui.button("Restart Simulation"):
                self.restart_sim()

            imgui.pop_item_width()

        imgui.end()
        imgui.render()
        self.imgui.render(imgui.get_draw_data())

    def resize(self, width: int, height: int):
        self.imgui.resize(width, height)

    def key_event(self, key, action, modifiers):
        keys = self.wnd.keys
        if action == keys.ACTION_PRESS and key == keys.R:
            self.videocapture.start_capture(filename="video.mp4", framerate=30)
        if action == keys.ACTION_PRESS and key == keys.F:
            self.videocapture.release()
        self.imgui.key_event(key, action, modifiers)

    def mouse_position_event(self, x, y, dx, dy):
        self.imgui.mouse_position_event(x, y, dx, dy)

    def mouse_drag_event(self, x, y, dx, dy):
        self.imgui.mouse_drag_event(x, y, dx, dy)

    def mouse_scroll_event(self, x_offset, y_offset):
        self.imgui.mouse_scroll_event(x_offset, y_offset)

    def mouse_press_event(self, x, y, button):
        self.imgui.mouse_press_event(x, y, button)

    def mouse_release_event(self, x: int, y: int, button: int):
        self.imgui.mouse_release_event(x, y, button)

    def unicode_char_entered(self, char):
        self.imgui.unicode_char_entered(char)


SlimeWindow.run()
