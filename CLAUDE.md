# Anonymize - Project Context

## Overview
Desktop app for anonymizing Swiss documents using Microsoft Presidio. Three-layer architecture: Vue frontend + Tauri shell + Python sidecar.

## Quick Commands

```bash
# Development (full app)
npm run tauri dev

# Development (API only)
~/.local/bin/uv run --project src-python uvicorn anonymize_api.main:app --port 14200

# Build Python sidecar (must do first)
~/.local/bin/uv run --project src-python python src-python/build.py

# Build production app
npm run tauri build

# Output: src-tauri/target/release/bundle/macos/Anonymize.app
```

## Architecture

```
Frontend (Vue/TS)  <-->  Tauri (Rust)  <-->  Python Sidecar (FastAPI)
     :1420                                        :14200
```

- **Frontend**: `src/` - Vue 3 + Tailwind CSS 4
- **Tauri**: `src-tauri/` - Rust, manages sidecar lifecycle
- **Python**: `src-python/` - FastAPI + Presidio + spaCy

## Key Files

| File | Purpose |
|------|---------|
| `src-python/anonymize_api/main.py` | FastAPI entry point |
| `src-python/anonymize_api/recognizers/swiss.py` | Swiss entity patterns (AHV, IBAN, phone) |
| `src-tauri/src/sidecar.rs` | Sidecar spawn/health check logic |
| `src-tauri/tauri.conf.json` | Tauri config, sidecar path in `bundle.externalBin` |
| `src/composables/useAnonymizer.ts` | Frontend anonymization logic |
| `src/lib/api.ts` | Typed API client |

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Check if model is loaded |
| `/entities` | GET | List available entity types |
| `/anonymize` | POST | Anonymize text |

## Swiss Entity Types

- `CH_AHV` - Social security: `756.1234.5678.90`
- `CH_PHONE` - Phone: `+41 79 123 45 67`
- `CH_POSTAL_CODE` - PLZ: `8001`
- `CH_IBAN` - Bank: `CH93 0076 2011 6238 5295 7`

## Build Notes

1. Python sidecar must be built before Tauri app
2. Binary name must match platform: `anonymize-api-aarch64-apple-darwin` (macOS ARM)
3. Sidecar runs on port 14200
4. spaCy model `de_core_news_sm` is bundled (~15MB)

## Common Issues

**App crashes on startup**: Check sidecar binary exists and is not 0 bytes
```bash
ls -la src-tauri/binaries/
```

**API not responding**: Model takes ~10s to load on first request

**Build fails**: Ensure Python sidecar builds first, then Tauri app
