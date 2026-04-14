CREATE EXTENSION IF NOT EXISTS vector;

CREATE TYPE image_status AS ENUM ('pending', 'vision_done', 'embedding_done', 'grouping_done', 'failed' )

CREATE TABLE IF NOT EXISTS workflow_sets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    label TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    screenshot_count INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS screenshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    image_url TEXT NOT NULL,
    image_data TEXT,
    description TEXT,
    embedding VECTOR(768),
    workflow_set_id UUID REFERENCES workflow_sets(id),
    processed_at TIMESTAMP DEFAULT NOW(),
    status image_status DEFAULT 'pending'
);

ALTER TABLE workflow_sets ENABLE ROW LEVEL SECURITY;
ALTER TABLE screenshots ENABLE ROW LEVEL SECURITY;


