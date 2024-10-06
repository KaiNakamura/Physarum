#version 460

#define width 0
#define height 0
#define local_size 1

layout (local_size_x = local_size, local_size_y = 1, local_size_z = 1) in;

layout(rgba8, location=0) restrict readonly uniform image2D fromTex;
layout(rgba8, location=1) restrict writeonly uniform image2D destTex;

struct Food {
    float x, y, amount, padding;
};

layout(std430, binding=2) restrict buffer infood {
    Food food[];
} FoodBuffer;

uniform int numFood;

// void drawFood(Food food) {
//     float sigma = food.amount; // Use the food amount as the standard deviation
//     int radius = int(3.0 * sigma);
//     ivec2 center = ivec2(food.x, food.y);

//     for (int y = -radius; y <= radius; y++) {
//         for (int x = -radius; x <= radius; x++) {
//             ivec2 pos = center + ivec2(x, y);
//             float dist2 = float(x * x + y * y);
//             float intensity = exp(-dist2 / (2.0 * sigma * sigma));
//             if (intensity > 0.01) { // Only draw if the intensity is significant
//                 imageStore(destTex, pos, vec4(intensity, 0.0, 0.0, 1.0)); // Red color for food with Gaussian intensity
//             }
//         }
//     }
// }

void drawFood(Food food) {
    int radius = int(food.amount);
    ivec2 center = ivec2(food.x, food.y);

    for (int y = -radius; y <= radius; y++) {
        for (int x = -radius; x <= radius; x++) {
            ivec2 pos = center + ivec2(x, y);
            float dist2 = float(x * x + y * y);
            if (dist2 <= float(radius * radius)) { // Only draw within the radius
                imageStore(destTex, pos, vec4(1.0, 0.0, 0.0, 1.0)); // Solid red color for food
            }
        }
    }
}

void main() {
    int index = int(gl_GlobalInvocationID);

    // Bounds check for food buffer
    if (index >= numFood) {
        return;
    }

    // Access the food from the food buffer
    Food food = FoodBuffer.food[index];

    // Draw the food
    drawFood(food);
}
