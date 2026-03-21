import { useState, useEffect } from 'react';
import { useGraphStore } from '../store/useGraphStore';

const DiagnosticOverlay = () => {
  const { nodes, isLoading } = useGraphStore();
  const [fps, setFps] = useState(0);
  const [ping, setPing] = useState(0);

  useEffect(() => {
    // 1. FPS High-Precision Sampling
    let frameCount = 0;
    let lastTime = performance.now();

    const tick = () => {
      frameCount++;
      const now = performance.now();
      if (now - lastTime >= 1000) {
        setFps(frameCount);
        frameCount = 0;
        lastTime = now;
      }
      requestAnimationFrame(tick);
    };
    const animId = requestAnimationFrame(tick);

    // 2. WebSocket Telemetry Latency Sampling
    const pingInterval = setInterval(() => {
        const start = performance.now();
        // Dummy fetch to check round-trip to the ASGI gateway
        fetch('/health')
            .then(() => setPing(Math.round(performance.now() - start)))
            .catch(() => setPing(-1));
    }, 5000);

    return () => {
        cancelAnimationFrame(animId);
        clearInterval(pingInterval);
    };
  }, []);

  return (
    <div className="fixed bottom-4 left-4 bg-black/60 border border-slate-700/50 p-2 rounded-md backdrop-blur-sm pointer-events-none select-none z-50">
      <div className="flex gap-4 items-center">
        <div className="flex flex-col">
          <span className="text-[10px] text-slate-500 uppercase tracking-tighter">Simulation</span>
          <span className={`text-xs font-mono font-bold ${fps < 30 ? 'text-red-400' : 'text-emerald-400'}`}>
            {fps} FPS
          </span>
        </div>

        <div className="flex flex-col border-l border-slate-800 pl-4">
          <span className="text-[10px] text-slate-500 uppercase tracking-tighter">Gateway</span>
          <span className={`text-xs font-mono font-bold ${ping > 100 ? 'text-amber-400' : 'text-slate-300'}`}>
            {ping === -1 ? 'OFFLINE' : `${ping} MS`}
          </span>
        </div>

        <div className="flex flex-col border-l border-slate-800 pl-4">
          <span className="text-[10px] text-slate-500 uppercase tracking-tighter">Topological Ocean</span>
          <span className="text-xs font-mono font-bold text-slate-300">
            {nodes.length.toLocaleString()} NODES
          </span>
        </div>

        {isLoading && (
            <div className="flex items-center gap-2 border-l border-slate-800 pl-4">
                <div className="w-1.5 h-1.5 rounded-full bg-blue-400 animate-pulse" />
                <span className="text-[10px] text-blue-400 font-bold uppercase tracking-widest">INGESTING_PHASE</span>
            </div>
        )}
      </div>
    </div>
  );
};

export default DiagnosticOverlay;
