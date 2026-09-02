"""
Gemini Enterprise API Client Adapter.
Provides robust calling interface with auto-fallback, JSON mode, and retry mechanics.
"""

import os
import json
import time
import requests
from typing import Dict, Any, List, Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

DEFAULT_MODELS = [
    "gemini-2.5-flash",
    "gemini-flash-latest",
    "gemini-2.5-flash-lite",
    "gemini-2.5-pro",
]
MAX_RETRIES = 3
INITIAL_BACKOFF_SEC = 1.0


class GeminiClient:
    """Enterprise client for Google Gemini platform with resilient fallback."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        preferred_model: str = "gemini-2.5-flash",
        timeout: int = 30,
    ) -> None:
        self.api_key = (
            api_key
            or os.environ.get("GEMINI_API_KEY")
            or os.environ.get("GOOGLE_API_KEY")
            or ""
        )
        self.preferred_model = preferred_model
        self.timeout = timeout
        self.session = requests.Session()

    def generate(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        json_mode: bool = False,
        temperature: float = 0.2,
    ) -> Dict[str, Any]:
        """Generate content from Gemini with auto-fallback across model candidates."""
        models_to_try = [self.preferred_model] + [
            m for m in DEFAULT_MODELS if m != self.preferred_model
        ]
        last_error = "No models available"

        for model in models_to_try:
            res = self._call_model(
                model=model,
                prompt=prompt,
                system_instruction=system_instruction,
                json_mode=json_mode,
                temperature=temperature,
            )
            if res.get("status") == "SUCCESS":
                return res
            last_error = res.get("error", "Unknown error")

        return {"status": "FAIL", "error": f"All candidate models failed. Last error: {last_error}"}

    def _call_model(
        self,
        model: str,
        prompt: str,
        system_instruction: Optional[str],
        json_mode: bool,
        temperature: float,
    ) -> Dict[str, Any]:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.api_key}"
        payload: Dict[str, Any] = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": 2048,
            },
        }
        if json_mode:
            payload["generationConfig"]["responseMimeType"] = "application/json"
        if system_instruction:
            payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}

        backoff = INITIAL_BACKOFF_SEC
        for attempt in range(MAX_RETRIES):
            start_time = time.time()
            try:
                r = self.session.post(url, json=payload, timeout=self.timeout)
                elapsed_ms = int((time.time() - start_time) * 1000)
                if r.status_code == 200:
                    data = r.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                        usage = data.get("usageMetadata", {})
                        return {
                            "status": "SUCCESS",
                            "model_used": model,
                            "latency_ms": elapsed_ms,
                            "text": text,
                            "usage": usage,
                        }
                if r.status_code in [429, 503]:
                    time.sleep(backoff)
                    backoff *= 2
                    continue
                return {"status": "FAIL", "model": model, "error": f"HTTP {r.status_code}: {r.text[:150]}"}
            except Exception as e:
                return {"status": "ERROR", "model": model, "error": str(e)}

        return {"status": "FAIL", "model": model, "error": f"Max retries exceeded for {model}"}
