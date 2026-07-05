# Screenshot Processing Pipeline

An automated pipeline that processes screenshots as they are uploaded — generating descriptions, embeddings, and grouping them into workflow clusters.

## Components

1. **Vision** — sends the screenshot to a vision model (qwen3-vl) and generates a description
2. **Embedding** — generates a vector embedding from the description using nomic-embed-text
3. **Grouping** — compares the embedding against existing workflow groups and assigns the screenshot to the most similar one, or creates a new group if none match

Each stage runs independently and communicates through Redis queues, so multiple screenshots can be in different stages of the pipeline simultaneously.

## Requirements
- Docker
- Supabase Project

### Database

1. Run `db/schema.sql` in the Supabase SQL Editor
2. Run `db/match_cluster.sql` in the Supabase SQL Editor
3. Deploy `db/index.ts` as a Supabase edge function and connect it to a storage webhook
4. Deploy `db/delete.ts` as a Supabase edge function

### Environment Variables

Create a `.env` file at the project root with the variables as specified by the .env.example file

Add `WEBHOOK_SECRET` and the deployed API URL as secrets in Supabase under Project Settings → Edge Functions → Secrets.

### Running Locally (Docker)

```bash
docker compose up
```

If code was changed since the last run:

```bash
docker compose up --build
```

The first run will download the Ollama models, which may take several minutes.
```