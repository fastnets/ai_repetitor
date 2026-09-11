import logging

import httpx


logger = logging.getLogger(__name__)


class LLMError(RuntimeError):
    pass


class OpenAICompatibleClient:
    def __init__(
        self,
        base_url: str,
        api_key: str,
        model: str,
        timeout: float = 45,
        max_tokens: int = 250,
        disable_thinking: bool = True,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.max_tokens = max_tokens
        self.disable_thinking = disable_thinking
        self.client = httpx.Client(timeout=timeout)

    def chat(self, messages: list[dict], session_id: str | None = None) -> str:
        if not self.api_key:
            raise LLMError("LLM_API_KEY не настроен на сервере")
        endpoint = (
            self.base_url
            if self.base_url.endswith("/chat/completions")
            else f"{self.base_url}/chat/completions"
        )
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "User-Agent": "ai-tutor/0.1",
        }
        if session_id and "opencode.ai" in endpoint:
            headers["x-opencode-session"] = session_id
        try:
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.35,
                "max_tokens": self.max_tokens,
            }
            if self.disable_thinking and self.model.startswith("deepseek-"):
                payload["thinking"] = {"type": "disabled"}
            response = self.client.post(
                endpoint,
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            if not content or not content.strip():
                logger.warning("LLM provider returned an empty assistant message: %s", response.text[:500])
                raise LLMError("Модель вернула пустой ответ")
            return content.strip()
        except httpx.HTTPStatusError as exc:
            provider_detail = exc.response.text[:500].replace("\n", " ")
            logger.warning("LLM provider rejected request (%s): %s", exc.response.status_code, provider_detail)
            raise LLMError(
                f"Сервис модели отклонил запрос (код {exc.response.status_code}). Проверьте ключ, модель и баланс."
            ) from exc
        except (httpx.HTTPError, KeyError, IndexError, TypeError) as exc:
            raise LLMError(f"Ошибка LLM API: {exc}") from exc

    def close(self):
        self.client.close()
