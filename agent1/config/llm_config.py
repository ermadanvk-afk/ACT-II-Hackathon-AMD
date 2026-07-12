import os
from dotenv import load_dotenv
from crewai import LLM

# Load .env from the project root (two levels up from this config/ folder)
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
load_dotenv(dotenv_path)

# Monkeypatch LLM.call to strip out 'cache_breakpoint'
# This completely bypasses CrewAI's buggy injection of this field!
_orig_call = LLM.call
def _patched_call(self, messages, *args, **kwargs):
    for m in messages:
        if isinstance(m, dict):
            m.pop('cache_breakpoint', None)
    return _orig_call(self, messages, *args, **kwargs)
LLM.call = _patched_call

# Use Fireworks via OpenAI-compatible endpoint (no LiteLLM needed).
# Passing provider="openai" explicitly bypasses CrewAI's model-constants validation
# and routes directly to the native OpenAI SDK pointed at Fireworks' base URL.
llm = LLM(
    model="accounts/fireworks/models/minimax-m3",
    provider="openai",
    api_key=os.getenv("FIREWORKS_API_KEY"),
    base_url="https://api.fireworks.ai/inference/v1"
)
