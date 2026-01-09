# Product Requirements Document (PRD)

## Hermes - Crowdin i18n Manager

**Version:** 1.0.0  
**Last Updated:** January 9, 2026  
**Status:** Released  

---

## 1. Executive Summary

### 1.1 Product Vision

Hermes is a unified localization management tool designed to streamline the translation workflow between development teams and the Crowdin translation platform. By combining an intuitive Terminal User Interface (TUI) with a scriptable CLI, Hermes eliminates manual translation management overhead while leveraging AI to accelerate the localization process.

### 1.2 Problem Statement

Development teams managing multilingual applications face several challenges:

| Challenge | Impact |
|-----------|--------|
| Manual translation downloads | Time-consuming, error-prone process |
| Format conversion requirements | JSON to framework-specific formats require custom scripts |
| Adding new translation keys | Multi-step process across multiple tools |
| Translating new content | External translation services add cost and delay |
| Configuration management | Different projects/environments need different settings |

### 1.3 Solution

Hermes provides a single, portable tool that:
- Automates Crowdin build and download workflows
- Converts translation formats automatically (JSON → JS for Radar.i18n)
- Integrates Gemini AI for instant translation of new keys
- Supports multiple configuration profiles
- Works as both interactive TUI and scriptable CLI

---

## 2. Target Users

### 2.1 Primary Users

| User Type | Description | Key Needs |
|-----------|-------------|-----------|
| **i18n Managers** | Responsible for translation coordination | Efficient workflows, status visibility, multi-project support |
| **Developers** | Add new features requiring translations | Quick key addition, minimal context switching |
| **DevOps/CI** | Automate translation workflows | CLI interface, scriptable operations |

### 2.2 User Personas

#### Persona 1: Lin (i18n Manager)
- **Role:** Localization Manager at enterprise company
- **Goals:** Manage translations for 8+ languages efficiently
- **Pain Points:** Repetitive manual downloads, tracking translation status
- **Uses Hermes for:** Daily translation downloads, batch updates

#### Persona 2: Wei (Frontend Developer)
- **Role:** Frontend developer adding new features
- **Goals:** Add translation keys without leaving development flow
- **Pain Points:** Learning Crowdin interface, waiting for translations
- **Uses Hermes for:** Adding keys with AI-generated translations

#### Persona 3: Chen (DevOps Engineer)
- **Role:** CI/CD pipeline maintainer
- **Goals:** Automate translation updates in build pipeline
- **Pain Points:** Manual intervention in deployment
- **Uses Hermes for:** CLI commands in CI/CD scripts

---

## 3. Product Features

### 3.1 Feature Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     HERMES FEATURES                         │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  DOWNLOAD   │  │   UPLOAD    │  │  PROFILE MANAGEMENT │  │
│  │  ─────────  │  │  ─────────  │  │  ─────────────────  │  │
│  │ • Build     │  │ • Read keys │  │ • Multiple profiles │  │
│  │ • Poll      │  │ • AI trans  │  │ • Token storage     │  │
│  │ • Download  │  │ • Add keys  │  │ • Path config       │  │
│  │ • Extract   │  │ • Upload    │  │ • Portable mode     │  │
│  │ • Convert   │  │             │  │                     │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│           TUI (Interactive)  │  CLI (Scriptable)            │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Feature Details

#### 3.2.1 Download Translations (P0 - Critical)

**Description:** Download and process translations from Crowdin project.

**User Story:**  
> As an i18n Manager, I want to download all translations with a single action, so that I can update my project without manual file handling.

**Acceptance Criteria:**
- [ ] Initiate Crowdin build for all languages
- [ ] Display real-time progress during build polling
- [ ] Download completed build as ZIP archive
- [ ] Extract files to configured data path
- [ ] Convert JSON files to JS format (Radar.i18n compatible)
- [ ] Organize output by language folder structure
- [ ] Display success/failure status with details

**Workflow:**
```
[Start Download] 
       ↓
[Initiate Crowdin Build] 
       ↓
[Poll Build Status] ←──┐
       ↓               │
   Building? ──Yes────┘
       ↓ No
[Download ZIP]
       ↓
[Extract to Data Path]
       ↓
[Convert JSON → JS for each language]
       ↓
[Save to Result Path]
       ↓
[Display Success]
```

**Supported Languages:**
| Language | Code | Output Folder |
|----------|------|---------------|
| Arabic | ar-SA | ar-sa |
| English (US) | en-US | en-us |
| Japanese | ja-JP | ja-jp |
| Chinese (TW) | zh-TW | native |
| Chinese (CN) | zh-CN | zh-cn |
| Thai | th-TH | th-th |
| Vietnamese | vi-VN | vi-vn |
| Indonesian | id-ID | id-ID |

---

#### 3.2.2 Upload Translations (P0 - Critical)

**Description:** Add new translation keys with AI-powered translations to Crowdin.

**User Story:**  
> As a Developer, I want to add new translation keys and get instant translations, so that I don't have to wait for external translation services.

**Acceptance Criteria:**
- [ ] Read new keys from configurable keys file
- [ ] Optionally download latest translations first
- [ ] Generate translations using Gemini AI for all 7 target languages
- [ ] Add new keys to Crowdin project
- [ ] Upload AI-generated translations for each language
- [ ] Display progress and results

**Workflow:**
```
[Start Upload]
       ↓
[Download First?] ──Yes──→ [Download Workflow]
       ↓ No                       ↓
[Read keys.txt] ←─────────────────┘
       ↓
[Use Gemini AI?] ──Yes──→ [Translate to 7 languages]
       ↓ No                       ↓
[Add Keys to Crowdin] ←───────────┘
       ↓
[Upload Translations per Language]
       ↓
[Display Results]
```

**AI Translation Languages:**
| Target Language | Crowdin Code |
|-----------------|--------------|
| Traditional Chinese | zh-TW |
| Simplified Chinese | zh-CN |
| English (US) | en-US |
| Japanese | ja-JP |
| Thai | th-TH |
| Vietnamese | vi-VN |
| Indonesian | id-ID |

---

#### 3.2.3 Profile Management (P1 - High)

**Description:** Manage multiple configuration profiles for different projects/environments.

**User Story:**  
> As an i18n Manager handling multiple projects, I want to switch between configurations easily, so that I can manage different Crowdin projects efficiently.

**Acceptance Criteria:**
- [ ] Create new profiles with custom settings
- [ ] Edit existing profile configurations
- [ ] Delete profiles (except last remaining)
- [ ] Switch active profile
- [ ] Secure token storage (base64 obfuscation)
- [ ] Portable configuration file

**Profile Configuration:**
| Setting | Description | Example |
|---------|-------------|---------|
| Name | Profile identifier | "production" |
| Project ID | Crowdin project ID | "577773" |
| Data Path | Downloaded files location | "translations/" |
| Result Path | Processed files output | "i18n/default/" |
| Keys Path | New translation keys file | "keys.txt" |
| Prompts Path | AI translation context | "prompts.txt" |
| Crowdin Token | API authentication | (obfuscated) |
| Gemini Token | AI API authentication | (obfuscated) |

---

#### 3.2.4 Dual Interface Mode (P1 - High)

**Description:** Support both interactive TUI and scriptable CLI interfaces.

**User Story:**  
> As a DevOps Engineer, I want to use CLI commands in scripts, while i18n Managers prefer visual interface, so the tool should support both workflows.

**TUI Mode (No Arguments):**
```
┌──────────────────────────────────────────┐
│           HERMES - Main Menu             │
├──────────────────────────────────────────┤
│                                          │
│    [D] Download Translations             │
│    [U] Upload Translations               │
│    [S] Settings                          │
│    [Q] Quit                              │
│                                          │
│    Profile: default                      │
│    Project: 577773                       │
│                                          │
└──────────────────────────────────────────┘
```

**CLI Mode (With Arguments):**
```bash
# Download translations
hermes download [--profile NAME]

# Upload translations  
hermes upload [--profile NAME] [--download-first] [--use-gemini]

# Configuration management
hermes config list
hermes config show [PROFILE]
hermes config set PROFILE KEY VALUE
```

---

## 4. User Experience

### 4.1 Design Principles

| Principle | Implementation |
|-----------|----------------|
| **Efficiency** | Single-action workflows, keyboard shortcuts |
| **Visibility** | Real-time progress, clear status messages |
| **Flexibility** | TUI for exploration, CLI for automation |
| **Portability** | Single executable, config file alongside |
| **Reliability** | Error handling, graceful degradation |

### 4.2 TUI Navigation

| Key | Action |
|-----|--------|
| `D` | Open Download screen |
| `U` | Open Upload screen |
| `S` | Open Settings screen |
| `Q` | Quit application |
| `Tab` | Navigate between elements |
| `Enter` | Confirm action |
| `Escape` | Go back / Cancel |

### 4.3 Visual Theme

- **Color Scheme:** Tokyo Night (dark theme optimized for terminal)
- **Typography:** Monospace, optimized for terminal rendering
- **Feedback:** Color-coded status (green=success, red=error, yellow=warning)

### 4.4 Error Handling

| Error Type | User Experience |
|------------|-----------------|
| Network failure | Retry prompt with details |
| Invalid token | Clear message directing to settings |
| Build failure | Show Crowdin error message |
| AI translation error | Fallback notice, continue without AI |
| File permission error | Clear path and permission guidance |

---

## 5. Technical Specifications

### 5.1 Technology Stack

| Layer | Technology | Rationale |
|-------|------------|-----------|
| Language | Python 3.11+ | Cross-platform, rich ecosystem |
| TUI Framework | Textual | Modern async TUI, CSS-like styling |
| CLI Framework | Typer | Type hints, auto-documentation |
| HTTP Client | Requests | Stable, well-documented |
| AI Integration | Google GenAI | Fast, cost-effective translations |
| Build Tool | PyInstaller | Single executable distribution |

### 5.2 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Presentation Layer                      │
│  ┌─────────────────────────┐  ┌─────────────────────────┐   │
│  │      TUI (Textual)      │  │      CLI (Typer)        │   │
│  │  • Main Menu Screen     │  │  • download command     │   │
│  │  • Download Screen      │  │  • upload command       │   │
│  │  • Upload Screen        │  │  • config command       │   │
│  │  • Settings Screen      │  │                         │   │
│  └─────────────────────────┘  └─────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│                       Core Layer                             │
│  ┌───────────────┐  ┌───────────────┐  ┌────────────────┐   │
│  │  config.py    │  │ crowdin_api   │  │ file_operations│   │
│  │  ───────────  │  │ ───────────── │  │ ──────────────│   │
│  │ • Load/Save   │  │ • Build       │  │ • Extract ZIP  │   │
│  │ • Profiles    │  │ • Download    │  │ • JSON → JS    │   │
│  │ • Tokens      │  │ • Upload      │  │ • File mapping │   │
│  └───────────────┘  └───────────────┘  └────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│                     External Services                        │
│  ┌─────────────────────────┐  ┌─────────────────────────┐   │
│  │      Crowdin API        │  │      Gemini AI API      │   │
│  └─────────────────────────┘  └─────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 5.3 File Output Format

**Input (Crowdin JSON):**
```json
{
  "key.name": "Translation value",
  "another.key": "Another value"
}
```

**Output (Radar.i18n JS):**
```javascript
Radar.i18n.load({
  "key.name": "Translation value",
  "another.key": "Another value"
});
```

### 5.4 Configuration File Schema

```json
{
  "active_profile": "string",
  "profiles": {
    "<profile_name>": {
      "name": "string",
      "project_id": "string",
      "data_path": "string",
      "result_path": "string",
      "key_path": "string",
      "prompts_path": "string",
      "crowdin_token": "string (base64)",
      "gemini_token": "string (base64)"
    }
  }
}
```

---

## 6. Success Metrics

### 6.1 Key Performance Indicators (KPIs)

| Metric | Target | Measurement |
|--------|--------|-------------|
| Download time | < 2 min for full build | Time from start to completion |
| Upload success rate | > 99% | Successful uploads / Total attempts |
| AI translation accuracy | > 90% usable | Manual review sample |
| User adoption | 100% of i18n team | Active users / Team size |
| Error rate | < 5% | Failed operations / Total operations |

### 6.2 User Satisfaction Goals

| Goal | Target |
|------|--------|
| Time saved per download | > 10 minutes vs manual |
| Time saved per upload | > 30 minutes vs manual |
| Learning curve | < 15 minutes to proficiency |
| Support tickets | < 2 per month |

---

## 7. Future Roadmap

### 7.1 Version 1.1 (Planned)

| Feature | Priority | Description |
|---------|----------|-------------|
| Translation preview | P1 | Preview AI translations before upload |
| Batch key management | P1 | Add/remove multiple keys at once |
| Build history | P2 | View and restore previous builds |
| Diff viewer | P2 | Compare translation changes |

### 7.2 Version 1.2 (Planned)

| Feature | Priority | Description |
|---------|----------|-------------|
| Multi-project sync | P1 | Sync translations across projects |
| Custom AI prompts | P2 | User-defined translation context |
| Translation memory | P2 | Reuse previous translations |
| Glossary support | P2 | Consistent terminology enforcement |

### 7.3 Version 2.0 (Vision)

| Feature | Priority | Description |
|---------|----------|-------------|
| Web interface | P1 | Browser-based alternative to TUI |
| Team collaboration | P1 | Shared profiles, audit logs |
| CI/CD plugins | P2 | GitHub Actions, GitLab CI integration |
| Translation QA | P2 | Automated quality checks |

---

## 8. Appendix

### 8.1 Glossary

| Term | Definition |
|------|------------|
| **Crowdin** | Cloud-based translation management platform |
| **TUI** | Terminal User Interface - graphical interface in terminal |
| **CLI** | Command Line Interface - text-based commands |
| **i18n** | Internationalization - designing for multiple languages |
| **Gemini AI** | Google's generative AI model |
| **Profile** | Named configuration for a specific project |

### 8.2 Related Documents

- Crowdin API Documentation: https://developer.crowdin.com/api/v2/
- Google Gemini API: https://ai.google.dev/docs
- Textual Framework: https://textual.textualize.io/

### 8.3 Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-09 | Auto-generated | Initial PRD based on codebase analysis |

---

*This PRD was generated by analyzing the existing Hermes codebase. It documents current functionality and proposes future enhancements based on product management best practices.*
