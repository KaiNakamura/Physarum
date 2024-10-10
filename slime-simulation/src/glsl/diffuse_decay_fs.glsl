uniform sampler2D points;
uniform sampler2D input_texture;
uniform vec2 resolution;
uniform float time;
uniform float decay;
uniform float blur;
varying vec2 vUv;

void main() {
  vec2 res = 1.0 / resolution;
  float pos = texture2D(points, vUv).r;

  // Accumulator
  float col = 0.0;

  // Blur box size
  const int maxDim = 10; // Set a maximum dimension for the blur

  float weight = 1.0 / pow(2.0 * blur + 1.0, 2.0);

  for (int i = -maxDim; i <= maxDim; i++) {
    for (int j = -maxDim; j <= maxDim; j++) {
      if (abs(float(i)) <= blur && abs(float(j)) <= blur) {
        vec3 val = texture2D(input_texture, fract(vUv + res * vec2(float(i), float(j)))).rgb;
        col += val.r * weight + val.g * weight * 0.5;
      }
    }
  }

  vec4 fin = vec4(pos * decay, col * decay, 0.5, 1.0);
  gl_FragColor = clamp(fin, 0.01, 1.0);
}