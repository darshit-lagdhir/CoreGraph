import { useRef, useMemo, useCallback } from 'react';
import ForceGraph3D from 'react-force-graph-3d';
import * as THREE from 'three';
import { useGraphStore } from '../store/useGraphStore';
import type { GraphNode } from '../store/useGraphStore';

const GraphCanvas = () => {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const fgRef = useRef<any>(null);
  const { nodes, links, selectedPath, setSelectedNode } = useGraphStore();

  const getLogarithmicRadius = useCallback((node: GraphNode) => {
    // Radius mapping as specified: R = min(R_max, R_base + log10(1 + BlastRadius) * ScaleFactor)
    const baseRadius = 2;
    const maxRadius = 15;
    const scaleFactor = 2.5;
    const blastRadiusLog = Math.log10(1 + (node.blast_radius || 0));
    return Math.min(maxRadius, baseRadius + blastRadiusLog * scaleFactor);
  }, []);

  const getNodeColor = useCallback((node: GraphNode) => {
    // Chromatic Intelligence based on CVI
    // [0, 30]: Green, [31, 70]: Amber, [71, 100]: Red
    const cvi = node.cvi || 0;
    if (cvi <= 30) return '#10b981'; // Emerald Green
    if (cvi <= 70) return '#f59e0b'; // Amber Gold
    return '#ef4444'; // Signal Red
  }, []);

  const nodeObject = useMemo(() => {
    // GAP RESOLUTION 004: Multi-Resolution Vertex Pooling Handover
    // Using a hybrid strategy to maintain 144Hz vision
    return (node: object) => {
      const gNode = node as GraphNode;
      const cvi = gNode.cvi || 0;
      
      // Promotion Logic: Only high-CVI nodes get full 3D spheres
      if (cvi > 70) {
        const radius = getLogarithmicRadius(gNode);
        const color = getNodeColor(gNode);
        const geometry = new THREE.SphereGeometry(radius, 8, 8); // Optimized segment count
        const material = new THREE.MeshPhongMaterial({
          color: new THREE.Color(color),
          emissive: new THREE.Color(color),
          emissiveIntensity: 0.5,
          shininess: 100,
        });
        return new THREE.Mesh(geometry, material);
      }
      
      // Point-Cloud Baseline: Low-CVI nodes become single points
      const dotGeom = new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(0, 0, 0)]);
      const dotMat = new THREE.PointsMaterial({ color: 0x444444, size: 2 });
      return new THREE.Points(dotGeom, dotMat);
    };
  }, [getLogarithmicRadius, getNodeColor]);

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
