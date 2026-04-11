-- backend/dal/migrations/triggers/v1_native_triggers.sql

-- ==============================================================================
-- 1. THE MASTER METADATA HEARTBEAT
-- ==============================================================================

CREATE OR REPLACE FUNCTION fn_update_last_modified()
RETURNS TRIGGER AS $BODY$
BEGIN
    NEW.updated_at = CLOCK_TIMESTAMP();
    RETURN NEW;
END;
$BODY$ LANGUAGE plpgsql;

-- SPLIT --

DROP TRIGGER IF EXISTS tr_packages_last_modified ON packages;

-- SPLIT --

CREATE TRIGGER tr_packages_last_modified
BEFORE UPDATE ON packages
FOR EACH ROW
EXECUTE FUNCTION fn_update_last_modified();

-- SPLIT --

DROP TRIGGER IF EXISTS tr_maintainer_metrics_last_modified ON maintainer_metrics;

-- SPLIT --

CREATE TRIGGER tr_maintainer_metrics_last_modified
BEFORE UPDATE ON maintainer_metrics
FOR EACH ROW
EXECUTE FUNCTION fn_update_last_modified();

-- SPLIT --

-- ==============================================================================
-- 2. THE HIGH-VELOCITY RISK SENTINEL (Task 022)
-- ==============================================================================

CREATE OR REPLACE FUNCTION fn_risk_threshold_sentinel()
RETURNS TRIGGER AS $BODY$
BEGIN
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
$BODY$ LANGUAGE plpgsql;

-- SPLIT --

DROP TRIGGER IF EXISTS tr_risk_sentinel_alert ON risk_scoring_index;

-- SPLIT --

CREATE TRIGGER tr_risk_sentinel_alert
AFTER UPDATE ON risk_scoring_index
FOR EACH ROW
EXECUTE FUNCTION fn_risk_threshold_sentinel();
