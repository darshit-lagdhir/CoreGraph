/**
 * COREGRAPH MASTER ENGINEERING SPECIFICATION: MODULE 12 - TASK 03
 * ADVANCED TOPOLOGICAL GENERIC HIERARCHIES: STRUCTURAL SOVEREIGNTY
 * Defines the connective tissue of the 3.88-million-node software ocean.
 */

import { NodeUUID, EdgeUUID } from './registry';

/**
 * ENodeType: Exhaustive discriminant for polymorphic node realization.
 */
export type ENodeType = 'PACKAGE' | 'MAINTAINER' | 'REPOSITORY' | 'NAMESPACE';

/**
 * TGraphNode: Polymorphic Node Atom.
 * Utilizes Gated Generics to ensure prototype-specific attribute integrity.
 */
export type TGraphNode<T extends ENodeType> = {
    readonly id: NodeUUID;
    readonly kind: T;
    readonly metadata: T extends 'PACKAGE'
        ? { readonly ecosystem: string; readonly manifest_hash: string }
        : T extends 'MAINTAINER'
        ? { readonly verified: boolean; readonly gpg_key_id: string }
        : { readonly raw_url: string };

    // Adjacency List (Flat-Packed Sovereignty)
    readonly edges: readonly EdgeUUID[];
};

/**
 * IDependencyEdge: Relational Tensor.
 * Strict directionality and relational weight.
 */
export interface IDependencyEdge {
    readonly id: EdgeUUID;
    readonly source: NodeUUID;
    readonly target: NodeUUID;
    readonly weight: number;
    readonly kind: 'DEPENDENCY' | 'MAINTENANCE' | 'CONTRIBUTION';
}

/**
 * ITransitivePath: Recursive Dependency Tree Schema.
 * Implements Depth-Quantized Type Self-Reference.
 */
export interface ITransitivePath {
    readonly node_id: NodeUUID;
    readonly depth: number;
    readonly parent_path: ITransitivePath | null; // Recursive Reference
}

/**
 * TOPOLOGY_PACING_GUARD: Hardware-Aware Structural Calibration.
 */
export const TOPOLOGY_PACING_CONSTANTS = {
    REDLINE: { max_check_depth: 500, eager_resolution: true },
    POTATO: { max_check_depth: 5, eager_resolution: false }
} as const;

/**
 * STRUCTURAL FIDELITY (F_str): Target 1.0 (Non-Repudiable Connectivity).
 */
export interface IStructuralAudit {
    readonly edges_sealed: number;
    readonly recursion_safety_ratio: 1.0;
    readonly traversal_latency: number;
}
