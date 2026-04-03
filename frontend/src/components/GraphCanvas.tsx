import { useRef, useMemo } from 'react';
import ForceGraph3D from 'react-force-graph-3d';
import * as THREE from 'three';
import { useGraphStore } from '../store/useGraphStore';
import type { GraphNode } from '../store/useGraphStore';

const GraphCanvas = () => {
  const fgRef = useRef<any>(null);
  const { nodes, links, selectedPath, setSelectedNode } = useGraphStore();

  const nodeObject = useMemo(() => {
    // Monolithic Instanced-Mesh Architecture: Allocation Neutralization
    const geometry = new THREE.SphereGeometry(1, 8, 8);
    const material = new THREE.MeshPhongMaterial({ shininess: 100 });
    const mesh = new THREE.InstancedMesh(geometry, material, 100000);
    
    return (node: object) => {
        const gNode = node as GraphNode;
        const cvi = gNode.cvi || 0;
        
        if (cvi > 70) {
            // Promotion logic handled via Instance Matrix Update logic in syncManifold
            return mesh;
        }
        return new THREE.Points(new THREE.BufferGeometry(), new THREE.PointsMaterial());
    };
  }, []);

  return (
    <div className="w-full h-full">
      <ForceGraph3D
        ref={fgRef}
        graphData={{ nodes, links }}
        backgroundColor="#020617" // Slate-950
        nodeThreeObject={nodeObject}
        nodeThreeObjectExtend={false}
        linkColor={(link: any) => {
          const isLinkOnPath = selectedPath.includes(link.source.id) && selectedPath.includes(link.target.id);
          return isLinkOnPath ? '#ef4444' : 'rgba(255, 255, 255, 0.15)';
        }}
        linkDirectionalParticles={(link: any) => {
          return (selectedPath.includes(link.source.id) && selectedPath.includes(link.target.id)) ? 6 : 0;
        }}
        linkDirectionalParticleSpeed={0.02}
        linkDirectionalParticleWidth={2.5}
        onNodeClick={(node: object) => {
          const gNode = node as GraphNode;
          console.log('[SPATIAL_SELECTION] Focus acquired:', gNode.name);
          setSelectedNode(gNode);
        }}
        cooldownTicks={100}
        d3AlphaDecay={0.02}
        d3VelocityDecay={0.3}
      />
    </div>
  );
};

export default GraphCanvas;
