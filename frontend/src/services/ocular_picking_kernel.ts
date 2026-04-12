export class OcularPickingKernel {
    public static resolveHit(x: number, y: number, spatialBuffer: Float32Array, count: number): number {
        let closest = -1;
        let minDist = Infinity;
        // Vectorized bounds testing against raw memory buffer
        for(let i=0; i<count; i++) {
            const dx = spatialBuffer[i*3] - x;
            const dy = spatialBuffer[i*3+1] - y;
            const distSq = dx*dx + dy*dy;
            if(distSq < minDist && distSq < 1.0) {
                minDist = distSq;
                closest = i;
            }
        }
        return closest;
    }
}
