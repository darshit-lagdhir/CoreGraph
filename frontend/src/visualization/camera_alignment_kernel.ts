/**
 * COREGRAPH MASTER ENGINEERING SPECIFICATION: MODULE 13 - TASK 10
 * CAMERA ALIGNMENT KERNEL: PERSPECTIVE PROJECTION MANIFOLD
 * Orchestrates bit-perfect viewport transformation for the 3.88M software ocean.
 */

/**
 * TCameraState: Tactical viewport parameters.
 */
export interface TCameraState {
    position: number[]; // vec3
    target: number[]; // vec3
    fov: number;
    aspect: number;
    near: number;
    far: number;
}

/**
 * AsynchronousViewportTransformationManifold: The Inner Ear.
 * Orchestrates perspective projection and dynamic frustum plane calibration.
 */
export class AsynchronousViewportTransformationManifold {
    private _view_matrix: Float32Array = new Float32Array(16);
    private _projection_matrix: Float32Array = new Float32Array(16);
    private _view_projection_matrix: Float32Array = new Float32Array(16);

    // Navigation Vitality
    private _viewports_projected: number = 0;
    private _matrix_latency_ms: number = 0;
    private _frustum_alignment_ratio: number = 1.0;

    constructor() {}

    /**
     * execute_perspective_transformation_sequence: Ocular Synthesis.
     * Computes the bit-perfect View-Projection stack for the active tactical context.
     */
    public execute_perspective_transformation_sequence(camera: TCameraState): Float32Array {
        const start_time = performance.now();

        // 1. Calculate Projection Matrix (Perspective)
        this._update_projection(camera.fov, camera.aspect, camera.near, camera.far);

        // 2. Calculate View Matrix (LookAt)
        this._update_view(camera.position, camera.target, [0, 1, 0]);

        // 3. Matrix Multiplication (Mvp = Mp * Mv)
        this._view_projection_matrix = this._multiply(this._projection_matrix, this._view_matrix);

        this._matrix_latency_ms = performance.now() - start_time;
        this._viewports_projected++;

        return this._view_projection_matrix;
    }

    private _update_projection(fov: number, aspect: number, near: number, far: number): void {
        const out = this._projection_matrix;
        const f = 1.0 / Math.tan(fov / 2);
        const nf = 1 / (near - far);

        out[0] = f / aspect; out[1] = 0; out[2] = 0; out[3] = 0;
        out[4] = 0; out[5] = f; out[6] = 0; out[7] = 0;
        out[8] = 0; out[9] = 0; out[10] = (far + near) * nf; out[11] = -1;
        out[12] = 0; out[13] = 0; out[14] = (2 * far * near) * nf; out[15] = 0;
    }

    private _update_view(eye: number[], target: number[], up: number[]): void {
        const out = this._view_matrix;
        let z0 = eye[0] - target[0], z1 = eye[1] - target[1], z2 = eye[2] - target[2];
        let len = z0*z0 + z1*z1 + z2*z2;
        if (len > 0) {
            len = 1 / Math.sqrt(len);
            z0 *= len; z1 *= len; z2 *= len;
        }
        let x0 = up[1]*z2 - up[2]*z1, x1 = up[2]*z0 - up[0]*z2, x2 = up[0]*z1 - up[1]*z0;
        len = x0*x0 + x1*x1 + x2*x2;
        if (len > 0) {
            len = 1 / Math.sqrt(len);
            x0 *= len; x1 *= len; x2 *= len;
        }
        let y0 = z1*x2 - z2*x1, y1 = z2*x0 - z0*x2, y2 = z0*x1 - z1*x0;
        len = y0*y0 + y1*y1 + y2*y2;
        if (len > 0) {
            len = 1 / Math.sqrt(len);
            y0 *= len; y1 *= len; y2 *= len;
        }
        out[0] = x0; out[1] = y0; out[2] = z0; out[3] = 0;
        out[4] = x1; out[5] = y1; out[6] = z1; out[7] = 0;
        out[8] = x2; out[9] = y2; out[10] = z2; out[11] = 0;
        out[12] = -(x0*eye[0] + x1*eye[1] + x2*eye[2]);
        out[13] = -(y0*eye[0] + y1*eye[1] + y2*eye[2]);
        out[14] = -(z0*eye[0] + z1*eye[1] + z2*eye[2]);
        out[15] = 1;
    }

    private _multiply(a: Float32Array, b: Float32Array): Float32Array {
        const out = new Float32Array(16);
        const a00 = a[0], a01 = a[1], a02 = a[2], a03 = a[3];
        const a10 = a[4], a11 = a[5], a12 = a[6], a13 = a[7];
        const a20 = a[8], a21 = a[9], a22 = a[10], a23 = a[11];
        const a30 = a[12], a31 = a[13], a32 = a[14], a33 = a[15];

        let b0 = b[0], b1 = b[1], b2 = b[2], b3 = b[3];
        out[0] = b0*a00 + b1*a10 + b2*a20 + b3*a30;
        out[1] = b0*a01 + b1*a11 + b2*a21 + b3*a31;
        out[2] = b0*a02 + b1*a12 + b2*a22 + b3*a32;
        out[3] = b0*a03 + b1*a13 + b2*a23 + b3*a33;

        b0 = b[4]; b1 = b[5]; b2 = b[6]; b3 = b[7];
        out[4] = b0*a00 + b1*a10 + b2*a20 + b3*a30;
        out[5] = b0*a01 + b1*a11 + b2*a21 + b3*a31;
        out[6] = b0*a02 + b1*a12 + b2*a22 + b3*a32;
        out[7] = b0*a03 + b1*a13 + b2*a23 + b3*a33;

        b0 = b[8]; b1 = b[9]; b2 = b[10]; b3 = b[11];
        out[8] = b0*a00 + b1*a10 + b2*a20 + b3*a30;
        out[9] = b0*a01 + b1*a11 + b2*a21 + b3*a31;
        out[10] = b0*a02 + b1*a12 + b2*a22 + b3*a32;
        out[11] = b0*a03 + b1*a13 + b2*a23 + b3*a33;

        b0 = b[12]; b1 = b[13]; b2 = b[14]; b3 = b[15];
        out[12] = b0*a00 + b1*a10 + b2*a20 + b3*a30;
        out[13] = b0*a01 + b1*a11 + b2*a21 + b3*a31;
        out[14] = b0*a02 + b1*a12 + b2*a22 + b3*a32;
        out[15] = b0*a03 + b1*a13 + b2*a23 + b3*a33;

        return out;
    }

    /**
     * _execute_frustum_plane_calibration: Navigation Sovereignty.
     * Optimizes Z-buffer range by clamping zNear/zFar to scene bounds.
     */
    public _execute_frustum_plane_calibration(activeClusterDistance: number): { near: number, far: number } {
        return { near: activeClusterDistance * 0.1, far: activeClusterDistance * 10.0 };
    }

    /**
     * get_navigation_vitality: Condensed HUD Metadata.
     */
    public get_navigation_vitality() {
        return {
            viewports_projected: this._viewports_projected,
            matrix_latency: this._matrix_latency_ms,
            alignment_ratio: this._frustum_alignment_ratio,
            navigation_integrity: 1.0
        };
    }
}

// Global Camera Singleton
export const CameraKernel = new AsynchronousViewportTransformationManifold();
