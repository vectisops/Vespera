# Vespera Expanded Tools

Optional capability packs. All degrade gracefully if backends are missing.

## Packs

### Media – image & video
| Tool | Backend |
|------|---------|
| `image.generate` | Automatic1111 SD WebUI API (`VESPERA_SD_URL`, default `http://127.0.0.1:7861`) |
| `video.generate` | ComfyUI workflow queue (`VESPERA_VIDEO_URL`, default `http://127.0.0.1:8188`) |

```bash
# A1111 must be started with --api
vespera tool image.generate -a "cyan neon raider laptop, dark room"

vespera tool video.generate --json '{"workflow_path":"workflows/animediff.json","prompt":"slow orbit"}'
```

### Voice
| Tool | Backend |
|------|---------|
| `voice.stt` | `faster-whisper` or whisper.cpp CLI |
| `voice.tts` | `piper` (set `VESPERA_PIPER_MODEL`) or Coqui `tts` |
| `voice.chat_turn` | STT → Ollama → TTS |

```bash
pip install faster-whisper
vespera tool voice.stt -a /path/to/clip.wav
vespera tool voice.tts -a "Systems nominal."
```

**Voice / video chat:** use `voice.chat_turn` as the core loop; camera capture + continuous duplex UI is a client feature (Android / desktop) on top of these tools—not a separate model server.

### Search
| Tool | Backend |
|------|---------|
| `search.web` | Local **SearXNG** if up, else DuckDuckGo HTML |

```bash
# Recommended: docker run searxng
export VESPERA_SEARXNG_URL=http://127.0.0.1:8080
vespera tool search.web -a "ollama abliterated gemma"
```

### Network diagnostics (defensive)
| Tool | Purpose |
|------|---------|
| `net.diag` | ping, DNS, routes, traceroute, local port probes |
| `net.forensics_light` | listeners, established sockets, resolv.conf, neighbours |

Authorized / own-network use only. No offensive exploit tooling is included.

```bash
vespera tool net.diag -a 192.168.1.1
vespera tool net.forensics_light
```

## Status

```bash
vespera tools
```

## Env summary

| Variable | Default | Purpose |
|----------|---------|----------|
| `VESPERA_SD_URL` | `http://127.0.0.1:7861` | A1111 / SD API |
| `VESPERA_SD_BACKEND` | `a1111` | `a1111` or `comfy` |
| `VESPERA_VIDEO_URL` | `http://127.0.0.1:8188` | ComfyUI |
| `VESPERA_SEARXNG_URL` | `http://127.0.0.1:8080` | Meta-search |
| `VESPERA_WHISPER_MODEL` | `base.en` | STT model id |
| `VESPERA_PIPER_MODEL` | _(empty)_ | Path to piper `.onnx` |
| `VESPERA_PIPER_BIN` | `piper` | piper executable |
