import React, { useState } from 'react';
import { ControlSidebar } from '../organisms/control_sidebar';
import { IntelligenceReadout } from '../organisms/intelligence_readout';

/**
 * COREGRAPH MASTER ENGINEERING SPECIFICATION: MODULE 14
 * LAYOUT: HUDOverlay.
 * Orchestrates absolute-positioned overlay components above the WebGL canvas.
 */
export const HUDOverlay: React.FC = () => {
    // Mock selected node state for initialization
    const [selectedNode, setSelectedNode] = useState<{
        id: string;
        nomenclature: string;
        version: string;
        maintainers: number;
        balance: number;
        blast_radius: number;
        cvi_score: number;
    } | undefined>(undefined);

    return (
        <main className="hud-container" aria-label="CoreGraph HUD Overlay">
            <ControlSidebar />
            {selectedNode && (
                <IntelligenceReadout 
                    node={selectedNode} 
                    onClose={() => setSelectedNode(undefined)} 
                />
            )}
        </main>
    );
};
