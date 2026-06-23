CREATE OR REPLACE FUNCTION match_cluster (
  new_embedding VECTOR(768),
  match_user_id TEXT,
  threshold FLOAT
)
RETURNS TABLE(id UUID, screenshot_count INT, centroid VECTOR(768))
LANGUAGE SQL
AS $$
  SELECT id, screenshot_count, centroid
  FROM workflow_sets
  WHERE user_id = match_user_id
    AND centroid IS NOT NULL
    AND 1 - (centroid <=> new_embedding) >= threshold
  ORDER BY centroid <=> new_embedding
  LIMIT 1;
$$;