# Known Bugs

Tracked bugs to fix before or during feature development.

---

## BUG-001: Gemini Error Displayed as Crowdin Error

**Status:** Open  
**Priority:** High  
**Found:** 2026-01-09  

### Description

When a request to Gemini AI fails during translation, the error message incorrectly shows it as a Crowdin error instead of a Gemini error.

### Expected Behavior

Error message should clearly indicate the source:
- "Gemini API error: {details}" for Gemini failures
- "Crowdin API error: {details}" for Crowdin failures

### Actual Behavior

Gemini errors are displayed as Crowdin errors, misleading users about the actual failure source.

### Impact

- Users may incorrectly troubleshoot Crowdin token/settings
- Delays in identifying the real issue (Gemini token, rate limit, etc.)
- Poor user experience

### Location

Likely in `src/hermes/core/crowdin_upload_api.py` - error handling during upload workflow.

### Fix Required

1. Separate error handling for Gemini and Crowdin API calls
2. Use distinct error messages for each service
3. Propagate correct error type to UI layer

---

## Type Safety Issues

From static analysis - lower priority but should be addressed:

| File | Line | Issue |
|------|------|-------|
| `crowdin_upload_api.py` | 162 | Potential `None.strip()` call |
| `download.py` | 242 | Optional token passed to required parameter |
| `upload.py` | 262, 299 | Optional token passed to required parameter |
