/**
 * COREGRAPH MASTER ENGINEERING SPECIFICATION: MODULE 12 - TASK 01
 * THE ALGEBRAIC DATA CONTRACT REGISTRY: DEFINITIVE STRUCTURAL SOVEREIGNTY
 * Defines the identity of the 3.88-million-node forensic ocean.
 */

export type NodeUUID = string & { readonly __brand: 'NodeUUID' };
export type EdgeUUID = string & { readonly __brand: 'EdgeUUID' };

export interface ICoreGraphNode {
    readonly id: NodeUUID;
    readonly name: string;
    readonly version: string;
    readonly type: 'PACKAGE' | 'MAINTAINER' | 'REPOSITORY' | 'NETWORK_NODE';

    readonly cvi_score: number;      // Composite Vulnerability Index
    readonly page_rank: number;      // Centrality Multiplier
    readonly maintenance_health: number; // [0.0 - 1.0]

    readonly position: {
        readonly x: number;
        readonly y: number;
        readonly z: number;
    };

    readonly metadata: {
        readonly financial_impact: number;
        readonly maintainer_count: number;
        readonly last_audit_epoch: number;
    };
}

export interface IDependencyEdge {
    readonly id: EdgeUUID;
    readonly source: NodeUUID;
    readonly target: NodeUUID;
    readonly weight: number;
    readonly relation_type: 'DIRECT' | 'TRANSITIVE' | 'PEER';
}

export type OSINT_Telemetry_Event =
    | { type: 'NODE_UPDATE'; payload: Partial<ICoreGraphNode> & { id: NodeUUID } }
    | { type: 'PATHOGEN_ALERT'; payload: { node_id: NodeUUID; risk_level: 'CRITICAL' | 'HIGH'; vector: string } }
    | { type: 'SYSTEM_LOCKDOWN'; payload: { reason: string; timestamp: number } }
    | { type: 'HUD_SYNC'; payload: { v_sync_locked: boolean; frame_drift: number } };

export interface ITransactionalPayload<T> {
    readonly status: 'SUCCESS' | 'PARTIAL' | 'FAILURE';
    readonly epoch: number;
    readonly data: T;
    readonly checksum: string; // SHA-384
}

export const TYPE_PACING_CONSTANTS = {
    REDLINE: { depth: Infinity, parallel_checks: true },
    POTATO: { depth: 2, parallel_checks: false, lazy_resolution: true }
} as const;
