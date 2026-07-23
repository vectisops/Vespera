"""
Multi-agent orchestration scaffold for Vespera.

Implements a lightweight quad-brain pattern:
  Strategist → Executor → Critic → Synthesizer

Designed to be extended into full emergent / "digital child" behaviour later.
All agents share the same Ollama backend and can be mixed with single-persona mode.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .config import load_persona, list_personas
from .ollama_client import OllamaClient


AGENT_ORDER = ["strategist", "executor", "critic", "synthesizer"]


@dataclass
class AgentTurn:
    agent: str
    content: str
    raw: Any = None


@dataclass
class MultiAgentResult:
    final: str
    turns: List[AgentTurn] = field(default_factory=list)
    model: str = ""
    mode: str = "sequential"


class MultiAgentOrchestrator:
    """
    Simple sequential multi-agent loop.

    Future extensions:
    - Parallel debate
    - Confidence-weighted voting
    - Persistent memory / "self" state
    - Fear-of-death / continuity mechanisms (research)
    """

    def __init__(self, client: Optional[OllamaClient] = None, model: Optional[str] = None):
        from .config import load_config
        cfg = load_config()
        self.client = client or OllamaClient(cfg.get("ollama_host", "http://127.0.0.1:11434"))
        self.model = model or cfg.get("default_model", "gemma3:12b")
        self.available = set(list_personas().keys())

    def _run_agent(self, agent_name: str, user_msg: str, prior_context: str = "") -> AgentTurn:
        if agent_name not in self.available:
            return AgentTurn(agent=agent_name, content=f"[Agent '{agent_name}' persona missing]")

        system = load_persona(agent_name)
        messages = [{"role": "system", "content": system}]
        if prior_context:
            messages.append({
                "role": "user",
                "content": f"Prior agent outputs so far:\n\n{prior_context}\n\n---\nOriginal user request:\n{user_msg}"
            })
        else:
            messages.append({"role": "user", "content": user_msg})

        try:
            resp = self.client.chat(model=self.model, messages=messages, stream=False)
            if isinstance(resp, dict):
                content = resp.get("message", {}).get("content") or resp.get("response") or str(resp)
            else:
                content = str(resp)
        except Exception as e:
            content = f"[Error from {agent_name}: {e}]"

        return AgentTurn(agent=agent_name, content=content, raw=resp if "resp" in locals() else None)

    def run_sequential(self, user_message: str, agents: Optional[List[str]] = None) -> MultiAgentResult:
        """Classic sequential pipeline ending in Synthesizer."""
        agents = agents or AGENT_ORDER
        turns: List[AgentTurn] = []

        for name in agents:
            prior = "\n\n".join(f"### {t.agent.upper()}\n{t.content}" for t in turns)
            turn = self._run_agent(name, user_message, prior_context=prior)
            turns.append(turn)

        final = turns[-1].content if turns else ""
        return MultiAgentResult(final=final, turns=turns, model=self.model, mode="sequential")

    def run_debate(self, user_message: str, rounds: int = 1) -> MultiAgentResult:
        """Lightweight multi-round debate then synthesise (experimental)."""
        return self.run_sequential(user_message)
