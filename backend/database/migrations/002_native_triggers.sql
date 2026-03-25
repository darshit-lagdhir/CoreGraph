-- backend/database/migrations/002_native_triggers.sql
-- ==============================================================================
-- 1. THE MASTER METADATA HEARTBEAT
-- ==============================================================================
CREATE OR REPLACE FUNCTION fn_update_last_modified()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CLOCK_TIMESTAMP();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS tr_packages_last_modified ON packages;
CREATE TRIGGER tr_packages_last_modified
BEFORE UPDATE ON packages
FOR EACH ROW EXECUTE FUNCTION fn_update_last_modified();
