import { useGraphStore } from '../store/useGraphStore';

const PropagationPanel = () => {
  const { selectedNode, selectedPath } = useGraphStore();

  if (!selectedNode) {
    return (
      <div className="bg-slate-900/80 border border-slate-700 p-4 rounded-lg backdrop-blur-md">
        <p className="text-slate-500 text-sm italic">Select a node to analyze propagation vectors.</p>
      </div>
    );
  }

  return (
    <div className="bg-slate-900/80 border border-slate-700 p-6 rounded-lg backdrop-blur-md w-80 shadow-2xl animate-fade-in">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-slate-100 font-bold text-lg">Impact Propagation</h3>
        <span className="bg-red-500/20 text-red-400 text-xs px-2 py-1 rounded font-mono border border-red-500/30">
          PROXIMITY_LOCK
        </span>
      </div>

      <div className="space-y-4">
        <div className="p-3 bg-slate-800/50 rounded border border-slate-700">
          <label className="text-slate-400 text-[10px] uppercase tracking-widest block mb-1">Target Resource</label>
          <div className="text-slate-100 font-mono text-sm truncate">{selectedNode.name}</div>
        </div>

        <div>
          <label className="text-slate-400 text-[10px] uppercase tracking-widest block mb-1">Traversed Breadcrumbs</label>
          <div className="space-y-2 max-h-48 overflow-y-auto pr-2 scrollbar-thin scrollbar-thumb-slate-700">
            {selectedPath.length > 0 ? (
              selectedPath.map((nodeId) => {
                return (
                  <div key={nodeId} className="flex items-center gap-2">
                    <div className="w-1 h-1 rounded-full bg-red-400" />
                    <span className="text-slate-300 text-xs font-mono truncate">{nodeId}</span>
                  </div>
                );
              })
            ) : (
                <div className="text-slate-500 text-xs italic">No path active.</div>
            )}
          </div>
        </div>

        <div className="pt-2 border-t border-slate-800">
            <div className="flex justify-between items-center text-[11px] mb-1">
                <span className="text-slate-400">Structural Distance</span>
                <span className="text-slate-100 font-mono">{selectedPath.length} nodes</span>
            </div>
            <div className="flex justify-between items-center text-[11px]">
                <span className="text-slate-400">Blast Radius Exposure</span>
                <span className="text-slate-100 font-mono">{(selectedNode.blast_radius || 0).toLocaleString()} nodes</span>
            </div>
        </div>
      </div>
    </div>
  );
};

export default PropagationPanel;
