import React, { useState, useEffect } from 'react';
import { Switch, Slider } from '../atoms/inputs';
import { GUIStore } from '../../store/ui_store';

/**
 * COREGRAPH MASTER ENGINEERING SPECIFICATION: MODULE 14
 * ORGANISM: ControlSidebar.
 * Orchestrates threat-filter toggles and visual isolation mechanisms.
 */
export const ControlSidebar: React.FC = () => {
    // Local state for debouncing
    const [criticalFilter, setCriticalFilter] = useState(GUIStore.isolateCriticalThreats);
    const [maintainerThreshold, setMaintainerThreshold] = useState(GUIStore.maintainerThreshold);
    const [financialThreshold, setFinancialThreshold] = useState(GUIStore.fundingThreshold);

    useEffect(() => {
        GUIStore.isolateCriticalThreats = criticalFilter;
        GUIStore.maintainerThreshold = maintainerThreshold;
        GUIStore.fundingThreshold = financialThreshold;
        GUIStore.notify();
    }, [criticalFilter, maintainerThreshold, financialThreshold]);

    return (
        <aside className="hud-sidebar bg-surface-elevated/80 shadow-2xl z-10 w-96 backdrop-blur-md rounded-xl m-4 border-l border-b border-border-active flex flex-col pointer-events-auto transition-gpu" aria-label="Control Sidebar">
            <header className="mb-4 bg-void/50 p-4 rounded-t-lg border-b border-border-muted shadow-sm">
                <h1 className="text-2xl font-black text-main tracking-tighter uppercase drop-shadow-md">COREGRAPH</h1>
                <p className="text-[0.65rem] text-threat-safe font-mono tracking-widest mt-1 opacity-90">&gt;&gt; Sovereign Intelligence HUD</p>
            </header>

            <section className="flex flex-col gap-6 px-4 pb-4">
                <div>
                    <div className="text-[0.7rem] font-bold text-dim uppercase tracking-widest mb-3 flex items-center gap-2"><span className="w-2 h-2 bg-threat-critical rounded-full inline-block animate-pulse"></span>Threat Isolation</div>
                    <Switch
                        id="critical-threats"
                        label="Isolate Critical Threats"
                        description="Filter hardware visibility by severe CVI scoring threshold."
                        checked={criticalFilter}
                        onChange={setCriticalFilter}
                    />
                </div>

                <div className="h-px bg-border-muted/50 w-full" />

                <div>
                    <div className="text-[0.7rem] font-bold text-dim uppercase tracking-widest mb-4 flex items-center gap-2"><span className="w-2 h-2 bg-text-muted rounded-full inline-block"></span>Human & Financial Logistics</div>
                    <Slider
                        id="maintainer-filter"
                        label="Max Maintainer Count"
                        unit="m"
                        min={0}
                        max={100}
                        value={maintainerThreshold}
                        onChange={setMaintainerThreshold}
                    />
                    <div className="mt-5">
                       <Slider
                           id="financial-filter"
                           label="Max Funding Threshold"
                           unit="$"
                           min={0}
                           max={10000000}
                           value={financialThreshold}
                           onChange={setFinancialThreshold}
                       />
                    </div>
                </div>
            </section>

            <footer className="mt-auto p-4 border-t border-border-muted/60 bg-void/30 rounded-b-lg">
                <div className="flex justify-between items-center text-[0.65rem] font-mono text-dim tracking-widest">
                    <span>SYSTEM: <span className="text-threat-safe font-bold glow-threat-safe">DISTRIBUTED SPATIAL-NAV SEALED</span></span>
                    <span className="text-threat-safe font-bold glow-threat-safe">F_per: 1.0</span>
                </div>
            </footer>
        </aside>
    );
};
