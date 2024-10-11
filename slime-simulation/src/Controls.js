import { Vector2 } from "three";

let pid = 0;

export default class Controls {
  constructor(renderer, agents) {
    this.renderer = renderer;
    this.agents = agents;
    this.size = new Vector2();

    this.radius = 0.025;
    this.count = 50;
  }

  addParticles(e) {
    let count = this.count;
    if (this.count == -1) {
      count = this.agents.texture.image.data.length / 4;
    }

    this.renderer.getSize(this.size);
    let w = this.size.width;
    let h = this.size.height;
    let radius = this.radius;
    let u = e.clientX / w;
    let v = 1 - e.clientY / h;
    let tex = this.agents.next.texture;
    let arr = tex.image.data;
    let max = arr.length / 4;
    let ratio = w / h,
      a,
      r,
      id;
    for (let i = pid; i < pid + count; i++) {
      id = (i % max) * 4;
      a = Math.random() * Math.PI * 2;
      r = Math.random() * radius;
      arr[id++] = u + Math.cos(a) * r;
      arr[id++] = v + Math.sin(a) * r * ratio;
      arr[id++] = Math.random();
    }
    pid += count;
    this.renderer.copyTextureToTexture(new Vector2(0, 0), tex, tex);
  }

  Randomize() {
    const centerX = 0.5;
    const centerY = 0.5;
    const maxRadius = 0.4;

    pid = 0;
    let tex = this.agents.texture;
    let arr = tex.image.data;
    let max = arr.length / 4;
    let id;
    for (let i = 0; i < max; i++) {
      id = i * 4;
      const angle = Math.random() * 2 * Math.PI; // Random angle between 0 and 2*PI
      const radius = Math.random() * maxRadius; // Random radius between 0 and maxRadius
      const posX = centerX + radius * Math.cos(angle); // Convert polar to Cartesian x
      const posY = centerY + radius * Math.sin(angle); // Convert polar to Cartesian y
      arr[id++] = posX;
      arr[id++] = posY;
      arr[id++] = Math.random();
    }
    this.renderer.copyTextureToTexture(new Vector2(0, 0), tex, tex);
    this.renderer.copyTextureToTexture(
      new Vector2(0, 0),
      tex,
      this.agents.next.texture,
    );
  }
}
