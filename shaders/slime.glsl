#version 460

#define width 0
#define height 0
#define local_size 1

#define PI 3.141592653
#define dt 0.0166

layout (local_size_x = local_size, local_size_y = 1, local_size_z = 1) in;

layout(rgba8, location=0) restrict readonly uniform image2D fromTex;
layout(rgba8, location=1) restrict writeonly uniform image2D destTex;

struct Slime {
    float x, y, orientation, padding;
};

layout(std430, binding=2) restrict buffer inslimes {
    Slime slimes[];
} SlimeBuffer;

uniform int numSlimes;

uniform float moveSpeed;
uniform float angularSpeed;
uniform float sensorDistance;
uniform float sensorAngle;

float rand(vec2 co) {
    return fract(sin(dot(co.xy, vec2(12.9898, 78.233))) * 43758.5453);
}

void drawSlime(Slime slime) {
    imageStore(destTex, ivec2(slime.x, slime.y), vec4(0, 1, 0, 1));
}

// Returns the location of the sensor relative to the slime's position
ivec2 getSensorLocation(Slime slime, float sensorAngleOffset) {
    float angle = slime.orientation + sensorAngleOffset;
    vec2 direction = vec2(cos(angle), sin(angle));
    return ivec2(slime.x, slime.y) + ivec2(direction * sensorDistance);
}

// Gets the value of the image at the given position
vec4 getImageValue(ivec2 pos) {
    if (pos.x >= 0 && pos.x < width && pos.y >= 0 && pos.y < height) {
        return imageLoad(fromTex, pos);
    }
    return vec4(0.0);
}

// Gets the sensor value of a slime at a given angle offset
float getSensorValue(Slime slime, float sensorAngleOffset) {
    ivec2 sensorLocation = getSensorLocation(slime, sensorAngleOffset);
    // TODO: Make values for this
    vec4 imageValue = getImageValue(sensorLocation);
    return 10 * imageValue.r + imageValue.g;
}

// For the given slime, sense the environment and turn
Slime sense(Slime slime) {
    float left = getSensorValue(slime, -sensorAngle);
    float center = getSensorValue(slime, 0);
    float right = getSensorValue(slime, sensorAngle);
    
    float randomSteerStrength = rand(vec2(slime.x, slime.y) * dt * slime.orientation);

    // If the center is stronger than both, go straight
    if (center > left && center > right) { }
    // If the center is weaker than both, turn randomly
    else if (center < left && center < right) {
        slime.orientation += (randomSteerStrength - 0.5) * 2 * angularSpeed * dt;
    }
    // Otherwise, turn towards the higher value
    else if (right > left) {
        slime.orientation += randomSteerStrength * angularSpeed * dt;
    }
    else if (left > right) {
        slime.orientation -= randomSteerStrength * angularSpeed * dt;
    }

    return slime;
}

// Moves the given slime
Slime move(Slime slime) {
    vec2 direction = vec2(cos(slime.orientation), sin(slime.orientation));
    vec2 newPos = vec2(slime.x, slime.y) + (direction * moveSpeed * dt);

    if (newPos.x < 0. || newPos.x >= width || newPos.y < 0. || newPos.y >= height) {
        newPos.x = min(width - 0.01, max(0., newPos.x));
        newPos.y = min(height - 0.01, max(0., newPos.y));
        slime.orientation = rand(newPos) * 2 * PI;
    }
    slime.x = newPos.x;
    slime.y = newPos.y;

    return slime;
}

void main() {
    int index = int(gl_GlobalInvocationID);

    // Bounds check for slime buffer
    if (index >= numSlimes) {
        return;
    }

    // Access the slime from the slime buffer
    Slime slime = SlimeBuffer.slimes[index];

    // Sense, move, and draw
    slime = sense(slime);
    slime = move(slime);
    drawSlime(slime);

    // Update the slime buffer with the new state
    SlimeBuffer.slimes[index] = Slime(slime.x, slime.y, slime.orientation, 0.);
}