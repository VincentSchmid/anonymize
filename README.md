# Anonymize

A desktop application for anonymizing Swiss documents using Microsoft Presidio. Built with Vue, Tauri, and Python.

## Features

- **Swiss-specific entity detection**: AHV/AVS numbers, Swiss phone numbers, postal codes, and IBAN
- **Standard PII detection**: Names, email addresses, locations, dates, and more
- **Multiple anonymization styles**:
  - **Replace**: `Hans Müller` → `<PERSON>`
  - **Mask**: `Hans Müller` → `***********`
  - **Hash**: `Hans Müller` → `a1b2c3d4...`
  - **Redact**: `Hans Müller` → *(removed)*
- **Offline processing**: All data stays on your machine
- **German language optimized**: Uses spaCy's German NLP model

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Tauri Desktop App                     │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────────────┐    ┌─────────────────────────┐ │
│  │    Vue Frontend     │    │    Python Sidecar       │ │
│  │  (Tailwind CSS 4)   │◄──►│  (FastAPI + Presidio)   │ │
│  │                     │    │                         │ │
│  │  • Text input       │    │  • NLP analysis         │ │
│  │  • File upload      │    │  • Entity detection     │ │
│  │  • Entity toggles   │    │  • Anonymization        │ │
│  │  • Result display   │    │  • Swiss recognizers    │ │
│  └─────────────────────┘    └─────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

## Prerequisites

- **Node.js** 18+ and npm
- **Rust** (for Tauri)
- **uv** (Python package manager) - will be installed automatically if missing
- **Python** 3.11+

## Quick Start

### 1. Install dependencies

```bash
# Install Node.js dependencies
npm install

# Install Python dependencies
~/.local/bin/uv sync --project src-python
```

### 2. Run in development mode

**Option A: Full Tauri app**
```bash
npm run tauri dev
```

**Option B: Python API only (for testing)**
```bash
~/.local/bin/uv run --project src-python uvicorn anonymize_api.main:app --port 14200
```

**Option C: Frontend only (requires API running)**
```bash
npm run dev
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check, returns model status |
| `GET` | `/entities` | List available entity types |
| `POST` | `/analyze` | Analyze text, return detected entities |
| `POST` | `/anonymize` | Analyze and anonymize text |
| `GET` | `/config` | Get current configuration |
| `PUT` | `/config` | Update configuration |

### Example: Anonymize text

```bash
curl -X POST http://localhost:14200/anonymize \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hans Müller wohnt in Zürich. AHV: 756.1234.5678.90",
    "anonymization_style": "replace"
  }'
```

Response:
```json
{
  "original_text": "Hans Müller wohnt in Zürich. AHV: 756.1234.5678.90",
  "anonymized_text": "<PERSON> wohnt in <LOCATION>. AHV: <CH_AHV>",
  "entities": [
    {"entity_type": "PERSON", "text": "Hans Müller", "score": 0.85},
    {"entity_type": "LOCATION", "text": "Zürich", "score": 0.85},
    {"entity_type": "CH_AHV", "text": "756.1234.5678.90", "score": 0.95}
  ],
  "anonymization_style": "replace"
}
```

## Supported Entity Types

### Swiss-specific
| Entity | Description | Example |
|--------|-------------|---------|
| `CH_AHV` | Swiss social security number | `756.1234.5678.90` |
| `CH_PHONE` | Swiss phone number | `+41 79 123 45 67` |
| `CH_POSTAL_CODE` | Swiss postal code | `8001` |
| `CH_IBAN` | Swiss IBAN | `CH93 0076 2011 6238 5295 7` |

### Standard
| Entity | Description |
|--------|-------------|
| `PERSON` | Person names |
| `EMAIL_ADDRESS` | Email addresses |
| `PHONE_NUMBER` | Phone numbers |
| `LOCATION` | Addresses, cities |
| `DATE_TIME` | Dates and times |
| `IBAN_CODE` | International bank accounts |

## Building for Production

### 1. Build the Python sidecar binary

```bash
cd src-python
~/.local/bin/uv run python build.py
```

This creates a standalone binary in `src-tauri/binaries/`.

### 2. Build the desktop app

```bash
npm run tauri build
```

Output locations:
- **macOS**: `src-tauri/target/release/bundle/dmg/`
- **Windows**: `src-tauri/target/release/bundle/msi/`
- **Linux**: `src-tauri/target/release/bundle/appimage/`

## Project Structure

```
anonymize/
├── src/                          # Vue frontend
│   ├── components/
│   │   ├── ui/                   # Base UI components
│   │   ├── TextInput.vue         # Text input area
│   │   ├── FileUpload.vue        # File drag & drop
│   │   ├── EntityToggle.vue      # Entity type toggles
│   │   ├── AnonymizationSettings.vue
│   │   └── ResultViewer.vue      # Results display
│   ├── composables/
│   │   ├── useAnonymizer.ts      # Anonymization logic
│   │   └── useSidecar.ts         # Backend management
│   └── lib/
│       └── api.ts                # Typed API client
├── src-tauri/                    # Tauri/Rust backend
│   ├── src/
│   │   ├── lib.rs                # App entry point
│   │   └── sidecar.rs            # Sidecar management
│   └── tauri.conf.json           # Tauri configuration
├── src-python/                   # Python sidecar
│   ├── anonymize_api/
│   │   ├── api/                  # FastAPI routes
│   │   ├── core/                 # Presidio wrappers
│   │   └── recognizers/          # Swiss recognizers
│   ├── pyproject.toml            # Python dependencies
│   └── build.py                  # PyInstaller build
├── package.json
└── vite.config.ts
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ANONYMIZE_HOST` | `127.0.0.1` | API host |
| `ANONYMIZE_PORT` | `14200` | API port |
| `ANONYMIZE_DEBUG` | `false` | Enable debug mode |

### Adjusting Entity Detection

Edit `src-python/anonymize_api/core/config.py` to change default enabled entities:

```python
default_entities: list[str] = [
    "PERSON",
    "EMAIL_ADDRESS",
    "PHONE_NUMBER",
    "LOCATION",
    "CH_AHV",
    "CH_PHONE",
    "CH_IBAN",
]
```

## Tech Stack

- **Frontend**: Vue 3, TypeScript, Tailwind CSS 4, Vite
- **Desktop**: Tauri 2, Rust
- **Backend**: Python 3.11+, FastAPI, Uvicorn
- **NLP**: Microsoft Presidio, spaCy (de_core_news_sm)

## License

MIT
