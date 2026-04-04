/**
 * COREGRAPH MASTER ENGINEERING SPECIFICATION: MODULE 12 - TASK 04
 * COMPOSITE VULNERABILITY METRIC SCHEMAS: ANALYTICAL SOVEREIGNTY
 * Quantifies the peril of the 3.88-million-node software ocean.
 */

/**
 * ERiskVector: Exhaustive dimensions of the threat manifold.
 */
export type ERiskVector =
    | 'STRUCTURAL_CRITICALITY'
    | 'TEMPORAL_DECAY'
    | 'FINANCIAL_EXPOSURE'
    | 'MAINTAINER_ENTROPY'
    | 'BLAST_RADIUS';

/**
 * TScoreValue: Branded Score Atom.
 * Prevents accidental cross-pollution of risk dimensions.
 */
export type TScoreValue<V extends ERiskVector> = {
    readonly raw_value: number; // [0.0 - 1.0] normalized precision
    readonly weight: number;
    readonly __risk_type: `RISK_${V}`;
};

/**
 * Threat_Vector_Schema: Discriminated Union for Signal Isolation.
 */
export type Threat_Vector_Schema =
    | { vector_id: 'STRUCTURAL'; score: TScoreValue<'STRUCTURAL_CRITICALITY'>; centrality_bias: number }
    | { vector_id: 'TEMPORAL'; score: TScoreValue<'TEMPORAL_DECAY'>; velocity_delta: number }
    | { vector_id: 'FINANCIAL'; score: TScoreValue<'FINANCIAL_EXPOSURE'>; burn_rate_hazard: number };

/**
 * TRiskManifold: Multi-Dimensional Analytical Interface.
 * Gated Generic ensuring exhaustive dimension coverage.
 */
export interface TRiskManifold<D extends ERiskVector> {
    readonly composite_cvi: number;
    readonly dimensions: readonly TScoreValue<D>[];
    readonly updated_at: number;
    readonly confidence_interval: number; // [0.0 - 1.0]
}

/**
 * ANALYTICAL_PACING_GUARD: Hardware-Aware Scoring Calibration.
 */
export const ANALYTICAL_PACING_CONSTANTS = {
    REDLINE: { score_depth: Infinity, eager_eval: true },
    POTATO: { score_depth: 3, eager_eval: false }
} as const;

/**
 * ANALYTICAL FIDELITY (F_ana): Target 1.0 (Non-Repudiable Peril).
 */
export interface IAnalyticalAudit {
    readonly metrics_sealed: number;
    readonly vector_safety_ratio: 1.0;
    readonly scoring_latency: number;
}
