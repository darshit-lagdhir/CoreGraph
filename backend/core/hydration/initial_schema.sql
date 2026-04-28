-- SECTOR KAPPA: SUPABASE INITIAL SCHEMA
-- Provides the topological substrate for the CoreGraph Cloud Preview.

-- 1. Nodes Table: Stores high-entropy forensic metadata and spatial vectors.
CREATE TABLE IF NOT EXISTS nodes (
    id TEXT PRIMARY KEY,
    metadata JSONB,
    topology_vector FLOAT8[], -- 3D Spectral Coordinates
    risk_weight FLOAT8 DEFAULT 0.0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Edges Table: Stores the sinew of the hadronic core (relationships).
CREATE TABLE IF NOT EXISTS edges (
    id SERIAL PRIMARY KEY,
    source_id TEXT REFERENCES nodes(id) ON DELETE CASCADE,
    target_id TEXT REFERENCES nodes(id) ON DELETE CASCADE,
    weight FLOAT8 DEFAULT 1.0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Clean Slate Protocol
TRUNCATE nodes CASCADE;

-- 3. Performance Indexes: Optimized for 144Hz query performance (Sector Theta).
CREATE INDEX IF NOT EXISTS idx_nodes_risk_weight ON nodes(risk_weight DESC);
CREATE INDEX IF NOT EXISTS idx_edges_source_target ON edges(source_id, target_id);
