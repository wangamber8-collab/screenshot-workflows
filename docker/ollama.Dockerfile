FROM ollama/ollama:latest

RUN ollama serve & sleep 5 && \
    ollama pull qwen3-vl:4b && \
    ollama pull nomic-embed-text