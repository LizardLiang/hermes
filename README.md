# Hermes - Crowdin i18n Manager

A unified TUI and CLI tool for managing Crowdin translations with Gemini AI translation support.

## Features

- 📥 **Download translations** from Crowdin and convert to JS format
- 📤 **Upload translations** with automatic Gemini AI translation for new keys
- ⚙️ **Profile management** - save multiple configurations
- 🔐 **Secure token storage** - API tokens stored in system keyring
- 🖥️ **Dual mode** - Interactive TUI or scriptable CLI

## Installation

### From Source (Development)

```bash
# Clone the repository
cd NetZero-Hermes

# Install with uv (recommended)
uv sync

# Run in TUI mode
uv run hermes

# Run in CLI mode
uv run hermes --help
```

### Building Executable

```bash
# Install dev dependencies
uv sync --dev

# Build single executable with PyInstaller
uv run pyinstaller hermes.spec

# Output: dist/hermes.exe
```

## Usage

### TUI Mode (Interactive)

Simply run without arguments to launch the interactive interface:

```bash
hermes
```

Navigate with:
- Arrow keys to move
- Enter to select
- Escape to go back
- Q to quit

### CLI Mode

#### Download Translations

```bash
# Using configured profile
hermes download

# With profile selection
hermes download --profile production

# Override settings
hermes download --token YOUR_TOKEN --project-id 12345
```

#### Upload Translations

```bash
# Full upload with Gemini AI translation
hermes upload

# Skip download step
hermes upload --no-download

# Skip AI translation
hermes upload --no-gemini

# With custom keys file
hermes upload --keys my-keys.txt
```

#### Configuration Commands

```bash
# Show current config
hermes config show

# Set active profile
hermes config set-profile production

# Create new profile
hermes config create-profile production --project-id 12345

# Delete profile
hermes config delete-profile old-profile

# Set API tokens (stored securely)
hermes config set-token --crowdin YOUR_CROWDIN_TOKEN
hermes config set-token --gemini YOUR_GEMINI_TOKEN

# Set other config values
hermes config set --project-id 12345
hermes config set --data-path "translations/"
hermes config set --result-path "i18n/default/"

# Show config file path
hermes config path
```

## Configuration

Configuration is stored **next to the executable** (portable mode):
- **Config file**: `./hermes.config.json` (same directory as the executable)
- **API tokens**: Stored in config file (base64 obfuscated)

This makes Hermes fully portable - just copy the executable and config file together.

### Config File Structure

```json
{
  "active_profile": "default",
  "profiles": {
    "default": {
      "name": "default",
      "project_id": "577773",
      "data_path": "GSSKPIM-1 (translations)/",
      "result_path": "i18n/default/",
      "key_path": "keys.txt",
      "prompts_path": "prompts.txt",
      "crowdin_token": "<base64 encoded>",
      "gemini_token": "<base64 encoded>"
    }
  }
}
```

### Environment Variables

You can also set tokens via environment variables:
- `CROWDIN_TOKEN` - Crowdin API token
- `GEMINI_TOKEN` - Gemini API token

## Project Structure

```
NetZero-Hermes/
├── src/hermes/
│   ├── __init__.py
│   ├── __main__.py          # Entry point (TUI/CLI router)
│   ├── cli.py                # CLI commands (Typer)
│   ├── core/
│   │   ├── config.py         # Configuration management
│   │   ├── crowdin_api.py    # Crowdin download API
│   │   ├── crowdin_upload_api.py  # Crowdin upload + Gemini
│   │   └── file_operations.py     # File processing
│   └── tui/
│       ├── app.py            # Main Textual app
│       ├── hermes.tcss       # TUI styles
│       └── screens/
│           ├── main_menu.py  # Main menu
│           ├── settings.py   # Settings screen
│           ├── download.py   # Download screen
│           └── upload.py     # Upload screen
├── pyproject.toml
├── hermes.spec               # PyInstaller config
└── README.md
```

## Dependencies

- **textual** - TUI framework
- **typer** - CLI framework
- **rich** - Terminal formatting
- **requests** - HTTP client
- **google-generativeai** - Gemini AI

## License

MIT
