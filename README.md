# Anonymize

A desktop app for anonymizing sensitive information in Swiss documents. Paste or upload text, and the app automatically detects and redacts personal data like names, addresses, AHV numbers, and more.

**All processing happens locally on your machine** — your data never leaves your computer.

## Download

Download the latest version from the [Releases](https://github.com/bitfox-ch/anonymize/releases) page:

- **macOS**: Download the `.dmg` file
- **Windows**: Download the `.msi` installer

### Important: Unsigned Executables

The app is not code-signed, so your operating system will show security warnings.

**On Windows:**
1. When you run the installer, Windows Defender SmartScreen will block it
2. Click "More info"
3. Click "Run anyway"

**On macOS:**
1. After mounting the DMG and dragging the app to Applications, macOS will block it
2. Open Terminal and run:
   ```bash
   xattr -cr /Applications/Anonymize.app
   ```
3. Now you can open the app normally

## Features

- **Swiss-specific detection**: Recognizes AHV/AVS numbers, Swiss phone numbers, postal codes, and IBAN
- **Standard PII detection**: Names, email addresses, locations, dates, and more
- **Multiple anonymization styles**:
  - **Replace**: `Hans Müller` → `<PERSON>`
  - **Mask**: `Hans Müller` → `***********`
  - **Hash**: `Hans Müller` → `a1b2c3d4...`
  - **Redact**: `Hans Müller` → *(removed)*
- **Two NLP models to choose from**:
  - **spaCy** (`de_core_news_sm`): Fast, lightweight German model (~15MB). Bundled with the app, works completely offline.
  - **Transformers** (`tabularisai/eu-pii-safeguard`): More accurate EU-focused PII detection with broader entity coverage. Downloaded on first use (~500MB).
- **Completely offline**: No internet connection required (with spaCy model)

## Supported Entity Types

### Swiss-specific
| Entity | Example |
|--------|---------|
| AHV/AVS number | `756.1234.5678.90` |
| Swiss phone number | `+41 79 123 45 67` |
| Swiss postal code | `8001` |
| Swiss IBAN | `CH93 0076 2011 6238 5295 7` |

### Standard
| Entity | Example |
|--------|---------|
| Person names | `Hans Müller` |
| Email addresses | `hans@example.ch` |
| Phone numbers | `044 123 45 67` |
| Locations | `Zürich`, `Bahnhofstrasse 1` |
| Dates | `15. März 2024` |

---

## Technical Details

### Architecture

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

### Tech Stack

- **Frontend**: Vue 3, TypeScript, Tailwind CSS 4, Vite
- **Desktop**: Tauri 2, Rust
- **Backend**: Python 3.11+, FastAPI, Uvicorn
- **NLP**: Microsoft Presidio, spaCy (de_core_news_sm)

### Building from Source

#### Prerequisites

- Node.js 18+ and npm
- Rust (for Tauri)
- Python 3.11+
- uv (Python package manager)

#### Development

```bash
# Install dependencies
npm install
uv sync --project src-python

# Run in development mode
npm run tauri dev
```

#### Production Build

```bash
# Build Python sidecar first
uv run --project src-python python src-python/build.py

# Build desktop app
npm run tauri build
```

### API Endpoints

The Python sidecar runs on port 14200 and exposes:

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check, returns model status |
| `GET` | `/entities` | List available entity types |
| `POST` | `/analyze` | Analyze text, return detected entities |
| `POST` | `/anonymize` | Analyze and anonymize text |
| `GET` | `/config` | Get current configuration |
| `PUT` | `/config` | Update configuration |

#### Example

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
  ]
}
```

### Project Structure

```
anonymize/
├── src/                          # Vue frontend
│   ├── components/               # UI components
│   ├── composables/              # Vue composables
│   └── lib/                      # API client
├── src-tauri/                    # Tauri/Rust backend
│   ├── src/                      # Rust source
│   └── tauri.conf.json           # Configuration
├── src-python/                   # Python sidecar
│   ├── anonymize_api/            # FastAPI app
│   └── build.py                  # PyInstaller build
└── package.json
```

## License

MIT
