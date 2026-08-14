-- ============================================================================
-- AfriGround — Database Init Script
-- Runs on first container creation via docker-entrypoint-initdb.d
-- ============================================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";       -- trigram search for satellite names
CREATE EXTENSION IF NOT EXISTS "btree_gist";    -- exclusion constraints for scheduling
