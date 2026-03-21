import { useEffect } from 'react';
import { useGraphStore } from './store/useGraphStore';
import { telemetryInstance } from './services/websocket';
import './index.css';

function App() {
  const isLoading = useGraphStore(state => state.isLoading);
  const selectedNode = useGraphStore(state => state.selectedNode);

  useEffect(() => {
    telemetryInstance.connect();
  }, []);

  return (
    <>
      <div 
        id="webgl-canvas-container" 
        style={{ position: 'absolute', top: 0, left: 0, zIndex: 0, width: '100%', height: '100%' }}
      >
        {/* Placeholder awaiting Phase 6 rendering integration */}
      </div>

      <div className="hud-container">
        <div style={{ padding: '24px' }}>
          <div className="hud-panel" style={{ width: '320px' }}>
            <h1 style={{ margin: '0 0 12px 0', fontSize: '18px', fontWeight: 'bold' }}>COREGRAPH // COMMAND</h1>
            <p style={{ margin: 0, fontSize: '13px', color: isLoading ? '#ffaa00' : '#00ff88', fontFamily: 'monospace' }}>
              {isLoading ? '[ SYSTEM SYNC: OFFLINE ]' : '[ TELEMETRY LINK: ESTABLISHED ]'}
            </p>
          </div>
        </div>

        {selectedNode && (
          <div style={{ position: 'absolute', right: '24px', top: '24px' }}>
            <div className="hud-panel" style={{ width: '320px' }}>
              <h2 style={{ margin: '0 0 12px 0', fontSize: '16px' }}>{selectedNode.name}</h2>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', fontSize: '13px' }}>
                <span style={{ color: '#888888' }}>CVI</span>
                <strong>{selectedNode.cvi.toFixed(2)}</strong>
                <span style={{ color: '#888888' }}>Radius</span>
                <strong>{selectedNode.blast_radius}</strong>
                <span style={{ color: '#888888' }}>Rank</span>
                <strong>{selectedNode.pagerank.toPrecision(3)}</strong>
                <span style={{ color: '#888888' }}>Net</span>
                <strong>{selectedNode.ecosystem}</strong>
              </div>
            </div>
          </div>
        )}
      </div>
    </>
  );
}

export default App;
