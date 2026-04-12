export class InteractionManager {
    private eventBuffer: Float32Array;
    private cursor: number = 0;
    constructor(capacity: number) {
        this.eventBuffer = new Float32Array(capacity * 5); // timestamp, x, y, eventType, nodeId
    }
    public queueEvent(x: number, y: number, type: number, id: number) {
        if (this.cursor >= this.eventBuffer.length / 5) this.cursor = 0;
        const idx = this.cursor * 5;
        this.eventBuffer[idx] = performance.now();
        this.eventBuffer[idx+1] = x;
        this.eventBuffer[idx+2] = y;
        this.eventBuffer[idx+3] = type;
        this.eventBuffer[idx+4] = id;
        this.cursor++;
    }
}
