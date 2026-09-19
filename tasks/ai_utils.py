"""
Thin wrapper around the Groq API for AI-assisted task planning.

Kept in its own module (rather than inline in views.py) so it's easy to:
  - unit test in isolation (mock this function, don't hit the real API in tests)
  - swap providers later without touching view/serializer code
"""
import json
import os
from groq import Groq
from django.conf import settings

_client = None


def get_client():
    global _client
    if _client is None:
        _client = Groq(api_key=settings.GROQ_API_KEY)
    return _client


def suggest_priority_and_subtasks(title: str, description: str) -> dict:
    """
    Given a task's title/description, ask the LLM for a suggested priority
    and a short breakdown of subtasks. Returns a dict; falls back to a safe
    default if the API call or JSON parsing fails, so a flaky network call
    never 500s the endpoint.
    """
    prompt = (
        "You are a project management assistant. Given a task, respond with "
        "ONLY valid JSON (no markdown fences) in this exact shape:\n"
        '{"priority": "LOW|MEDIUM|HIGH", "subtasks": ["...", "..."]}\n\n'
        f"Task title: {title}\n"
        f"Task description: {description or '(no description provided)'}"
    )

    try:
        client = get_client()
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        content = response.choices[0].message.content.strip()
        return json.loads(content)
    except Exception as exc:  # noqa: BLE001 - deliberately broad: any AI failure should degrade gracefully
        return {
            "priority": "MEDIUM",
            "subtasks": [],
            "error": f"AI suggestion unavailable: {exc}",
        }
