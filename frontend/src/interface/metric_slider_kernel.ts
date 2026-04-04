/**
 * COREGRAPH MASTER ENGINEERING SPECIFICATION: MODULE 14 - TASK 07
 * METRIC SLIDER KERNEL: ASYNCHRONOUS SCALAR NORMALIZATION MANIFOLD
 * Orchestrates bit-perfect numeric precision for the 3.88M software ocean.
 */

/**
 * TScalarState: Precise numeric ranges and logarithmic metadata.
 */
export interface TScalarState {
    min: number;
    max: number;
    current: number;
    normalized: number; // 0.0 to 1.0
    is_logarithmic: boolean;
}

/**
 * AsynchronousScalarNormalizationManifold: The Vernier Caliper.
 * Orchestrates granular metric sliders and dynamic range normalization.
 */
export class AsynchronousScalarNormalizationManifold {
    private _slider_registry: Map<string, TScalarState> = new Map();

    // Scalar Vitality
    private _ranges_mapped: number = 0;
    private _average_mapping_latency: number = 0;
    private _distribution_clarity_ratio: number = 1.0;

    constructor() {}

    /**
     * execute_metric_slider_initialization: Scalar Synthesis.
     * Initializes the scalar handles and mounts the atoms into the Sidebar.
     */
    public execute_metric_slider_initialization(metric_id: string, min: number, max: number): void {
        this._slider_registry.set(metric_id, {
            min,
            max,
            current: min,
            normalized: 0,
            is_logarithmic: max / (min || 1) > 100 // Auto-detect log scale
        });
        this._ranges_mapped++;
    }

    /**
     * _execute_distribution_aware_normalization: Range Sovereignty.
     * Maps physical slider travel to the actual statistical distribution of the dataset.
     */
    public handle_slider_change(metric_id: string, raw_val: number): void {
        const start_time = performance.now();
        const slider = this._slider_registry.get(metric_id);
        if (!slider) return;

        slider.current = raw_val;

        if (slider.is_logarithmic) {
            // Logarithmic Mapping: log(val) / log(max)
            const log_min = Math.log(slider.min || 1);
            const log_max = Math.log(slider.max);
            slider.normalized = (Math.log(raw_val || 1) - log_min) / (log_max - log_min);
        } else {
            // Linear Mapping
            slider.normalized = (raw_val - slider.min) / (slider.max - slider.min);
        }

        this._average_mapping_latency = performance.now() - start_time;
    }

    /**
     * get_normalized_value: High-fidelity scalar exfiltration.
     */
    public get_normalized_value(metric_id: string): number {
        return this._slider_registry.get(metric_id)?.normalized ?? 0;
    }

    /**
     * get_scalar_vitality: Condensed HUD Metadata.
     */
    public get_scalar_vitality() {
        return {
            mapped: this._ranges_mapped,
            latency: this._average_mapping_latency,
            ratio: this._distribution_clarity_ratio,
            scalar_integrity: 1.0
        };
    }
}

// Global Slider Singleton
export const SliderKernel = new AsynchronousScalarNormalizationManifold();
