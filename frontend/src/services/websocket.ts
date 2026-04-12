export class TelemetrySocket {
    private ws: WebSocket;
    constructor(url: string) {
        this.ws = new WebSocket(url);
        this.ws.binaryType = 'arraybuffer';
    }
    public onMessage(callback: (buffer: ArrayBuffer) => void) {
        this.ws.onmessage = (event) => {
            if (event.data instanceof ArrayBuffer) callback(event.data);
        };
    }
}
