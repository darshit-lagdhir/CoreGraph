-- backend/database/migrations/003_search_optimization.sql
-- ==============================================================================
-- 1. DETERMINISTIC PURL HASHING (Task 009)
-- ==============================================================================
ALTER TABLE packages ADD COLUMN IF NOT EXISTS purl_hash BIGINT;
ALTER TABLE package_versions ADD COLUMN IF NOT EXISTS dependency_ids INTEGER[];

CREATE INDEX IF NOT EXISTS idx_packages_purl_hash ON packages (purl_hash);
CREATE INDEX IF NOT EXISTS idx_packages_name_btree ON packages (name);
CREATE INDEX IF NOT EXISTS idx_packages_name_trgm ON packages USING gin (name gin_trgm_ops);

-- TRIGGER-BASED STATE MATERIALIZATION
CREATE OR REPLACE FUNCTION sync_graph_state() RETURNS TRIGGER AS $$
BEGIN
    NEW.purl_hash := hashtext(NEW.ecosystem || '/' || NEW.name);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_packages_hash_sync ON packages;
CREATE TRIGGER trg_packages_hash_sync
BEFORE INSERT OR UPDATE ON packages
FOR EACH ROW EXECUTE FUNCTION sync_graph_state();
