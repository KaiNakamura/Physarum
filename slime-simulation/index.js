import dat from "dat.gui";
import "file-loader?name=[name].[ext]!./src/html/index.html";
import {
  Mesh,
  OrthographicCamera,
  PlaneBufferGeometry,
  Scene,
  ShaderMaterial,
  Vector2,
  WebGLRenderer,
} from "three";
import { cities, coordToUV } from "./src/City";
import Controls from "./src/Controls";
import PingpongRenderTarget from "./src/PingpongRenderTarget";
import RenderTarget from "./src/RenderTarget";

// Define window width and height
let minDim = Math.min(window.innerWidth, window.innerHeight);
let w = minDim;
let h = minDim;

// Create a new WebGLRenderer
const renderer = new WebGLRenderer({
  alpha: true,
});
document.body.appendChild(renderer.domElement);
renderer.setSize(w, h);

// Create a new scene and camera
const scene = new Scene();
const camera = new OrthographicCamera(-w / 2, w / 2, h / 2, -h / 2, 0.1, 100);
camera.position.z = 1;

let totalPopulation = 0;
for (let city of cities) {
  totalPopulation += city.population;
}

// Get the radius for a city
const getCityRadius = (city) => {
  let area = 0.001 + 0.005 * (city.population / totalPopulation);
  return Math.sqrt(area / Math.PI);
};

// Returns the food value for a given position
const getFoodvalue = (u, v) => {
  let foodValue = 0;

  for (const city of cities) {
    const cityUV = coordToUV(city.coordinates, w, h);
    const cityRadius = getCityRadius(city);
    const distance = Math.sqrt((u - cityUV[0]) ** 2 + (v - cityUV[1]) ** 2);

    const sigma = cityRadius / 3.0; // Standard deviation
    if (distance < cityRadius) {
      const gaussianValue = Math.exp(-(distance ** 2) / (2 * sigma ** 2));
      foodValue += gaussianValue;
    }
  }

  return Math.min(1, foodValue);
};

// Initialize the agents
let size = 512; // Particle amount = (size ^ 2)
let count = size * size;
let pos = new Float32Array(count * 3);
let uvs = new Float32Array(count * 2);
let ptexdata = new Float32Array(count * 4);
let foodData = new Float32Array(count * 4);

let id = 0,
  u,
  v;
for (let i = 0; i < count; i++) {
  // Point cloud vertex
  id = i * 3;
  pos[id++] = pos[id++] = pos[id++] = 0;

  // Computes the uvs
  u = (i % size) / size;
  v = ~~(i / size) / size;
  id = i * 2;
  uvs[id++] = u;
  uvs[id] = v;

  // Particle texture values (agents)
  id = i * 4;
  ptexdata[id++] = Math.random(); // Normalized pos x
  ptexdata[id++] = Math.random(); // Normalized pos y
  ptexdata[id++] = Math.random(); // Normalized angle
  ptexdata[id++] = 1;

  // Check if the current uv is at a food uv
  id = i * 4;
  foodData[id++] = u;
  foodData[id++] = v;
  foodData[id++] = getFoodvalue(u, v);
  foodData[id++] = 1;
}

// Create the shader for diffusion and decay
let diffuse_decay_shader = new ShaderMaterial({
  uniforms: {
    points: { value: null },
    decay: { value: 0.9 },
  },
  vertexShader: require("./src/glsl/quad_vs.glsl"),
  fragmentShader: require("./src/glsl/diffuse_decay_fs.glsl"),
});
let diffuse_decay = new PingpongRenderTarget(w, h, diffuse_decay_shader);

// Create the shader for food
let food_shader = new ShaderMaterial({
  uniforms: {
    data: { value: null },
  },
  vertexShader: require("./src/glsl/quad_vs.glsl"),
  fragmentShader: require("./src/glsl/food_fs.glsl"),
});
let food = new PingpongRenderTarget(size, size, food_shader, foodData);

// Create the shader for moving the agents
let update_agents_shader = new ShaderMaterial({
  uniforms: {
    data: { value: null },
    foodData: { value: null },
    sa: { value: 2 },
    ra: { value: 4 },
    so: { value: 12 },
    ss: { value: 1 },
  },
  vertexShader: require("./src/glsl/quad_vs.glsl"),
  fragmentShader: require("./src/glsl/update_agents_fs.glsl"),
});
let update_agents = new PingpongRenderTarget(
  size,
  size,
  update_agents_shader,
  ptexdata,
);

// Create the shader for rendering the agents
let render_agents_shader = new ShaderMaterial({
  vertexShader: require("./src/glsl/render_agents_vs.glsl"),
  fragmentShader: require("./src/glsl/render_agents_fs.glsl"),
});
let render_agents = new RenderTarget(w, h, render_agents_shader, pos, uvs);

// Create the shader for the post processing step
let post_process_shader = new ShaderMaterial({
  uniforms: {
    data: {
      value: null,
    },
    foodData: {
      value: null,
    },
  },
  vertexShader: require("./src/glsl/quad_vs.glsl"),
  fragmentShader: require("./src/glsl/post_process_fs.glsl"),
});
let post_process = new Mesh(new PlaneBufferGeometry(), post_process_shader);
post_process.scale.set(w, h, 1);
scene.add(post_process);

// Create a new controls object
let controls = new Controls(renderer, update_agents);
controls.count = ~~(size * size * 0.05);

// Main update loop
function update() {
  requestAnimationFrame(update);

  // Update the time
  time = (Date.now() - start) * 0.001;

  // Update the trails
  diffuse_decay.material.uniforms.points.value = render_agents.texture;
  diffuse_decay.render(renderer, time);

  // Update the food
  food.material.uniforms.input_texture.value = diffuse_decay.texture;
  food.material.uniforms.data.value = foodData;
  food.render(renderer, time);

  // Update the agents
  update_agents.material.uniforms.data.value = diffuse_decay.texture;
  update_agents.material.uniforms.foodData.value = food.texture;
  update_agents.render(renderer, time);

  // Render the agents
  render_agents.material.uniforms.input_texture.value = update_agents.texture;
  // render_agents.material.uniforms.input_texture.value = food.texture;
  render_agents.render(renderer, time);

  // Apply post processing
  post_process.material.uniforms.data.value = diffuse_decay.texture;
  post_process.material.uniforms.foodData.value = food.texture;

  // Render the scene
  renderer.setSize(w, h);
  renderer.clear();
  renderer.render(scene, camera);
}

let materials = [
  diffuse_decay_shader,
  update_agents_shader,
  render_agents_shader,
];
let resolution = new Vector2(w, h);
materials.forEach((mat) => {
  mat.uniforms.resolution.value = resolution;
});

let start = Date.now();
let time = 0;

update();

// GUI Settings
let gui = new dat.GUI();
gui
  .add(diffuse_decay_shader.uniforms.decay, "value", 0.01, 0.99, 0.01)
  .name("Decay");
gui
  .add(update_agents_shader.uniforms.sa, "value", 1, 45, 0.1)
  .name("Sensor Angle");
gui
  .add(update_agents_shader.uniforms.ra, "value", 1, 45, 0.1)
  .name("Rotation Angle");
gui
  .add(update_agents_shader.uniforms.so, "value", 1, 50, 0.1)
  .name("Sensor Offset");
gui
  .add(update_agents_shader.uniforms.ss, "value", 0.1, 10, 0.1)
  .name("Step Size");
gui.add(controls, "random");
