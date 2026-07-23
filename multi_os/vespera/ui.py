"""
Gradio-based Control Center for Vespera.
Works identically on Linux, macOS, and Windows.
"""

from __future__ import annotations

from typing import List, Tuple

import gradio as gr

from .config import (
    load_config,
    save_config,
    list_personas,
    load_persona,
    get_recommended_models,
    load_persona_meta,
)
from .hardware import scan_hardware
from .ollama_client import OllamaClient


def get_hardware_text() -> str:
    report = scan_hardware()
    d = report.to_dict()
    lines = [
        f"**OS:** {d['os']} ({d['arch']})",
        f"**CPU:** {d['cpu']['physical']} physical / {d['cpu']['logical']} logical cores",
        f"**RAM:** {d['ram_gb']['total']} GB total  |  {d['ram_gb']['available']} GB free  ({d['ram_gb']['used_percent']}% used)",
    ]
    if d["gpus"]:
        for g in d["gpus"]:
            lines.append(
                f"**GPU:** {g['name']}  |  {g['total_vram_mb']/1024:.1f} GB total  |  "
                f"{g['free_vram_mb']/1024:.1f} GB free"
            )
    else:
        lines.append("**GPU:** None detected (or non-NVIDIA)")
    rec = d["recommendation_12b"]
    lines.append(f"**12B quant advice:** budget ~{rec['budget_gb']} GB → **{rec['recommended']}**")
    if d["notes"]:
        lines.append("\n**Notes:**")
        for n in d["notes"]:
            lines.append(f"- {n}")
    return "\n".join(lines)


def get_installed_models() -> List[str]:
    cfg = load_config()
    client = OllamaClient(cfg.get("ollama_host", "http://127.0.0.1:11434"))
    if not client.is_available():
        return []
    models = client.list_models()
    names = []
    for m in models:
        name = m.get("name") or m.get("model")
        if name:
            names.append(name)
    return names


def build_model_choices(persona: str | None = None) -> List[str]:
    """
    Build the model dropdown list.

    - Always include models currently installed in Ollama.
    - Also include any recommended models for the selected persona
      (even if not yet pulled) so the user can see what to install.
    - Recommended models that are installed are listed first.
    """
    installed = get_installed_models()
    recommended = get_recommended_models(persona) if persona else []

    # Preserve order: recommended-and-installed → other installed → recommended-not-installed
    ordered: List[str] = []
    seen = set()

    for m in recommended:
        if m in installed and m not in seen:
            ordered.append(m)
            seen.add(m)

    for m in installed:
        if m not in seen:
            ordered.append(m)
            seen.add(m)

    for m in recommended:
        if m not in seen:
            ordered.append(f"{m}  (recommended – not installed)")
            seen.add(m)

    if not ordered:
        ordered = ["(Ollama not reachable / no models)"]
    return ordered


def format_recommendation_text(persona: str) -> str:
    meta = load_persona_meta(persona)
    recs = get_recommended_models(persona)
    if not recs and not meta:
        return "_No specific model recommendation for this persona yet._"

    lines = []
    if recs:
        lines.append("**Recommended models:**")
        installed = set(get_installed_models())
        for m in recs:
            mark = "✅" if m in installed else "⬇️ not installed"
            lines.append(f"- `{m}`  {mark}")

    if meta.get("min_vram_gb"):
        lines.append(f"\n**Min VRAM guidance:** ~{meta['min_vram_gb']} GB")
    if meta.get("notes"):
        lines.append(f"\n**Notes:** {meta['notes']}")

    return "\n".join(lines)


def chat_fn(message: str, history: List[Tuple[str, str]], model: str, persona: str):
    if not message.strip():
        return history, ""

    # Strip the " (recommended – not installed)" suffix if present
    if model and " (recommended" in model:
        model = model.split(" (recommended")[0].strip()

    cfg = load_config()
    try:
        system = load_persona(persona)
    except Exception as e:
        history = history + [(message, f"Error loading persona: {e}")]
        return history, ""

    client = OllamaClient(cfg.get("ollama_host", "http://127.0.0.1:11434"))
    if not client.is_available():
        history = history + [(message, "Ollama is not reachable. Start `ollama serve` first.")]
        return history, ""

    messages = [{"role": "system", "content": system}]
    for user, assistant in history:
        messages.append({"role": "user", "content": user})
        messages.append({"role": "assistant", "content": assistant})
    messages.append({"role": "user", "content": message})

    try:
        resp = client.chat(model=model, messages=messages, stream=False)
        if isinstance(resp, dict):
            content = resp.get("message", {}).get("content") or resp.get("response") or str(resp)
        else:
            content = str(resp)
    except Exception as e:
        content = f"Error talking to Ollama: {e}"

    history = history + [(message, content)]
    return history, ""


def on_persona_change(persona: str):
    """Update recommendation text + model dropdown when persona changes."""
    rec_text = format_recommendation_text(persona)
    choices = build_model_choices(persona)
    # Prefer the first recommended model that is installed, else first choice
    value = choices[0] if choices else None
    recs = get_recommended_models(persona)
    installed = set(get_installed_models())
    for m in recs:
        if m in installed:
            value = m
            break
    return rec_text, gr.update(choices=choices, value=value)


def build_ui():
    cfg = load_config()
    persona_names = sorted(list_personas().keys()) or ["pure_logic"]
    active = cfg.get("active_persona", persona_names[0])
    if active not in persona_names:
        active = persona_names[0]

    initial_models = build_model_choices(active)
    initial_rec = format_recommendation_text(active)

    with gr.Blocks(
        title="Vespera Control Center",
        theme=gr.themes.Soft(primary_hue="cyan", neutral_hue="slate"),
        css="""
        .gradio-container { max-width: 1100px !important; }
        """,
    ) as demo:
        gr.Markdown(
            """
            # ⚡ Vespera Control Center
            Multi-OS Local AI Operator Stack  
            *Hardware prescan · Modular personas · Ollama backend*
            """
        )

        with gr.Tab("Chat"):
            with gr.Row():
                persona_dd = gr.Dropdown(
                    choices=persona_names,
                    value=active,
                    label="Persona",
                )
                model_dd = gr.Dropdown(
                    choices=initial_models,
                    value=initial_models[0] if initial_models else None,
                    label="Model",
                    allow_custom_value=True,
                )

            rec_md = gr.Markdown(initial_rec)

            persona_dd.change(
                on_persona_change,
                inputs=[persona_dd],
                outputs=[rec_md, model_dd],
            )

            chatbot = gr.Chatbot(height=480, label="Conversation")
            msg = gr.Textbox(placeholder="Message Vespera…", label="Input", lines=2)
            with gr.Row():
                send_btn = gr.Button("Send", variant="primary")
                clear_btn = gr.Button("Clear")

            send_btn.click(
                chat_fn,
                inputs=[msg, chatbot, model_dd, persona_dd],
                outputs=[chatbot, msg],
            )
            msg.submit(
                chat_fn,
                inputs=[msg, chatbot, model_dd, persona_dd],
                outputs=[chatbot, msg],
            )
            clear_btn.click(lambda: ([], ""), outputs=[chatbot, msg])

        with gr.Tab("Hardware Prescan"):
            hw_md = gr.Markdown(get_hardware_text())
            refresh_btn = gr.Button("Refresh Scan")
            refresh_btn.click(get_hardware_text, outputs=hw_md)

        with gr.Tab("Status & Config"):
            status_md = gr.Markdown("Loading…")

            def refresh_status():
                c = load_config()
                client = OllamaClient(c.get("ollama_host", "http://127.0.0.1:11434"))
                ok = client.is_available()
                models = get_installed_models() if ok else []
                text = (
                    f"**Ollama reachable:** {'✅ Yes' if ok else '❌ No'}\n\n"
                    f"**Active persona:** `{c.get('active_persona')}`\n\n"
                    f"**Default model:** `{c.get('default_model')}`\n\n"
                    f"**Configured host:** `{c.get('ollama_host')}`\n\n"
                    f"**Models visible:** {', '.join(models[:12]) if models else 'none'}"
                )
                return text

            status_md.value = refresh_status()
            gr.Button("Refresh Status").click(refresh_status, outputs=status_md)

            gr.Markdown("### Quick config write")
            new_persona = gr.Dropdown(choices=persona_names, label="Set active persona")
            new_model = gr.Textbox(label="Set default model name", value=cfg.get("default_model", ""))
            save_btn = gr.Button("Save Config")

            def save_cfg(p, m):
                c = load_config()
                if p:
                    c["active_persona"] = p
                if m:
                    c["default_model"] = m
                save_config(c)
                return refresh_status()

            save_btn.click(save_cfg, inputs=[new_persona, new_model], outputs=status_md)

        gr.Markdown(
            f"<center><small>Vespera multi-OS · Python + Gradio · Works on Linux / macOS / Windows</small></center>"
        )

    return demo


def main():
    demo = build_ui()
    demo.launch(server_name="127.0.0.1", server_port=7860, share=False)


if __name__ == "__main__":
    main()
