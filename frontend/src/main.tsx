import React, { useEffect, useRef } from 'react';
import { createRoot } from 'react-dom/client';
import { HUDOverlay } from './ui/layout/hud_overlay';
import './ui/globals.css';
import { AsynchronousWebGLContextManifold } from './visualization/context_kernel';

const App = () => {
    const canvasRef = useRef<HTMLCanvasElement>(null);

    useEffect(() => {
        if (canvasRef.current) {
            try {
                // Initialize WebGL Context
                const kernel = new AsynchronousWebGLContextManifold();
                kernel.initialize_webgl_context(canvasRef.current);
            } catch (e) {
                console.error("WebGL Init Error:", e);
            }
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
