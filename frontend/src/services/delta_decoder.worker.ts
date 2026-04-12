self.onmessage = (e: MessageEvent<ArrayBuffer>) => {
    const buffer = e.data;
    const view = new DataView(buffer);
    const recordSize = 44; // 32 chars + 3 floats (4 bytes each)
    const records = buffer.byteLength / recordSize;
    // Decode logic ensures main thread is completely unblocked for 144Hz HUD
    const positions = new Float32Array(records * 3);
    for (let i = 0; i < records; i++) {
        const offset = i * recordSize;
        positions[i*3] = view.getFloat32(offset + 32, false);
        positions[i*3+1] = view.getFloat32(offset + 36, false);
        positions[i*3+2] = view.getFloat32(offset + 40, false);
    }
    self.postMessage(positions, [positions.buffer]);
};
