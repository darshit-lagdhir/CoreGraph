import pako from 'pako';
import { useGraphStore } from '../store/useGraphStore';

interface BackoffConfig {
    baseDelayMs: number;
    maxDelayMs: number;
    maxAttempts: number;
}

export class TelemetryPipeline {
    private socket: WebSocket | null = null;
    private uri: string;
    private attempts: number = 0;
    private config: BackoffConfig = {
        baseDelayMs: 1000,
        maxDelayMs: 60000,
        maxAttempts: 10
    };

    constructor(uri: string) {
        this.uri = uri;
    }

    public connect(): void {
        this.socket = new WebSocket(this.uri);
        this.socket.binaryType = 'arraybuffer';

        this.socket.onopen = this.handleOpen.bind(this);
        this.socket.onmessage = this.handleMessage.bind(this);
        this.socket.onclose = this.handleClose.bind(this);
        this.socket.onerror = this.handleError.bind(this);
    }

    private handleOpen(): void {
        this.attempts = 0;
        console.log('[TELEMETRY] Binary websocket bound.');
    }

    private handleMessage(event: MessageEvent): void {
        if (event.data instanceof ArrayBuffer) {
            try {
                // Determine ping vs direct structural arrays
                const isPing = event.data.byteLength === 4; 
                if (isPing) return; 

                // Decompressing utilizing 64KB ArrayBuffer vectors directly
                const inflatedString = pako.inflate(new Uint8Array(event.data), { to: 'string' });
                const graphJson = JSON.parse(inflatedString);
                
                useGraphStore.getState().setGraphData(graphJson);
            } catch (error) {
                console.error('[TELEMETRY_FAULT] Binary parsing sequence halted:', error);
            }
        }
    }

    private handleClose(event: CloseEvent): void {
        console.warn(`[TELEMETRY_LOSS] Connection dropped logically: ${event.code}`);
        this.reconnectSequence();
    }

    private handleError(_error: Event): void {
        // Suppress complex trace variables triggering memory garbage collection loops
    }

    private reconnectSequence(): void {
        if (this.attempts >= this.config.maxAttempts) {
            console.error('[TELEMETRY_FAULT] Maximum mathematical retries executed. Pipeline locked.');
            return;
        }

        const exponentialDelay = Math.min(
            this.config.maxDelayMs, 
            this.config.baseDelayMs * Math.pow(2, this.attempts)
        );
        
        // Include mathematical Jitter neutralizing systemic race conditions
        const jitterMatrix = exponentialDelay + (Math.random() * 1000);

        this.attempts++;
        useGraphStore.getState().resetGraph();
        
        setTimeout(() => {
            console.log(`[TELEMETRY] Evaluating pipeline matrix: attempt ${this.attempts}`);
            this.connect();
        }, jitterMatrix);
    }

    public disconnect(): void {
        if (this.socket) {
            this.socket.close(1000, 'Client disconnected');
            this.socket = null;
        }
    }
}
