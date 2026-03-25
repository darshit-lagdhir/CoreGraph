-- ==============================================================================
-- COREGRAPH PERSISTENCE KERNEL: FOUNDATION (Task 020-027)
-- ==============================================================================

-- 1. ATOMIC EXTENSIONS
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "cube";
CREATE EXTENSION IF NOT EXISTS "earthdistance";

-- 2. THE TOTAL PERSISTENCE BUILD
CREATE TABLE IF NOT EXISTS author_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email_hash VARCHAR(64) NOT NULL,
    display_name VARCHAR(255),
    github_id VARCHAR(128),
    global_reputation_score FLOAT DEFAULT 0.0,
    is_verified_maintainer BOOLEAN DEFAULT false,
    identity_metadata JSONB DEFAULT '{}',
    first_seen_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS packages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ecosystem VARCHAR(32) NOT NULL,
    name VARCHAR(255) NOT NULL,
    version_latest VARCHAR(64),
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(ecosystem, name)
);

CREATE TABLE IF NOT EXISTS package_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    package_id UUID REFERENCES packages(id) ON DELETE CASCADE,
    version_string VARCHAR(128) NOT NULL,
    metadata_extra JSONB,
    release_date TIMESTAMPTZ DEFAULT now(),
    UNIQUE(package_id, version_string)
);

CREATE TABLE IF NOT EXISTS dependency_edges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parent_version_id UUID REFERENCES package_versions(id) ON DELETE CASCADE,
    child_package_id UUID REFERENCES packages(id) ON DELETE CASCADE,
    specifier VARCHAR(128) NOT NULL
);

CREATE TABLE IF NOT EXISTS risk_scoring_index (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    package_id UUID REFERENCES packages(id) ON DELETE CASCADE,
    risk_score FLOAT NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT now()
);
