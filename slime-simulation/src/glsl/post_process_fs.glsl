uniform sampler2D data;
uniform sampler2D foodData;
varying vec2 vUv;

float getFoodValue(vec2 uv) {
  return texture2D(foodData, fract(uv)).b;
}

void main() {
  vec4 src = texture2D(data, vUv);
  float foodValue = getFoodValue(vUv);
  gl_FragColor = vec4(foodValue, src.g, 0., 1.);
}