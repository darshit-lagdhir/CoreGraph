import pako from 'pako';
import { useGraphStore } from '../store/useGraphStore';

class TelemetryPipeline {
  private ws: WebSocket | null = null;
  private attempt = 0;
  private isConnecting = false;

  public connect() {
    if (this.isConnecting) return;
    this.isConnecting = true;

    this.ws = new WebSocket("ws://localhost:8000/ws/telemetry");
    this.ws.binaryType = "arraybuffer";

    this.ws.onopen = () => {
      this.attempt = 0;
      this.isConnecting = false;
      useGraphStore.getState().setIsLoading(false);
    };

    this.ws.onmessage = (event: MessageEvent) => {
      if (event.data instanceof ArrayBuffer) {
        try {
          const decompressedText = pako.inflate(event.data, { to: 'string' });
          const payload = JSON.parse(decompressedText);
          useGraphStore.getState().setGraphData(payload);
        } catch (error) {
           console.error("Binary decryption alignment error:", error);
        }
      }
    };

    this.ws.onclose = () => {
      this.ws = null;
      this.isConnecting = false;
      useGraphStore.getState().setIsLoading(true);
      this.reconnect();
    };

    this.ws.onerror = () => {
       // Handled by close events terminating the socket cleanly
    };
  }

  private reconnect() {
     const maxBase = 60;
     const base = 2;
     const jitter = Math.random();
     
     const delay = Math.min(Math.pow(base, this.attempt) + jitter, maxBase) * 1000;
     this.attempt += 1;
     
     setTimeout(() => {
        this.connect();
     }, delay);
  }
}

export const telemetryInstance = new TelemetryPipeline();
