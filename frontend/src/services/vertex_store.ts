export class VertexStore {
    public rowPtr: Uint32Array;
    public colIdx: Uint32Array;

    constructor(maxNodes: number, maxEdges: number) {
        this.rowPtr = new Uint32Array(maxNodes + 1);
        this.colIdx = new Uint32Array(maxEdges);
    }

    public syncFromBuffer(rowPtrBuffer: ArrayBuffer, colIdxBuffer: ArrayBuffer) {
        this.rowPtr = new Uint32Array(rowPtrBuffer);
        this.colIdx = new Uint32Array(colIdxBuffer);
    }

    public getNeighbors(nodeId: number): Uint32Array {
        const start = this.rowPtr[nodeId];
        const end = this.rowPtr[nodeId + 1];
        return this.colIdx.subarray(start, end);
    }
}
