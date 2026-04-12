import requests
import sys

OLLAMA_URL = "http://localhost:11434"

def check_server():
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        r.raise_for_status()
        models = [m["name"] for m in r.json().get("models", [])]
        print(f"Ollama server is up. Models available: {models}")
        return models
    except Exception as e:
        print(f"Could not reach Ollama server: {e}")
        sys.exit(1)

def test_qwen(models):
    name = "qwen3-vl:4b"
    if not any(name in m for m in models):
        print(f"{name} not found in loaded models")
        return False
    try:
        r = requests.post(f"{OLLAMA_URL}/api/generate", json={
            "model": name,
            "prompt": "Reply with only the word PASS.",
            "stream": False
        }, timeout=60)
        r.raise_for_status()
        response = r.json().get("response", "")
        if response.strip():
            print(f"{name} responded: {response.strip()[:100]}")
            return True
        else:
            print(f"{name} returned empty response")
            return False
    except Exception as e:
        print(f"{name} test failed: {e}")
        return False

def test_nomic(models):
    name = "nomic-embed-text"
    if not any(name in m for m in models):
        print(f"{name} not found in loaded models")
        return False
    try:
        r = requests.post(f"{OLLAMA_URL}/api/embeddings", json={
            "model": name,
            "prompt": "test embedding"
        }, timeout=30)
        r.raise_for_status()
        embedding = r.json().get("embedding", [])
        if len(embedding) > 0:
            print(f"{name} returned embedding with {len(embedding)} dimensions")
            return True
        else:
            print(f"{name} returned empty embedding")
            return False
    except Exception as e:
        print(f"{name} test failed: {e}")
        return False

if __name__ == "__main__":
    print("=== Ollama Model Tests ===\n")
    models = check_server()

    results = []
    results.append(test_qwen(models))
    results.append(test_nomic(models))

    
    sys.exit(0 if all(results) else 1)