#version 460

#define dt 0.0166

layout (local_size_x = 16, local_size_y = 16) in;

layout(rgba8, location=0) restrict readonly uniform image2D fromTex;
layout(rgba8, location=1) uniform image2D destTex;

vec4 fetchValue(ivec2 co) {
    return imageLoad(fromTex, co);
}

float blured(ivec2 co) {
    float sum = fetchValue(co + ivec2(-1, -1)).g +
                fetchValue(co + ivec2(-1,  0)).g +
                fetchValue(co + ivec2(-1,  1)).g +
                fetchValue(co + ivec2( 0, -1)).g +
                fetchValue(co + ivec2( 0,  0)).g +
                fetchValue(co + ivec2( 1, -1)).g +
                fetchValue(co + ivec2( 1,  0)).g +
                fetchValue(co + ivec2( 1,  1)).g +
                fetchValue(co + ivec2( 0,  1)).g +
                fetchValue(co + ivec2(-1,  1)).g +
                fetchValue(co + ivec2(-1,  0)).g;
    
    return sum / 9.0;
}

uniform float diffuseSpeed;
uniform float evaporateSpeed;

void main() {
    ivec2 texelPos = ivec2(gl_GlobalInvocationID.xy);
    vec4 original_value = imageLoad(fromTex, texelPos);
    float v = blured(texelPos);
    
    float diffused = mix(original_value.g, v, diffuseSpeed * dt);
    float evaporated = max(0.0, diffused - evaporateSpeed * dt);

    vec4 result = original_value;
    result.g = evaporated;

    imageStore(destTex, texelPos, result);
}
