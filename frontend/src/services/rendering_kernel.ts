import * as THREE from 'three';

/**
 * GAP RESOLUTION 004: HUD MULTI-RESOLUTION VERTEX-POOLING KERNEL.
 * Manages millions of nodes using a hybrid Point-Cloud and InstancedMesh approach.
 */
export class MultiResolutionVertexPoolingManifold {
    private hardwareTier: 'REDLINE' | 'POTATO';
    private pointCloud: THREE.Points;
    private sphereInstances: THREE.InstancedMesh;
    private maxSpheres: number;
    private cviThreshold: number = 70.0;
    
    private positions: Float32Array;
    private colors: Float32Array;
    private sizes: Float32Array;
    
    private activeSphereCount: number = 0;
    private nodeCount: number = 3880000;

    constructor(hardwareTier: 'REDLINE' | 'POTATO' = 'REDLINE') {
        this.hardwareTier = hardwareTier;
        this.maxSpheres = this.hardwareTier === 'REDLINE' ? 100000 : 500;
        this.cviThreshold = this.hardwareTier === 'REDLINE' ? 70.0 : 85.0;
        
        // 1. Initialize Monolithic BufferGeometry (The Point-Cloud Baseline)
        const geometry = new THREE.BufferGeometry();
        this.positions = new Float32Array(this.nodeCount * 3);
        this.colors = new Float32Array(this.nodeCount * 3);
        this.sizes = new Float32Array(this.nodeCount);
        
        geometry.setAttribute('position', new THREE.BufferAttribute(this.positions, 3));
        geometry.setAttribute('color', new THREE.BufferAttribute(this.colors, 3));
        geometry.setAttribute('size', new THREE.BufferAttribute(this.sizes, 1));
        
        const material = new THREE.PointsMaterial({
            size: 2,
            vertexColors: true,
            transparent: true,
            opacity: 0.8,
            sizeAttenuation: true
        });
        
        this.pointCloud = new THREE.Points(geometry, material);
        
        // 2. Initialize Dynamic Sphere Manifold (InstancedMesh)
        const sphereGeom = new THREE.SphereGeometry(1, 8, 8);
        const sphereMat = new THREE.MeshPhongMaterial({ shininess: 100 });
        this.sphereInstances = new THREE.InstancedMesh(sphereGeom, sphereMat, this.maxSpheres);
        this.sphereInstances.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
    }

    /**
     * Executes the VRAM attribute update for the 3.88M node graph.
     */
    public updateBufferGeometry(nodeData: any[]): void {
        const drawCount = Math.min(nodeData.length, this.nodeCount);
        
        for (let i = 0; i < drawCount; i++) {
            const node = nodeData[i];
            const idx = i * 3;
            
            // Sync positions
            this.positions[idx] = node.x;
            this.positions[idx + 1] = node.y;
            this.positions[idx + 2] = node.z;
            
            // Sync colors based on CVI (Chromatic Risk Intelligence)
            const color = this.calculateCVIColor(node.cvi);
            this.colors[idx] = color.r;
            this.colors[idx + 1] = color.g;
            this.colors[idx + 2] = color.b;
            
            // Point Visibility (Hide if promoted to sphere)
            this.sizes[i] = node.cvi >= this.cviThreshold ? 0.0 : 2.0;
        }
        
        this.pointCloud.geometry.attributes.position.needsUpdate = true;
        this.pointCloud.geometry.attributes.color.needsUpdate = true;
        this.pointCloud.geometry.attributes.size.needsUpdate = true;
        
        // 3. Promotion Logic: Update high-fidelity spheres
        this.promoteCriticalNodes(nodeData);
    }

    private promoteCriticalNodes(nodeData: any[]): void {
        this.activeSphereCount = 0;
        const dummy = new THREE.Object3D();
        
        for (const node of nodeData) {
            if (node.cvi >= this.cviThreshold && this.activeSphereCount < this.maxSpheres) {
                dummy.position.set(node.x, node.y, node.z);
                dummy.scale.setScalar(node.blastRadius || 1.0);
                dummy.updateMatrix();
                
                this.sphereInstances.setMatrixAt(this.activeSphereCount, dummy.matrix);
                
                if (this.sphereInstances.instanceColor) {
                    this.sphereInstances.setColorAt(this.activeSphereCount, this.calculateCVIColor(node.cvi));
                }
                
                this.activeSphereCount++;
            }
        }
        
        this.sphereInstances.count = this.activeSphereCount;
        this.sphereInstances.instanceMatrix.needsUpdate = true;
        if (this.sphereInstances.instanceColor) this.sphereInstances.instanceColor.needsUpdate = true;
    }

    private calculateCVIColor(cvi: number): THREE.Color {
        if (cvi > 80) return new THREE.Color(0xff0000); // Pathogen Red
        if (cvi > 50) return new THREE.Color(0xffa500); // Warning Orange
        return new THREE.Color(0x444444); // Safe Gray
    }

    public getObjects(): THREE.Object3D[] {
        return [this.pointCloud, this.sphereInstances];
    }
}
