export class SovereignUIState {
    public isolateCriticalThreats: boolean = false;
    public maintainerThreshold: number = 100; // Value from 0 to 100m
    public fundingThreshold: number = 10000000;    // Value from 0 to 10M

    private listeners: (() => void)[] = [];

    public subscribe(listener: () => void) {
        this.listeners.push(listener);
        return () => {
            this.listeners = this.listeners.filter(l => l !== listener);
        };
    }

    public notify() {
        for (const listener of this.listeners) {
            listener();
        }
    }
}

export const GUIStore = new SovereignUIState();
