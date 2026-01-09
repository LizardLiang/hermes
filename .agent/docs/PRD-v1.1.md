# Product Requirements Document (PRD)

## Hermes v1.1 - Translation Preview & Batch Management

**Version:** 1.1.0  
**Last Updated:** January 9, 2026  
**Status:** Planning  
**Target Release:** Q1 2026  

---

## 1. Executive Summary

### 1.1 Release Vision

Hermes v1.1 focuses on **trust and efficiency** - giving users confidence in AI-generated translations before they reach Crowdin, while streamlining bulk operations for power users.

### 1.2 Release Theme

> "**See Before You Send**" - Every translation change is visible, reviewable, and controllable.

### 1.3 Key Deliverables

| Feature | Priority | User Value |
|---------|----------|------------|
| Translation Preview | P0 | Verify AI translations before upload |
| Edit & Correct | P0 | Fix AI errors inline |
| Save as Draft | P1 | Resume work later |
| Batch Key Management | P1 | Add/remove multiple keys efficiently |
| Keyboard Shortcuts | P2 | Power user productivity |

### 1.4 Success Criteria

| Metric | Target |
|--------|--------|
| Translation error rate (post-upload) | Reduce by 80% |
| User confidence score | > 4.5/5 |
| Time to review 10 translations | < 2 minutes |
| Draft save adoption | > 50% of uploads use preview |

---

## 2. Problem Statement

### 2.1 Current Pain Points

#### Pain Point 1: Blind Uploads
```
Current User Experience:

User: "I'll upload these 5 new keys with AI translation"
       ↓
System: [Translating...] [Uploading...] [Done!]
       ↓
User: "Wait, what did it actually translate? 
       Did it get the context right?
       What if there's an error?"
       ↓
User: *Logs into Crowdin to manually check*
       ↓
User: "Oh no, it translated 'Carbon Sink' as '碳水槽' (carbon water tank)
       instead of '碳匯' (carbon sequestration)"
       ↓
User: *Manually fixes in Crowdin* 😫
```

**Impact:** 
- 15-30 minutes wasted per error discovered
- Loss of trust in AI translation feature
- Users avoid using AI, defeating the purpose

#### Pain Point 2: One-at-a-Time Key Management
```
Current Workflow for 20 new keys:

1. Add key to keys.txt
2. Run upload
3. Repeat 20 times... 

Or:

1. Add all 20 keys to keys.txt
2. Run upload
3. Hope nothing goes wrong
4. No way to remove keys that were mistakes
```

**Impact:**
- Tedious workflow for bulk additions
- No key removal capability
- Error recovery requires Crowdin manual intervention

#### Pain Point 3: Lost Work
```
Scenario:

User: *Spends 10 minutes reviewing AI translations*
User: "These look good, but I need to check with the team first"
User: *Closes Hermes*
User: *Returns next day*
User: "I have to regenerate all translations again?" 😫
```

**Impact:**
- Wasted AI API calls
- Repeated review effort
- Friction in approval workflows

---

## 3. Target Users

### 3.1 Primary Users for v1.1

| User | Key v1.1 Need | Feature |
|------|---------------|---------|
| **i18n Manager** | Review before approve | Translation Preview |
| **Developer** | Quick bulk additions | Batch Key Management |
| **Team Lead** | Approval workflow | Save as Draft |

### 3.2 User Stories

#### Epic 1: Translation Preview

```
US-1.1: View AI Translations Before Upload
As an i18n Manager
I want to see all AI-generated translations before uploading
So that I can catch and fix errors before they reach Crowdin

Acceptance Criteria:
- See source key and all 7 language translations
- Translations displayed in readable table format
- Clear visual distinction between languages
- Ability to proceed or cancel upload
```

```
US-1.2: Edit Translations Inline
As an i18n Manager  
I want to edit incorrect AI translations in the preview
So that I can fix errors without leaving Hermes

Acceptance Criteria:
- Click/select any translation to edit
- Edit in place with immediate visual feedback
- Track which translations were manually edited
- Edited translations used in upload (not AI original)
```

```
US-1.3: Save Translation Draft
As a Team Lead
I want to save my reviewed translations as a draft
So that I can get approval before uploading to Crowdin

Acceptance Criteria:
- Save current preview state to local file
- Load draft to resume review later
- Draft includes: keys, all translations, edit history
- Clear indication of draft vs live upload
```

#### Epic 2: Batch Key Management

```
US-2.1: Add Multiple Keys at Once
As a Developer
I want to add multiple translation keys in one operation
So that I can efficiently add all keys for a new feature

Acceptance Criteria:
- Support multi-line input in keys file
- Process all keys in single operation
- Show progress for batch operations
- Report success/failure per key
```

```
US-2.2: Remove Keys from Upload Queue
As a Developer
I want to remove specific keys from the upload queue
So that I can fix mistakes before uploading

Acceptance Criteria:
- View list of keys to be uploaded
- Select individual keys to remove
- Confirm removal action
- Removed keys not sent to Crowdin
```

```
US-2.3: Key Validation
As a Developer
I want the system to validate my keys before translation
So that I catch formatting errors early

Acceptance Criteria:
- Check for duplicate keys
- Validate key naming convention
- Warn about keys that already exist in Crowdin
- Block upload of invalid keys with clear error message
```

---

## 4. Feature Specifications

### 4.1 Feature 1: Translation Preview Screen

#### 4.1.1 Overview

A new screen in the upload workflow that displays all AI-generated translations for review before upload.

#### 4.1.2 Screen Layout

```
┌──────────────────────────────────────────────────────────────────────────┐
│  HERMES - Translation Preview                            [Draft: Unsaved]│
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Keys to Upload: 3                    AI Model: gemini-2.0-flash         │
│  ─────────────────────────────────────────────────────────────────────── │
│                                                                          │
│  ┌─ Key 1: dashboard.carbon.title ─────────────────────────────────────┐ │
│  │                                                                      │ │
│  │  zh-TW │ 碳排放儀表板                                        [Edit] │ │
│  │  zh-CN │ 碳排放仪表板                                        [Edit] │ │
│  │  en-US │ Carbon Emissions Dashboard                          [Edit] │ │
│  │  ja-JP │ 炭素排出ダッシュボード                               [Edit] │ │
│  │  th-TH │ แดชบอร์ดการปล่อยคาร์บอน                              [Edit] │ │
│  │  vi-VN │ Bảng điều khiển phát thải carbon                    [Edit] │ │
│  │  id-ID │ Dasbor Emisi Karbon                                 [Edit] │ │
│  │                                                                      │ │
│  └──────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
│  ┌─ Key 2: dashboard.carbon.subtitle [EDITED] ─────────────────────────┐ │
│  │                                                                      │ │
│  │  zh-TW │ 即時碳排放監控 ✏️                                    [Edit] │ │
│  │  zh-CN │ 实时碳排放监控                                       [Edit] │ │
│  │  en-US │ Real-time Carbon Monitoring                         [Edit] │ │
│  │  ...                                                                 │ │
│  └──────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
│  ┌─ Key 3: dashboard.carbon.empty ─────────────────────────────────────┐ │
│  │  ...                                                                 │ │
│  └──────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
├──────────────────────────────────────────────────────────────────────────┤
│  [S] Save Draft    [R] Regenerate    [↑↓] Navigate    [Enter] Edit      │
│                                                                          │
│         [ Cancel ]                              [ Upload to Crowdin ]    │
└──────────────────────────────────────────────────────────────────────────┘
```

#### 4.1.3 Interaction States

| State | Visual Indicator | User Action |
|-------|------------------|-------------|
| Unedited | Default styling | None |
| Edited | ✏️ icon + [EDITED] badge | User modified |
| Selected | Highlighted row | Keyboard navigation |
| Editing | Inline text input | Typing |
| Error | Red border + message | Validation failed |

#### 4.1.4 Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `↑` / `↓` | Navigate between keys |
| `←` / `→` | Navigate between languages |
| `Enter` | Edit selected translation |
| `Escape` | Cancel edit / Go back |
| `S` | Save as draft |
| `R` | Regenerate AI translation for selected |
| `D` | Delete selected key from queue |
| `Ctrl+Enter` | Upload to Crowdin |

#### 4.1.5 Edit Mode

```
┌─────────────────────────────────────────────────────────────────┐
│  Editing: dashboard.carbon.subtitle (zh-TW)                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Original (AI): 即時碳排放監控                                   │
│                                                                 │
│  Your Edit:                                                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 即時碳排監測                                             │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  [ Cancel ]                                    [ Save Edit ]    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

### 4.2 Feature 2: Save as Draft

#### 4.2.1 Overview

Allow users to save their translation preview state locally for later review or team approval.

#### 4.2.2 Draft File Format

**Filename:** `hermes-draft-{timestamp}.json`

**Schema:**
```json
{
  "version": "1.1",
  "created_at": "2026-01-09T14:30:00Z",
  "updated_at": "2026-01-09T15:45:00Z",
  "profile": "default",
  "project_id": "577773",
  "ai_model": "gemini-2.0-flash",
  "status": "draft",
  "keys": [
    {
      "key": "dashboard.carbon.title",
      "translations": {
        "zh-TW": {
          "ai_original": "碳排放儀表板",
          "current": "碳排放儀表板",
          "edited": false
        },
        "zh-CN": {
          "ai_original": "碳排放仪表板",
          "current": "碳排放仪表板", 
          "edited": false
        },
        "en-US": {
          "ai_original": "Carbon Emissions Dashboard",
          "current": "Carbon Emissions Dashboard",
          "edited": false
        }
        // ... other languages
      }
    }
    // ... other keys
  ],
  "metadata": {
    "total_keys": 3,
    "edited_translations": 1,
    "prompts_hash": "abc123"
  }
}
```

#### 4.2.3 Draft Workflows

**Save Draft:**
```
[Preview Screen] 
       ↓
[Press 'S' or click "Save Draft"]
       ↓
[Select save location] (default: ./drafts/)
       ↓
[Draft saved with timestamp]
       ↓
[Continue editing or exit]
```

**Load Draft:**
```
[Upload Screen]
       ↓
[Click "Load Draft" or press 'L']
       ↓
[Select draft file from list]
       ↓
[Preview Screen with draft data]
       ↓
[Continue editing / Upload]
```

#### 4.2.4 Draft List View

```
┌──────────────────────────────────────────────────────────────────┐
│  HERMES - Load Draft                                             │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Available Drafts:                                               │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ ► hermes-draft-2026-01-09-1430.json                        │ │
│  │   Created: Jan 9, 2026 2:30 PM                             │ │
│  │   Keys: 3 | Edited: 1 | Profile: default                   │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │   hermes-draft-2026-01-08-0915.json                        │ │
│  │   Created: Jan 8, 2026 9:15 AM                             │ │
│  │   Keys: 12 | Edited: 5 | Profile: production               │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  [↑↓] Navigate    [Enter] Load    [D] Delete    [Esc] Cancel    │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

### 4.3 Feature 3: Batch Key Management

#### 4.3.1 Overview

Enhanced key management allowing bulk operations and validation before translation.

#### 4.3.2 Key Input Methods

**Method 1: Keys File (Enhanced)**
```
# keys.txt - Now supports comments and sections

# Feature: Carbon Dashboard
dashboard.carbon.title
dashboard.carbon.subtitle
dashboard.carbon.empty_state

# Feature: User Settings  
settings.user.profile_name
settings.user.language_preference

# Ignored (commented out)
# deprecated.old.key
```

**Method 2: Interactive Key Editor (New)**

```
┌──────────────────────────────────────────────────────────────────┐
│  HERMES - Key Manager                                            │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Keys to Process: 5                                              │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ [✓] dashboard.carbon.title              NEW                 ││
│  │ [✓] dashboard.carbon.subtitle           NEW                 ││
│  │ [✓] dashboard.carbon.empty_state        NEW                 ││
│  │ [✗] settings.user.profile               EXISTS - Skip       ││
│  │ [✓] settings.user.language              NEW                 ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  ┌─ Add New Key ───────────────────────────────────────────────┐│
│  │ feature.new.key                                              ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  [A] Add Key    [D] Delete Selected    [Space] Toggle           │
│  [V] Validate All                      [Enter] Proceed          │
│                                                                  │
│         [ Cancel ]                    [ Translate Selected ]    │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

#### 4.3.3 Key Validation Rules

| Rule | Check | Error Message |
|------|-------|---------------|
| Format | `^[a-z][a-z0-9_.]*[a-z0-9]$` | "Key must be lowercase with dots/underscores" |
| Length | 3-100 characters | "Key must be 3-100 characters" |
| Duplicate (local) | Not in current batch | "Duplicate key in batch" |
| Duplicate (remote) | Not in Crowdin project | "Key already exists in Crowdin" |
| Reserved | Not system reserved | "Reserved key name" |

#### 4.3.4 Validation Results

```
┌──────────────────────────────────────────────────────────────────┐
│  Validation Results                                              │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ✓ 4 keys valid and ready                                       │
│  ⚠ 1 key skipped (already exists)                               │
│  ✗ 1 key invalid (see errors below)                             │
│                                                                  │
│  Errors:                                                         │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ ✗ Dashboard.Title                                           ││
│  │   Error: Key must be lowercase with dots/underscores        ││
│  │   Suggestion: dashboard.title                               ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  [ Fix Errors ]                        [ Continue with Valid ]  │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

### 4.4 Feature 4: Enhanced Upload Workflow

#### 4.4.1 New Upload Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           UPLOAD WORKFLOW v1.1                          │
└─────────────────────────────────────────────────────────────────────────┘

                              ┌─────────────┐
                              │   Start     │
                              └──────┬──────┘
                                     │
                    ┌────────────────┴────────────────┐
                    ▼                                 ▼
            ┌──────────────┐                 ┌──────────────┐
            │  New Keys    │                 │ Load Draft   │
            │  (keys.txt)  │                 │              │
            └──────┬───────┘                 └──────┬───────┘
                   │                                │
                   ▼                                │
            ┌──────────────┐                        │
            │    Key       │                        │
            │  Manager     │ ◄── NEW                │
            │  (validate)  │                        │
            └──────┬───────┘                        │
                   │                                │
                   ▼                                │
            ┌──────────────┐                        │
            │   Gemini     │                        │
            │   Translate  │                        │
            └──────┬───────┘                        │
                   │                                │
                   └────────────────┬───────────────┘
                                    ▼
                            ┌──────────────┐
                            │   Preview    │ ◄── NEW
                            │   Screen     │
                            └──────┬───────┘
                                   │
                   ┌───────────────┼───────────────┐
                   ▼               ▼               ▼
            ┌──────────┐   ┌──────────────┐  ┌──────────┐
            │  Edit    │   │ Save Draft   │  │  Cancel  │
            └────┬─────┘   └──────────────┘  └──────────┘
                 │                 ▲
                 └─────────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │   Confirm    │
                    │   Upload     │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │   Upload to  │
                    │   Crowdin    │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │   Success    │
                    │   Summary    │
                    └──────────────┘
```

#### 4.4.2 Upload Confirmation Dialog

```
┌──────────────────────────────────────────────────────────────────┐
│  Confirm Upload to Crowdin                                       │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  You are about to upload:                                        │
│                                                                  │
│    • 4 new translation keys                                      │
│    • 28 translations (4 keys × 7 languages)                      │
│    • 2 manually edited translations                              │
│                                                                  │
│  Target:                                                         │
│    • Profile: default                                            │
│    • Project: 577773                                             │
│    • File: CommonResource                                        │
│                                                                  │
│  ⚠️  This action cannot be undone from Hermes.                   │
│     To remove keys, use Crowdin directly.                        │
│                                                                  │
│         [ Cancel ]                    [ Confirm Upload ]         │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

#### 4.4.3 Success Summary

```
┌──────────────────────────────────────────────────────────────────┐
│  ✓ Upload Complete                                               │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Summary:                                                        │
│  ────────────────────────────────────────────────────────────    │
│  Keys Added:        4 / 4  ✓                                     │
│  Translations:     28 / 28 ✓                                     │
│  Time Elapsed:     12.3 seconds                                  │
│                                                                  │
│  Breakdown by Language:                                          │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  zh-TW  ████████████████████  4/4  ✓                     │   │
│  │  zh-CN  ████████████████████  4/4  ✓                     │   │
│  │  en-US  ████████████████████  4/4  ✓                     │   │
│  │  ja-JP  ████████████████████  4/4  ✓                     │   │
│  │  th-TH  ████████████████████  4/4  ✓                     │   │
│  │  vi-VN  ████████████████████  4/4  ✓                     │   │
│  │  id-ID  ████████████████████  4/4  ✓                     │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  Draft file deleted: hermes-draft-2026-01-09-1430.json           │
│                                                                  │
│                                          [ Done ]                │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 5. CLI Enhancements

### 5.1 New Commands

```bash
# Preview translations without uploading
hermes upload --preview

# Save preview as draft
hermes upload --preview --save-draft ./my-draft.json

# Load and upload from draft
hermes upload --from-draft ./my-draft.json

# Validate keys only
hermes keys validate

# List keys with status
hermes keys list --check-crowdin

# Interactive key editor
hermes keys edit
```

### 5.2 Command Reference

| Command | Description | Options |
|---------|-------------|---------|
| `upload --preview` | Generate translations, show preview, don't upload | `--save-draft PATH` |
| `upload --from-draft` | Load draft and upload | `--skip-preview` |
| `keys validate` | Validate keys.txt format | `--fix` auto-fix issues |
| `keys list` | List keys to be uploaded | `--check-crowdin` verify against remote |
| `keys edit` | Interactive key editor | - |

### 5.3 Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Validation error (invalid keys) |
| 3 | Network error (Crowdin/Gemini unreachable) |
| 4 | Authentication error |
| 5 | User cancelled |

---

## 6. Technical Design

### 6.1 Architecture Changes

```
src/hermes/
├── core/
│   ├── config.py
│   ├── crowdin_api.py
│   ├── crowdin_upload_api.py
│   ├── file_operations.py
│   ├── draft_manager.py          # NEW - Draft save/load
│   └── key_validator.py          # NEW - Key validation
├── tui/
│   ├── app.py
│   ├── hermes.tcss
│   └── screens/
│       ├── main_menu.py
│       ├── settings.py
│       ├── download.py
│       ├── upload.py
│       ├── preview.py            # NEW - Translation preview
│       ├── key_manager.py        # NEW - Key management
│       └── draft_list.py         # NEW - Draft selection
└── cli.py                        # Enhanced with new commands
```

### 6.2 New Module: `draft_manager.py`

```python
class DraftManager:
    """Manage translation drafts"""
    
    def save_draft(
        self, 
        keys: list[TranslationKey],
        profile: str,
        path: str | None = None
    ) -> str:
        """Save current translations as draft, return path"""
        
    def load_draft(self, path: str) -> Draft:
        """Load draft from file"""
        
    def list_drafts(self, directory: str = "./drafts") -> list[DraftInfo]:
        """List available drafts"""
        
    def delete_draft(self, path: str) -> bool:
        """Delete a draft file"""
```

### 6.3 New Module: `key_validator.py`

```python
class KeyValidator:
    """Validate translation keys"""
    
    def validate_format(self, key: str) -> ValidationResult:
        """Check key format against rules"""
        
    def check_duplicates(self, keys: list[str]) -> list[str]:
        """Find duplicate keys in batch"""
        
    async def check_crowdin(
        self, 
        keys: list[str], 
        api: CrowdinAPI
    ) -> dict[str, KeyStatus]:
        """Check which keys exist in Crowdin"""
        
    def suggest_fix(self, key: str) -> str | None:
        """Suggest corrected key format"""
```

### 6.4 Data Models

```python
@dataclass
class TranslationKey:
    key: str
    translations: dict[str, Translation]
    status: KeyStatus  # NEW, EXISTS, INVALID

@dataclass  
class Translation:
    language: str
    ai_original: str
    current: str
    edited: bool
    
@dataclass
class Draft:
    version: str
    created_at: datetime
    updated_at: datetime
    profile: str
    project_id: str
    ai_model: str
    keys: list[TranslationKey]
    
@dataclass
class DraftInfo:
    path: str
    created_at: datetime
    key_count: int
    edited_count: int
    profile: str
```

### 6.5 Preview Screen State Machine

```
                    ┌─────────┐
                    │ Loading │
                    └────┬────┘
                         │
                         ▼
┌──────────┐       ┌─────────┐       ┌──────────┐
│ Editing  │◄─────►│ Viewing │◄─────►│ Confirm  │
└──────────┘       └────┬────┘       └──────────┘
                        │
              ┌─────────┼─────────┐
              ▼         ▼         ▼
        ┌─────────┐ ┌───────┐ ┌──────────┐
        │ Saving  │ │ Done  │ │ Uploading│
        │ Draft   │ │       │ │          │
        └─────────┘ └───────┘ └──────────┘
```

---

## 7. User Experience

### 7.1 Design Principles for v1.1

| Principle | Implementation |
|-----------|----------------|
| **Transparency** | Show all translations before upload |
| **Control** | User decides what gets uploaded |
| **Reversibility** | Save drafts, edit before commit |
| **Efficiency** | Keyboard-first, bulk operations |
| **Feedback** | Clear status at every step |

### 7.2 Accessibility

| Feature | Implementation |
|---------|----------------|
| Keyboard navigation | Full keyboard support, no mouse required |
| Screen reader | Semantic labels on all elements |
| Color contrast | WCAG AA compliance |
| Font scaling | Respects terminal font settings |

### 7.3 Error States

| Error | User Message | Recovery Action |
|-------|--------------|-----------------|
| AI translation failed | "Translation failed for {key}. Retry or enter manually." | Retry / Manual input |
| Network timeout | "Connection timed out. Check network and retry." | Retry button |
| Invalid key format | "Key '{key}' invalid: {reason}. Suggested: {fix}" | Auto-fix option |
| Draft corrupted | "Draft file corrupted. Start fresh or restore backup." | New / Backup |

---

## 8. Testing Strategy

### 8.1 Unit Tests

| Module | Test Coverage Target |
|--------|---------------------|
| `draft_manager.py` | 95% |
| `key_validator.py` | 95% |
| `preview.py` | 80% |
| `key_manager.py` | 80% |

### 8.2 Integration Tests

| Scenario | Test Case |
|----------|-----------|
| Full upload flow | New keys → Validate → Translate → Preview → Edit → Upload |
| Draft workflow | Save draft → Exit → Reload → Continue → Upload |
| Error recovery | Network fail mid-upload → Retry → Complete |
| Batch operations | 50 keys → Validate → Translate → Upload |

### 8.3 User Acceptance Tests

| Test | Pass Criteria |
|------|---------------|
| First-time user | Complete upload with preview in < 5 min |
| Edit translation | Find and edit error in < 30 sec |
| Draft save/load | Save, exit, reload, upload in < 2 min |
| Batch validation | Validate 20 keys with 3 errors in < 1 min |

---

## 9. Rollout Plan

### 9.1 Development Phases

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| **Phase 1** | 2 weeks | Key validation, Key manager screen |
| **Phase 2** | 3 weeks | Preview screen, Edit functionality |
| **Phase 3** | 2 weeks | Draft save/load, Draft list screen |
| **Phase 4** | 1 week | CLI enhancements |
| **Phase 5** | 1 week | Testing, bug fixes |
| **Phase 6** | 1 week | Documentation, release |

**Total: 10 weeks**

### 9.2 Release Strategy

| Stage | Audience | Duration | Goal |
|-------|----------|----------|------|
| Alpha | 2 internal users | 1 week | Core functionality validation |
| Beta | Full i18n team | 2 weeks | Workflow validation, feedback |
| GA | All users | - | Full release |

### 9.3 Feature Flags

| Flag | Default | Description |
|------|---------|-------------|
| `preview_enabled` | true | Enable preview screen |
| `draft_enabled` | true | Enable draft save/load |
| `key_validation_strict` | false | Strict validation mode |
| `crowdin_existence_check` | true | Check keys against Crowdin |

---

## 10. Success Metrics

### 10.1 Quantitative Metrics

| Metric | Baseline (v1.0) | Target (v1.1) | Measurement |
|--------|-----------------|---------------|-------------|
| Translation errors caught | 0% | 80% | Errors fixed in preview vs total |
| Upload confidence score | N/A | > 4.5/5 | Post-upload survey |
| Time to review | N/A | < 30s/key | Time tracking |
| Draft feature adoption | 0% | > 50% | Uploads using preview |
| Key validation saves | N/A | > 20/month | Invalid keys caught |

### 10.2 Qualitative Metrics

| Metric | Method | Frequency |
|--------|--------|-----------|
| User satisfaction | NPS survey | Monthly |
| Feature usefulness | In-app feedback | Per session |
| Pain points | User interviews | Bi-weekly during beta |

### 10.3 Success Criteria for GA

- [ ] Zero critical bugs
- [ ] All P0 features complete
- [ ] 90% positive feedback from beta users
- [ ] Documentation complete
- [ ] Performance within targets (< 2s screen load)

---

## 11. Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Preview slows workflow | Medium | Medium | Make preview skippable via flag |
| Draft files accumulate | Low | Low | Auto-cleanup after successful upload |
| AI cost increase | Low | Medium | Cache translations, batch requests |
| Complex UI overwhelms users | Medium | High | Progressive disclosure, good defaults |
| Crowdin API rate limits | Low | High | Request batching, backoff strategy |

---

## 12. Open Questions

| Question | Owner | Due Date | Status |
|----------|-------|----------|--------|
| Should drafts sync across team members? | PM | Jan 15 | Open |
| Max keys per batch upload? | Eng | Jan 12 | Open |
| Draft retention policy? | PM | Jan 15 | Open |
| Keyboard shortcut conflicts? | UX | Jan 10 | Open |

---

## 13. Appendix

### 13.1 Mockup Assets

See `/docs/mockups/v1.1/` for high-fidelity mockups.

### 13.2 API Changes

No Crowdin API changes required. All new features use existing endpoints.

### 13.3 Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| textual | >= 0.89.1 | TUI framework (existing) |
| pydantic | >= 2.0 | NEW - Draft schema validation |

### 13.4 Glossary

| Term | Definition |
|------|------------|
| Draft | Saved state of translations before upload |
| Preview | Screen showing translations for review |
| Key validation | Checking key format and existence |
| Batch operation | Processing multiple keys at once |

---

## 14. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 0.1 | 2026-01-09 | PM | Initial draft |

---

## 15. Approvals

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Product Manager | | | |
| Engineering Lead | | | |
| UX Designer | | | |
| QA Lead | | | |

---

*This PRD defines Hermes v1.1 requirements. All features subject to change based on user feedback and technical constraints.*
