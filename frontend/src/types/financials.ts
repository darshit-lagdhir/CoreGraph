/**
 * COREGRAPH MASTER ENGINEERING SPECIFICATION: MODULE 12 - TASK 02
 * HIGH-PERFORMANCE FINANCIAL LEDGER TYPINGS: ECONOMIC SOVEREIGNTY
 * Secures the economic heartbeat of the 3.88-million-node software ocean.
 */

/**
 * Currency Codes: Template Literal Type Generation for high-velocity resolution.
 */
export type TCurrencyCode = 'USD' | 'EUR' | 'GBP' | 'SAT' | 'ETH';

/**
 * Branded Monetary Value: Prevents accidental currency mixing and rounding errors.
 * Utilizes BigInt for atomic precision (units of smallest denominator).
 */
export type TMonetaryValue<C extends TCurrencyCode> = {
    readonly value: bigint;
    readonly currency: C;
    readonly __brand: `MONETARY_${C}`;
};

/**
 * Economic Funding Source: Discriminated Union for Strategic Isolation.
 */
export type Economic_Funding_Source =
    | { source_type: 'OPEN_COLLECTIVE'; collective_id: string; transparency_score: number }
    | { source_type: 'GITHUB_SPONSORSHIP'; sponsor_id: string; tier_velocity: number }
    | { source_type: 'CORPORATE_GRANT'; entity_id: string; audit_trail_hash: string }
    | { source_type: 'COMMUNITY_DONATION'; donor_id: string; anonymity_flag: boolean };

/**
 * ITransactionalLedger: Atomic Transactional Interface Bulkhead.
 * Gated Generic ensuring 100% Flow Integrity.
 */
export interface ITransactionalLedger<C extends TCurrencyCode> {
    readonly transaction_id: string & { readonly __brand: 'TxID' };
    readonly node_id: string; // References NodeUUID
    readonly amount: TMonetaryValue<C>;
    readonly source: Economic_Funding_Source;
    readonly timestamp: number;
    readonly flow_vector: 'INFLOW' | 'OUTFLOW' | 'STAGNANT';
}

/**
 * IFiscalTelemetry: Condensed economic state for the 144Hz HUD.
 */
export interface IFiscalTelemetry {
    readonly total_funding_gap: TMonetaryValue<'USD'>;
    readonly ecosystem_burn_rate: number; // Percent per epoch
    readonly critical_nodes_at_risk: number;
}

/**
 * FISCAL_PACING_GUARD: Hardware-Aware Ledger Calibration.
 */
export const FISCAL_PACING_CONSTANTS = {
    REDLINE: { ledger_depth: 1000, async_audit: true },
    POTATO: { ledger_depth: 50, async_audit: false }
} as const;

/**
 * FISCAL FIDELITY (F_fsc): Target 1.0 (Bit-Perfect Ledger).
 */
export interface IFiscalAudit {
    readonly total_ledgers_sealed: number;
    readonly currency_coverage_ratio: 1.0;
    readonly precision_integrity: boolean;
}
