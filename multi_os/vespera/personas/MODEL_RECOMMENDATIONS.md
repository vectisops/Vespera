# Model Recommendations – Low Refusal / High Acceptance

Priority order for Vespera on the Raider (RTX 4090 Laptop 16 GB):

## Primary (best balance)
1. **Gemma 3 12B Abliterated** – `hf.co/mlabonne/gemma-3-12b-it-abliterated-GGUF:Q5_K_M`
   - Excellent instruction following, very low refusal, strong for both task and NSFW personas.
2. **Llama 3.1 8B Abliterated** – `hf.co/bartowski/Llama-3.1-8B-Instruct-abliterated-GGUF:Q5_K_M`
   - Fast, compliant, good fallback.

## Strong alternatives
- `dolphin-llama3:8b` (classic uncensored line, high acceptance)
- `qwen2.5:14b` (capable; some residual safety – prefer abliterated Qwen if available)
- Larger Hermes / Yi / Mixtral uncensored quants at Q3–Q4 if you want more capability and can accept slower tokens

## Guidance
- Prefer **abliterated / obliterated / uncensored** community quants over stock instruct models when running explicit or high-compliance personas.
- Q5_K_M is the quality/speed sweet spot on 16 GB for ~8–12B models.
- Keep one “clean” stock model only if you need it for specific non-sensitive tasks; otherwise standardise on the abliterated line so persona behaviour stays consistent.

Pull example (Ollama):
```bash
ollama pull hf.co/mlabonne/gemma-3-12b-it-abliterated-GGUF:Q5_K_M
```
