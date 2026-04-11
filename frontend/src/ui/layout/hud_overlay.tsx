import React, { useState, Component, ErrorInfo, ReactNode } from 'react';
import { ControlSidebar } from '../organisms/control_sidebar';
import { IntelligenceReadout } from '../organisms/intelligence_readout';

/**
 * SovereignErrorBoundary: Prevents the React Tree from dying during extreme high-speed ingestion anomalies.
 */
class SovereignErrorBoundary extends Component<{children: ReactNode}, {hasError: boolean}> {
    constructor(props: {children: ReactNode}) {
        super(props);
        this.state = { hasError: false };
    }

    static getDerivedStateFromError(_: Error) {
        return { hasError: true };
    }

    componentDidCatch(error: Error, errorInfo: ErrorInfo) {
        console.error("Critical React Boundary Violation Intercepted:", error, errorInfo);
    }

    render() {
        if (this.state.hasError) {
            return <div className="hud-container-error" style={{color: 'red'}}>HUD Render Anomaly Suppressed. 144Hz WebGL Context Maintained.</div>;
        }
        return this.props.children;
    }
}

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
        <SovereignErrorBoundary>
            <main className="hud-container" aria-label="CoreGraph HUD Overlay">
                <ControlSidebar />
                {selectedNode && (
                    <IntelligenceReadout
                        node={selectedNode}
                        onClose={() => setSelectedNode(undefined)}
                    />
                )}
            </main>
        </SovereignErrorBoundary>
    );
};
