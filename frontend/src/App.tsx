import { useEffect } from 'react';
import { Activity, ShieldAlert, Cpu } from 'lucide-react';
import { useGraphStore } from './store/useGraphStore';
import { TelemetryPipeline } from './services/websocket';
import GraphCanvas from './components/GraphCanvas';

function App() {
  const { nodes, links, isLoading } = useGraphStore();

  useEffect(() => {
    // Pipeline strictly decoupled from UI loop
    const pipeline = new TelemetryPipeline('ws://localhost:8000/ws/telemetry');
    pipeline.connect();
    return () => pipeline.disconnect();
  }, []);

  return (
    <div className="relative w-full h-full bg-slate-950 text-slate-200">
      {/* 3D WebGL Canvas Layer (z-index: 0) */}
      <div className="absolute inset-0 z-0">
        <GraphCanvas />
      </div>

      {/* OSINT Command Sidebar (z-index: 50) */}
      <div className="absolute left-0 top-0 h-full w-80 bg-slate-900/80 backdrop-blur-md border-r border-slate-800 z-50 p-6 flex flex-col shadow-2xl">
        <div className="flex items-center gap-3 mb-8">
          <Activity className="text-emerald-500" size={24} />
          <h1 className="text-xl font-bold tracking-tight text-white">COREGRAPH_OSINT</h1>
        </div>

        <div className="flex flex-col gap-4 flex-grow">
          {isLoading ? (
            <div className="flex flex-col gap-2 p-4 rounded bg-slate-800/50 border border-slate-700 animate-pulse">
              <span className="text-xs text-slate-400 uppercase tracking-widest font-mono">Stream Vector</span>
              <span className="text-sm text-emerald-400 font-mono">AWAITING BINARY PAYLOAD...</span>
            </div>
          ) : (
            <div className="flex flex-col gap-2 p-4 rounded bg-slate-800/50 border border-slate-700">
              <span className="text-xs text-slate-400 uppercase tracking-widest font-mono">Matrix Nodes</span>
              <span className="text-2xl text-white font-mono">{nodes.length.toLocaleString()}</span>

              <span className="text-xs text-slate-400 uppercase tracking-widest font-mono mt-2">Matrix Edges</span>
              <span className="text-xl text-white font-mono">{links.length.toLocaleString()}</span>
            </div>
          )}
        </div>

        <div className="mt-auto border-t border-slate-800 pt-4">
          <div className="flex items-center gap-2 text-xs text-slate-500 font-mono">
            <Cpu size={14} />
            <span>i9-13980hx THREAD POOL ACTIVE</span>
          </div>
        </div>
      </div>

      {/* Floating Diagnostics Panel (bottom right) */}
      <div className="absolute bottom-6 right-6 w-72 bg-slate-900/80 backdrop-blur-md border border-slate-800 z-50 p-4 rounded shadow-xl">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs text-slate-400 uppercase tracking-widest font-mono">System CVI Limits</span>
          <ShieldAlert size={16} className="text-amber-500" />
        </div>
        <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden">
          <div className="h-full bg-gradient-to-r from-emerald-500 via-amber-500 to-rose-500 w-1/3 opacity-80" />
        </div>
        <div className="flex justify-between mt-2 text-[10px] text-slate-500 font-mono">
          <span>0 (SECURE)</span>
          <span>100 (CRITICAL)</span>
        </div>
      </div>
    </div>
  );
}

export default App;
