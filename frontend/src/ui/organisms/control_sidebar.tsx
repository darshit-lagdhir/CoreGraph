import React, { useState } from 'react';
import { Switch, Slider } from '../atoms/inputs';

/**
 * COREGRAPH MASTER ENGINEERING SPECIFICATION: MODULE 14
 * ORGANISM: ControlSidebar.
 * Orchestrates threat-filter toggles and visual isolation mechanisms.
 */
export const ControlSidebar: React.FC = () => {
    // Local state for debouncing
    const [criticalFilter, setCriticalFilter] = useState(false);
    const [maintainerThreshold, setMaintainerThreshold] = useState(100);
    const [financialThreshold, setFinancialThreshold] = useState(1000000);

    return (
        <aside className="hud-sidebar" aria-label="Control Sidebar">
            <header className="mb-8">
                <h1 className="text-xl font-bold text-main tracking-tighter">COREGRAPH</h1>
                <p className="text-xs text-dim uppercase tracking-widest mt-1">Sovereign Intelligence HUD</p>
            </header>

            <section className="flex flex-col gap-4">
                <div className="text-xs font-semibold text-dim uppercase tracking-wider mb-2">Threat Isolation</div>
                <Switch 
                    id="critical-threats"
                    label="Isolate Critical Threats"
                    description="Filter visibility by CVI threshold."
                    checked={criticalFilter}
                    onChange={setCriticalFilter}
                />
                
                <div className="h-px bg-border-muted my-2" />

                <div className="text-xs font-semibold text-dim uppercase tracking-wider mb-2">Human & Financial Metrics</div>
                <Slider 
                    id="maintainer-filter"
                    label="Maintainer Count"
                    unit="m"
                    min={0}
                    max={100}
                    value={maintainerThreshold}
                    onChange={setMaintainerThreshold}
                />
                <Slider 
                    id="financial-filter"
                    label="Funding Threshold"
                    unit="$"
                    min={0}
                    max={10000000}
                    value={financialThreshold}
                    onChange={setFinancialThreshold}
                />
            </section>

            <footer className="mt-auto pt-8 border-t border-border-muted">
                <div className="flex justify-between items-center text-xs font-mono text-dim">
                    <span>STATUS: SOVEREIGN</span>
                    <span className="text-threat-safe">F_per: 1.0</span>
                </div>
            </footer>
        </aside>
    );
};
