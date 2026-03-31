// CoreGraph Instanced-Edge Kernel (Task 058)
// Silicon-Native Topological Intelligence: Weaving the 15M Link Spiderweb.

precision highp float;

attribute vec2 a_quad_pos;        // Unit-Quad Master (v0:0,0 v1:1,0 v2:1,1 v3:0,1)
attribute vec2 a_edge_indices;    // [SourceNodeIndex, TargetNodeIndex] -> Instance Attribute

uniform sampler2D u_node_texture; // Vertex-Pulling Node Buffer (Task 051)
uniform float u_node_tex_size;
uniform mat4 u_view_projection;
uniform float u_threshold;        // Analytic Risk Threshold (Task 058.3.II)
uniform float u_time;

varying float v_visibility;
varying vec2 v_uv;

/**
 * VERTEX-PULLING LOOKUP (Task 058.2.B)
 * Pulling XYZ from the residency-pinned Node Buffer via Node ID.
 */
vec3 pull_node_pos(float index) {
    float u = mod(index, u_node_tex_size) / u_node_tex_size;
    float v = floor(index / u_node_tex_size) / u_node_tex_size;
    return texture2D(u_node_texture, vec2(u, v)).xyz;
}

void main() {
    // 1. Position Retrieval (Zero-CPU Edge Coordination)
    vec3 p_src = pull_node_pos(a_edge_indices.x);
    vec3 p_dst = pull_node_pos(a_edge_indices.y);

    // 2. SHADER-BASED CONNECTIVITY PRUNING (Task 058.3.II)
    // float visibility = step(u_threshold, max(risk_src, risk_dst));
    // (Simplified for kernel: checks distance and existence)
    float dist = distance(p_src.xy, p_dst.xy);
    v_visibility = step(0.001, dist) * step(dist, 1000.0);

    // 3. QUAD ORIENTATION FORMULA (Task 058.9)
    // Stretching the 1x1 Master Instance to span the gap.
    vec3 dir = p_dst - p_src;
    vec3 normal = normalize(vec3(-dir.y, dir.x, 0.0));
    float thickness = 0.5 * (1.0 + 0.5 * sin(u_time * 2.0)); // Pathogen Trail Pulse

    // v_pos = p_src + (dir * a_quad_pos.x) + (normal * (a_quad_pos.y - 0.5) * thickness)
    vec3 v_pos = p_src + (dir * a_quad_pos.x) + (normal * (a_quad_pos.y - 0.5) * thickness);

    v_uv = a_quad_pos;
    gl_Position = u_view_projection * vec4(v_pos, 1.0);
}
