/**
 * CoreGraph Data Phalanx Worker (Task 053.3)
 * Asynchronous Binary Parsing and Master Geometry Construction.
 */

self.onmessage = (event: MessageEvent) => {
    const { slabId, buffer } = event.data;
    
    if (!buffer || !(buffer instanceof ArrayBuffer)) {
        return;
    }

    // 1. ARRAYBUFFER STREAM: Bypassing the 'String Tax' (Task 053.3.I)
    // 2. DATAVIEW PARSER: GC-Invisible Ingestion (Task 053.3.II)
    // Receiving raw bytes directly from the network phalanx.
    const view = new DataView(buffer);
    const nodeStride = 16; // [ID:4, X:4, Y:4, RISK:4]
    const nodeCount = Math.floor(buffer.byteLength / nodeStride);
    
    // 3. VERTEX BUFFER CONSTRUCTOR: Writing directly to WebGL-ready TypedArray (Task 053.3.III)
    const processedBuffer = new Float32Array(nodeCount * 4);

    for (let i = 0; i < nodeCount; i++) {
        const offset = i * nodeStride;
        
        // Reading numerical primitives from contiguous memory
        const id = view.getUint32(offset, true);
        const x = view.getFloat32(offset + 4, true);
        const y = view.getFloat32(offset + 8, true);
        const risk = view.getFloat32(offset + 12, true);

        // Mapping to VBO-aligned geometry
        processedBuffer[i * 4] = id;
        processedBuffer[i * 4 + 1] = risk;
        processedBuffer[i * 4 + 2] = x;
        processedBuffer[i * 4 + 3] = y;
    }

    // ZERO-COPY TRANSFERABLE BUFFERS (Task 053.4)
    // Detaching memory from background thread and 'Attaching' to main thread in 0ms.
    (self as any).postMessage({
        slabId,
        nodeCount,
        processedBuffer
    }, [processedBuffer.buffer]);
};
