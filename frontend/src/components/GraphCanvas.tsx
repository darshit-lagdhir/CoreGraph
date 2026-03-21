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
    // Custom shader-based rendering strategy (simplified representation here)
    // Instanced rendering would typically require low-level THREE.InstancedMesh access,
    // which react-force-graph-3d supports via nodeThreeObject.
    return (node: object) => {
      const gNode = node as GraphNode;
      const radius = getLogarithmicRadius(gNode);
      const color = getNodeColor(gNode);

      const isNodeOnPath = selectedPath.includes(gNode.id);

      const geometry = new THREE.SphereGeometry(radius, 16, 16);
      const material = new THREE.MeshPhongMaterial({
        color: new THREE.Color(color),
        transparent: true,
        opacity: selectedPath.length > 0 ? (isNodeOnPath ? 1.0 : 0.15) : 0.9,
        emissive: isNodeOnPath ? new THREE.Color(color) : new THREE.Color(0x000000),
        emissiveIntensity: isNodeOnPath ? 0.8 : 0,
        shininess: 100,
      });

      // Dispose logic internally handled by react-force-graph on removal usually,
      // but provided as a baseline here.
      return new THREE.Mesh(geometry, material);
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
