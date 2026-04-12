export class LayoutStabilityKernel {
    private buffer: Float32Array;
    constructor(nodeCapacity: number) {
        this.buffer = new Float32Array(nodeCapacity * 3);
    }
    public updateFromBinaryFrame(view: DataView, offset: number, count: number) {
        for(let i=0; i<count; i++) {
            this.buffer[i*3] = view.getFloat32(offset + i*12, true);
            this.buffer[i*3+1] = view.getFloat32(offset + i*12 + 4, true);
            this.buffer[i*3+2] = view.getFloat32(offset + i*12 + 8, true);
        }
    }
}
