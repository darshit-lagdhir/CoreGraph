-- backend/dal/migrations/triggers/v1_native_triggers.sql

-- ==============================================================================
-- 1. THE MASTER METADATA HEARTBEAT
-- ==============================================================================
-- This function is designed to be highly efficient, minimizing CPU cycles
-- by utilizing the internal CLOCK_TIMESTAMP() of the PG kernel.

CREATE OR REPLACE FUNCTION fn_update_last_modified()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CLOCK_TIMESTAMP();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- BINDING THE TRIGGER TO FOUNDATIONAL TABLES
-- We apply this to 'packages' and 'maintainer_metrics' as a baseline.
DROP TRIGGER IF EXISTS tr_packages_last_modified ON packages;
CREATE TRIGGER tr_packages_last_modified
BEFORE UPDATE ON packages
FOR EACH ROW
EXECUTE FUNCTION fn_update_last_modified();

DROP TRIGGER IF EXISTS tr_maintainer_metrics_last_modified ON maintainer_metrics;
CREATE TRIGGER tr_maintainer_metrics_last_modified
BEFORE UPDATE ON maintainer_metrics
FOR EACH ROW
EXECUTE FUNCTION fn_update_last_modified();

-- ==============================================================================
-- 2. THE HIGH-VELOCITY RISK SENTINEL (Task 022)
-- ==============================================================================
-- This function identifies a state transition from 'Yellow' to 'Red'.
-- CROSS-REFERENCE: Task 022 (Graph Alerting).

CREATE OR REPLACE FUNCTION fn_risk_threshold_sentinel()
RETURNS TRIGGER AS $$
BEGIN
    -- Only trigger if the new risk score exceeds the critical threshold
    -- and the previous score was below it. This prevents 'Notification Storms'.
    IF (NEW.risk_score >= 0.9 AND (OLD.risk_score < 0.9 OR OLD.risk_score IS NULL)) THEN
        PERFORM pg_notify('risk_threshold_breach',
            json_build_object(
                'package_id', NEW.package_id,
                'r_idx', NEW.risk_score,
                'previous_idx', OLD.risk_score,
                'timestamp', CLOCK_TIMESTAMP()
            )::text
        );
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS tr_risk_sentinel_alert ON risk_scoring_index;
CREATE TRIGGER tr_risk_sentinel_alert
AFTER UPDATE ON risk_scoring_index
FOR EACH ROW
EXECUTE FUNCTION fn_risk_threshold_sentinel();
