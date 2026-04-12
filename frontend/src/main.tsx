import React, { useEffect, useRef } from 'react';
import { createRoot } from 'react-dom/client';
import { HUDOverlay } from './ui/layout/hud_overlay';
import './ui/globals.css';
import { ContextKernel } from './visualization/context_kernel';
import { InstancedManifold } from './visualization/instanced_manifold';
import { AsynchronousViewportTransformationManifold } from './visualization/camera_alignment_kernel';

const App = () => {
    const canvasRef = useRef<HTMLCanvasElement>(null);

    useEffect(() => {
        if (!canvasRef.current) return;

        let animationFrameId: number;
        const canvas = canvasRef.current;

        try {
            // 1. Ignition
            const gl = ContextKernel.initialize_webgl_context(canvas);

            // Force canvas resize to fill viewport
            const handleResize = () => {
                canvas.width = window.innerWidth;
                canvas.height = window.innerHeight;
                gl.viewport(0, 0, canvas.width, canvas.height);
            };
            window.addEventListener('resize', handleResize);
            handleResize();

            const boot = async () => {
                // 1. Generate 100,000 Software Ecosystem Nodes for the visualizer
                const NODE_COUNT = 100000;

                const position_buffer = gl.createBuffer();
                gl.bindBuffer(gl.ARRAY_BUFFER, position_buffer);

                // INSTANCE_STRIDE = 32 (8 floats per instance = 32 bytes)
                // layout: [x, y, z, size, cvi, pad, pad, pad]
                const data = new Float32Array(NODE_COUNT * 8);
                for(let i = 0; i < NODE_COUNT; i++) {
                    const r = 100 * Math.cbrt(Math.random());
                    const theta = Math.random() * 2 * Math.PI;
                    const phi = Math.acos(2 * Math.random() - 1);

                    const idx = i * 8;
                    data[idx] = r * Math.sin(phi) * Math.cos(theta); // x
                    data[idx+1] = r * Math.sin(phi) * Math.sin(theta); // y
                    data[idx+2] = r * Math.cos(phi); // z
                    data[idx+3] = Math.random() * 2.0 + 1.0; // size

                    // CVI Threat Level
                    data[idx+4] = Math.random() > 0.95 ? 80 + Math.random() * 20 : Math.random() * 40;
                }

                // Directly allocate and upload the 32-byte stride buffer
                gl.bufferData(gl.ARRAY_BUFFER, data, gl.STATIC_DRAW);

                // 2. Setup Shaders (VAO will immediately latch onto position_buffer)
                await InstancedManifold.execute_unified_shader_initialization(gl);

                // 4. Camera Init
                const cameraManifold = new AsynchronousViewportTransformationManifold();
                let angle = 0;
                let lastTime = performance.now();

                const render = (time: number) => {
                    const dt = time - lastTime;
                    lastTime = time;
                    angle += 0.0003 * dt;

                    gl.clearColor(0.011, 0.011, 0.015, 1.0); // background
                    gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
                    gl.enable(gl.BLEND);
                    gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA);

                    const vpMatrix = cameraManifold.execute_perspective_transformation_sequence({
                        position: [Math.cos(angle) * 150, 40, Math.sin(angle) * 150],
                        target: [0, 0, 0],
                        fov: 45 * Math.PI / 180,
                        aspect: window.innerWidth / window.innerHeight,
                        near: 0.1,
                        far: 1000.0
                    });

                    const program = (InstancedManifold as any)._program;
                    if (program) {
                        gl.useProgram(program);
                        const loc = gl.getUniformLocation(program, 'u_view_projection');
                        if (loc) gl.uniformMatrix4fv(loc, false, vpMatrix);
                        // Draw
                        InstancedManifold.execute_atomic_instanced_draw_call(NODE_COUNT);
                    }

                    animationFrameId = requestAnimationFrame(render);
                };

                animationFrameId = requestAnimationFrame(render);
            };

            boot();

            return () => {
                window.removeEventListener('resize', handleResize);
                cancelAnimationFrame(animationFrameId);
            };
        } catch (e) {
            console.error("WebGL Engine Boot Failure:", e);
        }
    }, []);

    return (
        <>
            <canvas
                ref={canvasRef}
                style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', zIndex: 0 }}
            />
            <HUDOverlay />
        </>
    );
};

const rootEl = document.getElementById('root');
if (rootEl) {
    const root = createRoot(rootEl);
    root.render(
        <React.StrictMode>
            <App />
        </React.StrictMode>
    );
}
