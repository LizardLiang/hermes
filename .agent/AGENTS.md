# Hermes - AI Agent Context

This document provides context for AI agents working on the Hermes project.

## Project Overview

**Hermes** is a Crowdin i18n Manager - a TUI/CLI tool for managing translations with Gemini AI support.

### Quick Facts

| Item | Value |
|------|-------|
| Language | Python 3.11+ |
| TUI Framework | Textual |
| CLI Framework | Typer |
| AI Integration | Google Gemini 2.0 Flash |
| Build Tool | PyInstaller |
| Package Manager | uv |

---

## Folder Structure

```
NetZero-Hermes/
│
├── .agent/                          # AI Agent documentation
│   ├── AGENTS.md                    # This file - agent context
│   └── docs/
│       ├── PRD-v1.0.md              # Product Requirements v1.0 (current)
│       ├── PRD-v1.1.md              # Product Requirements v1.1 (planned)
│       ├── CODE_PATTERNS.md         # Mandatory coding standards
│       └── BUGS.md                  # Known bugs to fix
│
├── src/hermes/                      # Main source code
│   ├── __init__.py
│   ├── __main__.py                  # Entry point (TUI/CLI router)
│   ├── cli.py                       # CLI commands (Typer-based)
│   │
│   ├── core/                        # Business logic
│   │   ├── __init__.py
│   │   ├── config.py                # Configuration & profile management
│   │   ├── crowdin_api.py           # Crowdin download API client
│   │   ├── crowdin_upload_api.py    # Crowdin upload + Gemini AI translation
│   │   └── file_operations.py       # File processing (ZIP, JSON→JS)
│   │
│   └── tui/                         # Terminal UI
│       ├── __init__.py
│       ├── app.py                   # Main Textual application
│       ├── hermes.tcss              # TUI styles (Tokyo Night theme)
│       └── screens/
│           ├── __init__.py
│           ├── main_menu.py         # Main menu screen
│           ├── settings.py          # Profile settings screen
│           ├── download.py          # Download translations screen
│           └── upload.py            # Upload translations screen
│
├── i18n/default/                    # Output: processed translations
│   ├── ar-sa/
│   ├── en-us/
│   ├── ja-jp/
│   ├── native/                      # zh-TW (Traditional Chinese)
│   ├── zh-cn/
│   ├── th-th/
│   ├── vi-vn/
│   └── id-ID/
│
├── GSSKPIM-1 (translations)/        # Input: downloaded Crowdin files
│
├── pyproject.toml                   # Project configuration
├── hermes.spec                      # PyInstaller build spec
├── hermes.config.json               # Runtime configuration
├── uv.lock                          # Dependency lock file
├── keys.txt                         # New translation keys to upload
├── prompts.txt                      # AI translation context/prompts
├── README.md                        # User documentation
└── dist/hermes.exe                  # Built executable
```

---

## Key Concepts

### 1. Profiles
Multiple named configurations stored in `hermes.config.json`. Each profile contains:
- Crowdin project ID
- Input/output paths
- API tokens (base64 obfuscated)

### 2. Translation Workflow

**Download:**
```
Crowdin Build → Poll Status → Download ZIP → Extract → JSON→JS Convert
```

**Upload:**
```
Read keys.txt → Gemini AI Translate → Add Keys to Crowdin → Upload Translations
```

### 3. Language Mapping

| Crowdin Code | Output Folder | Language |
|--------------|---------------|----------|
| ar-SA | ar-sa | Arabic |
| en-US | en-us | English |
| ja-JP | ja-jp | Japanese |
| zh-TW | native | Traditional Chinese |
| zh-CN | zh-cn | Simplified Chinese |
| th-TH | th-th | Thai |
| vi-VN | vi-vn | Vietnamese |
| id-ID | id-ID | Indonesian |

### 4. File Format Conversion

**Input (Crowdin JSON):**
```json
{"key.name": "Translation value"}
```

**Output (Radar.i18n JS):**
```javascript
Radar.i18n.load({"key.name": "Translation value"});
```

---

## Development Commands

```bash
# Install dependencies
uv sync

# Run TUI mode
uv run hermes

# Run CLI mode
uv run hermes download
uv run hermes upload
uv run hermes config show

# Build executable
uv run pyinstaller hermes.spec

# Lint code
uv run ruff check src/
```

---

## Current Status

### Version 1.0 (Released)
- Download translations from Crowdin
- Upload new keys with AI translation
- Multi-profile support
- TUI and CLI interfaces

### Version 1.1 (Planned)
See `.agent/docs/PRD-v1.1.md` for detailed requirements:
- Translation preview before upload
- Inline editing of AI translations
- Save/load drafts
- Batch key management
- Key validation

---

## Known Issues

See `.agent/docs/BUGS.md` for full bug tracking.

---

## Architecture Notes

### Presentation Layer
- **TUI**: Textual-based screens with Tokyo Night theme
- **CLI**: Typer commands with Rich output

### Core Layer
- `config.py`: Profile and token management
- `crowdin_api.py`: Download operations
- `crowdin_upload_api.py`: Upload + AI translation
- `file_operations.py`: File system operations

### External Services
- **Crowdin API**: Translation management platform
- **Google Gemini AI**: Automatic translation generation

---

## AI Agent Guidelines

When working on this project:

1. **Read CODE_PATTERNS.md first** - `.agent/docs/CODE_PATTERNS.md` contains mandatory coding standards. Read it before writing any code.
2. **Read PRDs** - Check `.agent/docs/PRD-*.md` for product requirements
3. **Maintain TUI/CLI parity** - Features should work in both interfaces
4. **Test with `uv run`** - Don't forget to test changes
5. **Update this file** - Keep folder structure current after major changes
