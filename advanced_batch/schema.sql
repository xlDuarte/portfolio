-- SQLite JSON1-backed event store. All events are synthetic in this lab.
-- Schema created automatically by advanced_batch.engine.connect().
CREATE TABLE IF NOT EXISTS events (
    event_id TEXT PRIMARY KEY,
    project_id INTEGER NOT NULL,
    sequence INTEGER NOT NULL,
    occurred_at TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    origin TEXT NOT NULL,
    UNIQUE(project_id,sequence)
);
CREATE INDEX IF NOT EXISTS events_project_seq ON events(project_id,sequence);
-- Analytical query used by case #100:
SELECT json_extract(payload_json,'$.line') AS line,
       SUM(json_extract(payload_json,'$.good_units')) AS good_units,
       SUM(json_extract(payload_json,'$.planned_min')) AS planned_min,
       SUM(json_extract(payload_json,'$.good_units') * json_extract(payload_json,'$.ideal_cycle_min')) AS ideal_good_min
FROM events WHERE project_id=100 GROUP BY line ORDER BY line;
