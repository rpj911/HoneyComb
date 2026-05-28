import json
import logging
import requests

logger = logging.getLogger(__name__)


class LLMClient(object):

    def __init__(self, base_url, model, timeout=120):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self._chat_url = "{}/api/chat".format(self.base_url)

    def chat(self, messages, temperature=0.2, max_tokens=2048):
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }
        logger.debug("LLM request: %s", json.dumps(payload, ensure_ascii=False)[:300])
        try:
            resp = requests.post(self._chat_url, json=payload, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            content = data["message"]["content"]
            logger.debug("LLM response: %s", content[:200])
            return content
        except requests.RequestException as e:
            logger.error("LLM request failed: %s", e)
            raise

    def chat_once(self, system_prompt, user_prompt, **kwargs):
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        return self.chat(messages, **kwargs)
