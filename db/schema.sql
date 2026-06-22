CREATE EXTENSION IF NOT EXISTS vector;

CREATE TYPE image_status AS ENUM ('pending', 'vision_done', 'embedding_done', 'grouping_done', 'failed' );

CREATE TABLE IF NOT EXISTS workflow_sets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    label TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    screenshot_count INTEGER DEFAULT 1,
    user_id TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS screenshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    image_url TEXT NOT NULL,
    description TEXT,
    embedding VECTOR(768),
    workflow_set_id UUID,
    processed_at TIMESTAMP DEFAULT NOW(),
    status image_status DEFAULT 'pending',
    user_id TEXT NOT NULL
);

ALTER TABLE workflow_sets ENABLE ROW LEVEL SECURITY;
ALTER TABLE screenshots ENABLE ROW LEVEL SECURITY;


