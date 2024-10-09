uniform sampler2D input_texture;
uniform sampler2D data;

varying vec2 vUv;

void main() {
  // Where to sample in the data trail texture to get the agent's world position
  vec4 src = texture2D(input_texture, vUv);
  vec4 val = src;
  
  gl_FragColor = val;
}