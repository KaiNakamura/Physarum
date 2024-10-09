import "file-loader?name=[name].[ext]!./src/html/index.html";
import {
  Scene,
  OrthographicCamera,
  WebGLRenderer,
  Mesh,
  PlaneBufferGeometry,
  ShaderMaterial,
  Vector2,
} from "three";
import PingpongRenderTarget from "./src/PingpongRenderTarget";
import RenderTarget from "./src/RenderTarget";
import { City, Point, cities, coordToPixel, coordToUV } from "./src/City";
import dat from "dat.gui";
import Controls from "./src/Controls";

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

// Initialize the food
let foodUVs = cities.map((city) => {
  return coordToUV(city.coordinates, w, h);
});

function isUVEqual(a, b, epsilon = 0.01) {
  const distance = Math.sqrt(
    Math.pow(a[0] - b[0], 2) + Math.pow(a[1] - b[1], 2),
  );
  return distance < epsilon;
}

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
  if (foodUVs.some((uv) => isUVEqual(uv, [u, v]))) {
    console.log("Found a food uv at", u, v);
    foodData[id++] = u;
    foodData[id++] = v;
    foodData[id++] = 1;
    foodData[id++] = 1;
  } else {
    foodData[id++] = u;
    foodData[id++] = v;
    foodData[id++] = 0;
    foodData[id++] = 0;
  }
}

// Create the shader for diffusion and decay
let diffuse_decay = new ShaderMaterial({
  uniforms: {
    points: { value: null },
    decay: { value: 0.9 },
  },
  vertexShader: require("./src/glsl/quad_vs.glsl"),
  fragmentShader: require("./src/glsl/diffuse_decay_fs.glsl"),
});
let trails = new PingpongRenderTarget(w, h, diffuse_decay);

// Create the shader for food
let update_food = new ShaderMaterial({
  uniforms: {
    data: { value: null },
  },
  vertexShader: require("./src/glsl/quad_vs.glsl"),
  fragmentShader: require("./src/glsl/food_fs.glsl"),
});
let food = new PingpongRenderTarget(size, size, update_food, foodData);

// Create the shader for moving the agents
let update_agents = new ShaderMaterial({
  uniforms: {
    data: { value: null },
    foodData: { value: null },
    sa: { value: 2 },
    ra: { value: 4 },
    so: { value: 12 },
    ss: { value: 1.1 },
  },
  vertexShader: require("./src/glsl/quad_vs.glsl"),
  fragmentShader: require("./src/glsl/update_agents_fs.glsl"),
});
let agents = new PingpongRenderTarget(size, size, update_agents, ptexdata);

// Create the shader for rendering the agents
let render_agents = new ShaderMaterial({
  vertexShader: require("./src/glsl/render_agents_vs.glsl"),
  fragmentShader: require("./src/glsl/render_agents_fs.glsl"),
});
let render = new RenderTarget(w, h, render_agents, pos, uvs);

// Create the shader for the post processing step
let postprocess = new ShaderMaterial({
  uniforms: {
    data: {
      value: null,
    },
  },
  vertexShader: require("./src/glsl/quad_vs.glsl"),
  fragmentShader: require("./src/glsl/postprocess_fs.glsl"),
});
let postprocess_mesh = new Mesh(new PlaneBufferGeometry(), postprocess);
postprocess_mesh.scale.set(w, h, 1);
scene.add(postprocess_mesh);

// Create a new controls object
let controls = new Controls(renderer, agents);
controls.count = ~~(size * size * 0.05);

// Main update loop
function update() {
  requestAnimationFrame(update);

  // Update the time
  time = (Date.now() - start) * 0.001;

  // Update the trails
  trails.material.uniforms.points.value = render.texture;
  trails.render(renderer, time);

  // Update the food
  food.material.uniforms.input_texture.value = trails.texture;
  food.material.uniforms.data.value = foodData;
  food.render(renderer, time);

  // Update the agents
  agents.material.uniforms.data.value = trails.texture;
  agents.material.uniforms.foodData.value = food.texture;
  agents.render(renderer, time);

  // Render the agents
  render.material.uniforms.input_texture.value = agents.texture;
  // render.material.uniforms.input_texture.value = food.texture;
  render.render(renderer, time);

  // Apply post processing
  postprocess_mesh.material.uniforms.data.value = trails.texture;

  // Render the scene
  renderer.setSize(w, h);
  renderer.clear();
  renderer.render(scene, camera);
}

let materials = [diffuse_decay, update_agents, render_agents];
let resolution = new Vector2(w, h);
materials.forEach((mat) => {
  mat.uniforms.resolution.value = resolution;
});

let start = Date.now();
let time = 0;

update();

// GUI Settings
let gui = new dat.GUI();
gui.add(diffuse_decay.uniforms.decay, "value", 0.01, 0.99, 0.01).name("Decay");
gui.add(update_agents.uniforms.sa, "value", 1, 90, 0.1).name("Sensor Angle");
gui.add(update_agents.uniforms.ra, "value", 1, 90, 0.1).name("Rotation Angle");
gui.add(update_agents.uniforms.so, "value", 1, 90, 0.1).name("Sensor Offset");
gui.add(update_agents.uniforms.ss, "value", 0.1, 10, 0.1).name("Step Size");
gui.add(controls, "random");
gui.add(controls, "radius", 0.001, 0.25);
gui.add(controls, "count", 1, size * size, 1);
