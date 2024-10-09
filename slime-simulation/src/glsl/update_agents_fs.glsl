uniform sampler2D input_texture;
uniform sampler2D data;
uniform sampler2D foodData;

uniform vec2 resolution;
uniform float time;
uniform float sa;
uniform float ra;
uniform float so;
uniform float ss;

const float PI  = 3.14159265358979323846264;
const float PI2 = PI * 2.;
const float RAD = 1. / PI;
const float PHI = 1.61803398874989484820459 * .1;
const float SQ2 = 1.41421356237309504880169 * 1000.;

float rand(in vec2 coordinate){
  return fract(tan(distance(coordinate * (time + PHI), vec2(PHI, PI * .1))) * SQ2);
}

float getDataValue(vec2 uv) {
  return texture2D(data, fract(uv)).r;
}

float getTrailValue(vec2 uv) {
  return texture2D(data, fract(uv)).g;
}

float getFoodValue(vec2 uv) {
  return texture2D(foodData, fract(uv)).b;
}

float getSensorValue(vec2 uv) {
  return getTrailValue(uv) + 2. * getFoodValue(uv);
}

varying vec2 vUv;

void main() {
  // Converts degree to radians
  float SA = sa * RAD;
  float RA = ra * RAD;

  // Downscales the parameters
  vec2 res = 1. / resolution; // Data trail scale
  vec2 SO = so * res;
  vec2 SS = ss * res;

  // Where to sample in the data trail texture to get the agent's world position
  vec4 src = texture2D(input_texture, vUv);
  vec4 val = src;

  // Agent's heading 
  float angle = val.z * PI2;

  // Compute the sensors positions 
  vec2 uvLeft = val.xy + vec2(cos(angle - SA), sin(angle - SA)) * SO;
  vec2 uvCenter = val.xy + vec2(cos(angle), sin(angle)) * SO;
  vec2 uvRight = val.xy + vec2(cos(angle + SA), sin(angle + SA)) * SO;

  // Get the values unders the sensors 
  float left = getSensorValue(uvLeft);
  float center  = getSensorValue(uvCenter);
  float right = getSensorValue(uvRight);

  // If the center is stronger than both, go straight
  if (center > left && center > right ) { }
  // If the center is weaker than both, turn randomly
  else if (center < left && center < right) {
    if (rand(val.xy) > .5) {
      angle += RA;
    } else{
      angle -= RA;
    }
  }
  // Otherwise, turn towards the higher value
  else if (left < right) {
    angle += RA;
  }
  else if (left > right){
    angle -= RA;
  }

  // Move forward
  vec2 offset = vec2(cos(angle), sin(angle)) * SS;
  val.xy += offset;

  // Move only if the destination is free
  // if (getDataValue(val.xy) == 1.) {
  //   val.xy = src.xy;
  //   angle = rand(val.xy + time) * PI2;
  // }

  // Wraps the coordinates so they remains in the [0-1] interval
  // val.xy = fract(val.xy);

  // Converts the angle back to [0-1]
  val.z = (angle / PI2);
  
  gl_FragColor = val;
}