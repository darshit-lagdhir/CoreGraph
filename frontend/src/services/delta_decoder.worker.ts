export class DeltaDecoder {
    static decode(buffer: ArrayBuffer, count: number) {
        const view = new DataView(buffer);
        for(let i=0; i<count; i++) {
            const offset = i * 24;
            const seq = view.getBigUint64(offset, true);
            const nodeId = view.getUint32(offset + 8, true);
        }
    }
}
