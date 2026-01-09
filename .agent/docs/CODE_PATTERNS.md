# Code Pattern Rules

Mandatory coding standards for all contributors (human and AI) working on Hermes.

---

## Rule 1: No `else` Blocks

**If you need `else`, the function is structured incorrectly.**

Use early returns, guard clauses, or restructure the logic.

```python
# BAD - using else
def get_status(user):
    if user.is_active:
        return "active"
    else:
        return "inactive"

# GOOD - early return
def get_status(user):
    if user.is_active:
        return "active"
    return "inactive"
```

```python
# BAD - nested else
def process_order(order):
    if order.is_valid:
        if order.has_stock:
            return fulfill_order(order)
        else:
            return "out_of_stock"
    else:
        return "invalid_order"

# GOOD - guard clauses with early returns
def process_order(order):
    if not order.is_valid:
        return "invalid_order"
    
    if not order.has_stock:
        return "out_of_stock"
    
    return fulfill_order(order)
```

**Why:** 
- Reduces nesting and cognitive load
- Makes the "happy path" clear
- Forces you to handle edge cases first

---

## Rule 2: Keep Functions Simple

**Each function should do ONE thing.**

If a function is doing multiple things, split it.

```python
# BAD - function doing too much
def process_translation(key, text):
    # validate
    if not key or not text:
        raise ValueError("Invalid input")
    
    # translate
    response = gemini.translate(text)
    translated = response.text.strip()
    
    # save
    with open(f"{key}.json", "w") as f:
        json.dump({"key": key, "text": translated}, f)
    
    # upload
    crowdin.upload(key, translated)
    
    return translated

# GOOD - split into focused functions
def validate_input(key: str, text: str) -> None:
    if not key:
        raise ValueError("Key is required")
    if not text:
        raise ValueError("Text is required")

def translate_text(text: str) -> str:
    response = gemini.translate(text)
    return response.text.strip()

def save_translation(key: str, text: str) -> None:
    with open(f"{key}.json", "w") as f:
        json.dump({"key": key, "text": text}, f)

def process_translation(key: str, text: str) -> str:
    validate_input(key, text)
    translated = translate_text(text)
    save_translation(key, translated)
    crowdin.upload(key, translated)
    return translated
```

**Guidelines:**
- Function should fit on one screen (~20-30 lines max)
- If you need comments to explain sections, split into functions
- Function name should fully describe what it does

---

## Rule 3: Prefer Pure Functions

**Pure functions:** same input → same output, no side effects.

```python
# IMPURE - modifies external state
total = 0
def add_to_total(value):
    global total
    total += value
    return total

# PURE - no side effects
def add(a: int, b: int) -> int:
    return a + b
```

```python
# IMPURE - depends on external state
def get_greeting():
    hour = datetime.now().hour
    if hour < 12:
        return "Good morning"
    return "Good afternoon"

# PURE - explicit dependency
def get_greeting(hour: int) -> str:
    if hour < 12:
        return "Good morning"
    return "Good afternoon"
```

**When impure is acceptable:**
- I/O operations (file, network, database)
- UI updates
- Logging

**Keep impure functions at the edges**, with pure logic in the core.

```
┌─────────────────────────────────────────┐
│           Impure Shell                  │
│  ┌───────────────────────────────────┐  │
│  │         Pure Core                 │  │
│  │                                   │  │
│  │   • Business logic               │  │
│  │   • Data transformation          │  │
│  │   • Validation                   │  │
│  │                                   │  │
│  └───────────────────────────────────┘  │
│                                         │
│  • File I/O                            │
│  • API calls                           │
│  • User input                          │
└─────────────────────────────────────────┘
```

---

## Rule 4: No Magic Numbers or Strings

**Every literal value must have a named constant.**

```python
# BAD - magic numbers
def calculate_timeout(retries):
    return retries * 1000 + 5000

def get_status_color(status):
    if status == "success":
        return "#00ff00"
    return "#ff0000"

# GOOD - named constants
RETRY_INTERVAL_MS = 1000
BASE_TIMEOUT_MS = 5000

STATUS_SUCCESS = "success"
COLOR_SUCCESS = "#00ff00"
COLOR_ERROR = "#ff0000"

def calculate_timeout(retries: int) -> int:
    return retries * RETRY_INTERVAL_MS + BASE_TIMEOUT_MS

def get_status_color(status: str) -> str:
    if status == STATUS_SUCCESS:
        return COLOR_SUCCESS
    return COLOR_ERROR
```

**Constant organization:**

```python
# constants.py or at top of module

# Timeouts (milliseconds)
TIMEOUT_API_CALL_MS = 30000
TIMEOUT_BUILD_POLL_MS = 5000
TIMEOUT_UPLOAD_MS = 60000

# Retry settings
MAX_RETRIES = 3
RETRY_BACKOFF_FACTOR = 2

# Status codes
STATUS_SUCCESS = "success"
STATUS_PENDING = "pending"
STATUS_FAILED = "failed"

# API endpoints
CROWDIN_API_BASE = "https://api.crowdin.com/api/v2"
GEMINI_MODEL = "gemini-2.0-flash"

# File paths
DEFAULT_KEYS_FILE = "keys.txt"
DEFAULT_CONFIG_FILE = "hermes.config.json"
```

**Why:**
- Single source of truth
- Easy to find and modify
- Self-documenting code
- Prevents typos

---

## Rule 5: Try-Catch Only at Leaf Functions

**`try-catch` should only appear in "end" functions that don't call other functions.**

This prevents try-catch from scattering throughout the codebase.

```python
# BAD - try-catch in orchestration function
def upload_translations(keys):
    try:
        for key in keys:
            try:
                translation = translate(key)
                try:
                    save(translation)
                except IOError as e:
                    log.error(f"Save failed: {e}")
            except TranslationError as e:
                log.error(f"Translation failed: {e}")
    except Exception as e:
        log.error(f"Upload failed: {e}")

# GOOD - try-catch only in leaf functions
def read_file(path: str) -> str | None:
    """Leaf function - handles its own errors"""
    try:
        with open(path) as f:
            return f.read()
    except IOError:
        return None

def call_api(url: str) -> dict | None:
    """Leaf function - handles its own errors"""
    try:
        response = requests.get(url, timeout=TIMEOUT_API_CALL_MS)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return None

def upload_translations(keys: list[str]) -> UploadResult:
    """Orchestration function - no try-catch, uses return values"""
    results = []
    
    for key in keys:
        translation = translate(key)
        if translation is None:
            results.append(Result(key, success=False, error="translation_failed"))
            continue
        
        saved = save(translation)
        if not saved:
            results.append(Result(key, success=False, error="save_failed"))
            continue
        
        results.append(Result(key, success=True))
    
    return UploadResult(results)
```

**Error handling strategy:**

| Layer | Error Handling |
|-------|----------------|
| Leaf functions (I/O, API) | `try-catch`, return `None` or `Result` type |
| Core logic | Check return values, propagate errors up |
| Entry points (CLI, TUI) | Final `try-catch` for unexpected errors |

```
┌─────────────────────────────────────────┐
│  Entry Point (CLI/TUI)                  │
│  └─ Final try-catch for crashes         │
├─────────────────────────────────────────┤
│  Orchestration Layer                    │
│  └─ NO try-catch                        │
│  └─ Check return values                 │
│  └─ Propagate errors via Result types   │
├─────────────────────────────────────────┤
│  Leaf Functions (I/O, Network)          │
│  └─ try-catch allowed                   │
│  └─ Return None or Result on failure    │
└─────────────────────────────────────────┘
```

**Benefits:**
- Errors are handled once, at the source
- Orchestration code stays clean
- Error flow is predictable
- Easier to test

---

## Rule 6: Maximum 3 Levels of Nesting

**No function may have more than 3 levels of indentation.**

Count from the function body as level 1.

```python
# BAD - 5 levels of nesting
def process_data(items):
    for item in items:                        # Level 1
        if item.is_valid:                     # Level 2
            for sub in item.children:         # Level 3
                if sub.active:                # Level 4
                    if sub.value > 0:         # Level 5 ❌ TOO DEEP
                        handle(sub)

# GOOD - extract to separate functions
def should_process(sub) -> bool:
    if not sub.active:
        return False
    return sub.value > 0

def process_children(children):
    for sub in children:                      # Level 1
        if should_process(sub):               # Level 2
            handle(sub)

def process_data(items):
    for item in items:                        # Level 1
        if not item.is_valid:                 # Level 2
            continue
        process_children(item.children)       # Level 2
```

```python
# BAD - nested conditions
def get_discount(user, order):
    if user:                                  # Level 1
        if user.is_member:                    # Level 2
            if order.total > 100:             # Level 3
                if order.has_coupon:          # Level 4 ❌ TOO DEEP
                    return 0.3
                return 0.2
            return 0.1
    return 0

# GOOD - early returns flatten the structure
def get_discount(user, order) -> float:
    if not user:                              # Level 1
        return 0
    
    if not user.is_member:                    # Level 1
        return 0
    
    if order.total <= 100:                    # Level 1
        return 0.1
    
    if order.has_coupon:                      # Level 1
        return 0.3
    
    return 0.2
```

**Counting levels:**

```python
def example():
    │
    ├─ Level 1: for, if, while, with, try
    │   │
    │   ├─ Level 2: nested for, if, while, with
    │   │   │
    │   │   ├─ Level 3: MAX ALLOWED ✓
    │   │   │   │
    │   │   │   └─ Level 4: TOO DEEP ❌
```

**Strategies to reduce nesting:**

| Problem | Solution |
|---------|----------|
| Nested if-else | Early returns / guard clauses |
| Nested loops | Extract inner loop to function |
| Callback hell | Use async/await or extract functions |
| Complex conditions | Extract to named boolean function |

**Why:**
- Deep nesting is hard to read and debug
- Forces you to break down complex logic
- Each function stays focused
- Easier to test individual pieces

---

## Summary Checklist

Before submitting code, verify:

- [ ] No `else` blocks - used early returns instead
- [ ] Functions are small and do one thing
- [ ] Pure functions where possible
- [ ] No magic numbers or strings - all named constants
- [ ] `try-catch` only in leaf functions
- [ ] Maximum 3 levels of nesting

---

## Examples in Hermes Codebase

### Good Pattern Locations
*(To be updated as codebase is refactored)*

### Anti-Pattern Locations to Refactor
*(To be updated during code review)*
