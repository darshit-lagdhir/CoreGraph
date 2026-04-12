self.onmessage = (e: MessageEvent<ArrayBuffer>) => {
    const buffer = e.data;
    const view = new Float32Array(buffer);
    const count = view.length / 3;
    // GPU Cache boundary optimized physics integrator
    for(let i=0; i<count; i++) {
        view[i*3] = view[i*3] * 0.95; // friction / gravity
        view[i*3+1] = view[i*3+1] * 0.95;
        view[i*3+2] = view[i*3+2] * 0.95;
    }
    self.postMessage(view.buffer, [view.buffer]);
};
