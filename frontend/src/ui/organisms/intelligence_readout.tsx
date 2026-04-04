import React from 'react';

/**
 * COREGRAPH MASTER ENGINEERING SPECIFICATION: MODULE 14
 * ORGANISM: IntelligenceReadout.
 * Orchestrates dynamic, high-fidelity presentation of selected node data.
 */
interface NodeData {
  id: string;
  nomenclature: string;
  version: string;
  maintainers: number;
  balance: number;
  blast_radius: number;
  cvi_score: number;
}

export const IntelligenceReadout: React.FC<{ node?: NodeData; onClose: () => void }> = ({ node, onClose }) => {
  if (!node) return null;

  const currencyFormatter = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  });

  return (
    <article 
      className="fixed top-8 right-8 w-80 bg-bg-surface border border-muted p-6 rounded-lg backdrop-blur-xl shadow-2xl z-hud-overlay"
      aria-label={`Intelligence Readout for ${node.nomenclature}`}
      role="region"
    >
      <header className="flex justify-between items-start mb-6">
        <div>
          <h2 className="text-xl font-bold text-main">{node.nomenclature}</h2>
          <p className="text-xs font-mono text-dim">{node.version} | ID: {node.id}</p>
        </div>
        <button 
          onClick={onClose}
          className="text-dim hover:text-main transition-fast"
          aria-label="Close Readout"
        >
          ✕
        </button>
      </header>

      <section className="space-y-6">
        <div className="grid grid-cols-2 gap-4">
          <div className="flex flex-col gap-1">
            <span className="text-[10px] text-dim uppercase tracking-widest font-semibold">Maintainers</span>
            <span className={`text-lg font-mono ${node.maintainers === 0 ? 'text-threat-critical' : 'text-main'}`}>
              {node.maintainers}
            </span>
          </div>
          <div className="flex flex-col gap-1 text-right">
            <span className="text-[10px] text-dim uppercase tracking-widest font-semibold">CVI Index</span>
            <span className="text-lg font-mono text-threat-unfunded">
              {node.cvi_score.toFixed(2)}
            </span>
          </div>
        </div>

        <div className="flex flex-col gap-1 pt-4 border-t border-border-muted">
          <span className="text-[10px] text-dim uppercase tracking-widest font-semibold">Financial Ledger (USD)</span>
          <span className={`text-2xl font-bold tracking-tight ${node.balance === 0 ? 'text-threat-critical' : 'text-sustainability'}`}>
            {currencyFormatter.format(node.balance)}
          </span>
        </div>

        <div className="flex flex-col gap-1 pt-4 border-t border-border-muted">
          <span className="text-[10px] text-dim uppercase tracking-widest font-semibold">Downstream Blast Radius</span>
          <div className="flex items-center gap-2">
            <div className="flex-1 h-2 bg-bg-surface-elevated rounded-full overflow-hidden">
                <div 
                  className="h-full bg-threat-critical" 
                  style={{ width: `${Math.min(node.blast_radius / 1000 * 100, 100)}%` }} 
                />
            </div>
            <span className="text-xs font-mono text-threat-critical">{node.blast_radius}</span>
          </div>
        </div>
      </section>

      <footer className="mt-8 flex gap-2">
          <button className="flex-1 py-2 bg-threat-critical text-bg-void text-xs font-bold rounded uppercase tracking-widest hover:opacity-90 transition-fast">
              Quarantine
          </button>
          <button className="flex-1 py-2 border border-border-muted text-main text-xs font-bold rounded uppercase tracking-widest hover:bg-bg-surface-elevated transition-fast">
              Investigate
          </button>
      </footer>
    </article>
  );
};
