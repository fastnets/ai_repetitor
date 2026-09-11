"""Compare latency of OpenAI-compatible models using environment credentials."""

import json
import os
import sys
import time
from uuid import uuid4

import httpx


def main():
    endpoint = os.getenv("AI_API_URL") or os.getenv("LLM_BASE_URL")
    key = os.getenv("AI_API_KEY") or os.getenv("LLM_API_KEY")
    if not endpoint or not key:
        raise SystemExit("Set AI_API_URL/AI_API_KEY (or LLM equivalents)")
    if not endpoint.endswith("/chat/completions"):
        endpoint = endpoint.rstrip("/") + "/chat/completions"
    models = sys.argv[1:] or [os.getenv("AI_MODEL") or os.getenv("LLM_MODEL")]
    messages = [
        {
            "role": "system",
            "content": "Ты краткий репетитор математики 3 класса. Ответь одним коротким вопросом, без решения.",
        },
        {
            "role": "user",
            "content": "В коробке было 24 карандаша, 7 отдали. Сколько осталось?",
        },
    ]
    results = []
    with httpx.Client(timeout=90) as client:
        for model in models:
            started = time.perf_counter()
            response = client.post(
                endpoint,
                headers={"Authorization": f"Bearer {key}", "x-opencode-session": str(uuid4())},
                json={"model": model, "messages": messages, "temperature": 0.2, "max_tokens": 220},
            )
            elapsed = round(time.perf_counter() - started, 2)
            answer = None
            if response.is_success:
                answer = response.json()["choices"][0]["message"]["content"]
            results.append(
                {
                    "model": model,
                    "status": response.status_code,
                    "seconds": elapsed,
                    "response_chars": len(response.text),
                    "answer": answer,
                }
            )
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
