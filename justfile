# Anonymize - Development Commands

# Default recipe: list available commands
default:
    @just --list

# Run the full Tauri app in development mode
dev:
    npm run tauri dev

# Run only the Python API backend (for API development)
api:
    ~/.local/bin/uv run --project src-python uvicorn anonymize_api.main:app --port 14200 --reload

# Run only the Vue frontend (without Tauri)
frontend:
    npm run dev

# Build the Python sidecar binary
build-sidecar:
    ~/.local/bin/uv run --project src-python python src-python/build.py

# Build the production Tauri app (builds sidecar first)
build: build-sidecar
    npm run tauri build

# Kill any running backend processes
kill-backend:
    -pkill -9 -f "uvicorn.*anonymize_api" 2>/dev/null || true
    -pkill -9 -f "anonymize-api" 2>/dev/null || true
    -kill -9 $(lsof -ti :14200) 2>/dev/null || true
    @echo "Backend processes killed"

# Kill frontend dev server
kill-frontend:
    -pkill -9 -f "vite" 2>/dev/null || true
    -kill -9 $(lsof -ti :1420) 2>/dev/null || true
    @echo "Frontend processes killed"

# Kill all dev processes (backend + frontend)
kill: kill-backend kill-frontend
    @echo "All processes killed"

# Restart the API backend (kill then start)
restart-api: kill
    @sleep 1
    ~/.local/bin/uv run --project src-python uvicorn anonymize_api.main:app --port 14200 --reload

# Check backend health
health:
    @curl -s http://127.0.0.1:14200/health | python3 -m json.tool || echo "Backend not running"

# Test the anonymize endpoint with sample text
test-api:
    @curl -s -X POST http://127.0.0.1:14200/anonymize \
        -H "Content-Type: application/json" \
        -d '{"text": "Hans Müller wohnt in Zürich. AHV: 756.1234.5678.90"}' \
        | python3 -m json.tool

# Test entities endpoint
test-entities:
    @echo "Testing /entities endpoint..."
    @curl -s http://127.0.0.1:14200/entities | python3 -m json.tool || echo "Failed to fetch entities"
    @echo ""
    @echo "Entity count:"
    @curl -s http://127.0.0.1:14200/entities | python3 -c "import sys, json; data = json.load(sys.stdin); print(len(data.get('entities', [])))" 2>/dev/null || echo "0"

# Full API test suite
test-all: health test-entities test-api
    @echo "All tests completed"

# Install dependencies
install:
    npm install
    ~/.local/bin/uv sync --project src-python

# Clean build artifacts
clean:
    rm -rf dist
    rm -rf src-tauri/target
    rm -rf src-python/.venv
    rm -rf node_modules

# Show default entity config
show-config:
    @echo "Default config (bundled):"
    @cat src-tauri/resources/entity-config.json
    @echo ""
    @echo "User config (if exists):"
    @cat ~/Library/Application\ Support/com.anonymize.app/entity-config.json 2>/dev/null || echo "No user config yet"

# Edit default entity config
edit-config:
    ${EDITOR:-nano} src-tauri/resources/entity-config.json

# Reset user config to defaults
reset-config:
    rm -f ~/Library/Application\ Support/com.anonymize.app/entity-config.json
    @echo "User config removed. App will use default config on next launch."
