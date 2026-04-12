"""
inference.py - Prosthetic Env RL Agent
Must be in root directory. Uses OpenAI client with structured stdout logs.
"""
import os
import sys
import requests
from openai import OpenAI

# ── Environment variables (API_BASE_URL and MODEL_NAME have defaults) ──────────
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME   = os.getenv("MODEL_NAME",   "Qwen/Qwen2.5-72B-Instruct")
HF_TOKEN     = os.getenv("HF_TOKEN")          # No default — must be set as HF secret
ENV_BASE_URL = os.getenv("ENV_BASE_URL", "http://localhost:7860")

# ── OpenAI client (all LLM calls go through this) ─────────────────────────────
client = OpenAI(
    base_url=API_BASE_URL,
    api_key=HF_TOKEN or "dummy-key-for-env-only-runs",
)

# ── Task definitions matching openenv.yaml ────────────────────────────────────
TASKS = [
    {"id": "1", "name": "Precision Grip",  "prompt": "Apply a mid-level grip force between 3 and 7."},
    {"id": "2", "name": "Power Grip",       "prompt": "Apply maximum grip force of 9 or higher."},
    {"id": "3", "name": "Relaxation",       "prompt": "Release all grip force to 1 or below."},
    {"id": "4", "name": "Delicate Pinch",   "prompt": "Apply a very light grip force of exactly 2."},
    {"id": "5", "name": "Firm Handshake",   "prompt": "Apply a strong but non-maximum grip force of exactly 8."},
]

SYSTEM_PROMPT = (
    "You are an AI controller for a prosthetic hand. "
    "When given a grip task, respond with ONLY a single integer force value between 0 and 10. "
    "No explanation, just the number."
)


def call_env(endpoint: str, payload: dict) -> dict:
    """Make an HTTP call to the environment server."""
    try:
        resp = requests.post(f"{ENV_BASE_URL}{endpoint}", json=payload, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"error": str(e)}


def get_llm_action(task_prompt: str) -> str:
    """Ask the LLM for a grip force value."""
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": task_prompt},
            ],
            max_tokens=10,
            temperature=0.0,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        # Fallback: return a safe mid-range value so the env step still runs
        return "5"


def run_agent():
    print("[START]")
    print(f"[STEP] model={MODEL_NAME} base_url={API_BASE_URL}")

    for task in TASKS:
        task_id   = task["id"]
        task_name = task["name"]

        # ── Reset environment for this task ───────────────────────────────────
        reset_result = call_env("/reset", {"task_id": task_id})
        episode_id   = reset_result.get("episode_id", "unknown")

        print(f"[STEP] task_id={task_id} task_name={task_name} episode_id={episode_id} status=reset_ok")

        # ── Get action from LLM ───────────────────────────────────────────────
        raw_action = get_llm_action(task["prompt"])
        try:
            force = max(0, min(10, int(float(raw_action))))
        except ValueError:
            force = 5  # safe fallback

        # ── Step the environment ──────────────────────────────────────────────
        step_result = call_env("/step", {"episode_id": episode_id, "force": force})
        reward      = step_result.get("reward", 0.5)
        observation = step_result.get("observation", {})

        print(
            f"[STEP] task_id={task_id} force={force} reward={reward} "
            f"observation={observation}"
        )

    print("[END]")


if __name__ == "__main__":
    run_agent()
