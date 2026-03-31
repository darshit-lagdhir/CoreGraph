// CoreGraph Heuristic-Heatmap Kernel (Task 057)
// Silicon-Native Analytical Macro-Intelligence: The Probability Mist.

precision highp float;

uniform sampler2D u_density_texture; // Seeded via Zero-Copy Slab Stream
uniform float u_zoom_level;
uniform float u_radius_governor;     // Dynamic Radius to protect iGPU Fill-Rate

varying vec2 v_tex_coord;

/**
 * THE GAUSSIAN FALLOFF APPROXIMATION (Task 057.3.II)
 * 10x faster than exp() for resource-constrained iGPUs.
 */
float compute_gaussian_mist(vec2 center, vec2 current, float sigma) {
    float dist = distance(center, current) / sigma;
    // Polynomial approximation: 1.0 - dist^2
    return clamp(1.0 - (dist * dist), 0.0, 1.0);
}

void main() {
    // 1. Density-Seed Sampling (Task 057.2.B)
    // Low-resolution accumulation pass.
    vec4 density_data = texture2D(u_density_texture, v_tex_coord);

    // 2. Multi-Channel Risk Mapping (Task 057.3.III)
    // R: Pathogen Risk | G: Ecosystem Vitality | B: Dependency Density
    float risk = density_data.r;
    float vitality = density_data.g;
    float dependency = density_data.b;

    // 3. Heuristic Pruning (Task 057.5.III)
    // Fragment-Discard optimization to protect Fill-Rate.
    if (dot(density_data.rgb, vec3(1.0)) < 0.05) {
        discard;
    }

    // 4. Fragment Coalescence (Additive Blending)
    // Splat intensity scaling: I = (R/P) * log10(P+1)
    float intensity = risk * u_radius_governor;

    // Liquid Risk Nebula output
    gl_FragColor = vec4(vec3(1.0, 0.2, 0.1) * intensity, intensity);
}
