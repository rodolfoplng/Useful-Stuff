# Regular Expressions Cheat Sheet (Regex)

A compact and **practical** guide to regular expressions with examples you can copy‑paste. Examples are shown in generic regex plus quick usage in **Python**.  
  

---  
  
## Quick Reference  
  
### Character Classes  
- `.` — any char (except newline unless DOTALL)
- `\d` — digit `[0-9]`
- `\D` — not digit
- `\w` — word char `[A-Za-z0-9_]` (engine-dependent re: Unicode)
- `\W` — not word char
- `\s` — whitespace (space, tab, newline, …)
- `\S` — not whitespace
- `[abc]` — a, b, or c
- `[^abc]` — not a, b, or c
- `[a-z]` — range
- `[a-zA-Z]` — multiple ranges
- `[\s\S]` — any char (common DOTALL workaround)

### Quantifiers  
- `?` — 0 or 1 (optional)
- `*` — 0 or more
- `+` — 1 or more
- `{m}` — exactly m
- `{m,}` — m or more
- `{m,n}` — between m and n
- `*?`, `+?`, `??`, `{m,n}?` — **lazy** (minimal) versions
- `*+`, `++`, `?+`, `{m,n}+` — **possessive** (no backtracking; not in all engines)

### Anchors & Boundaries  
- `^` — start of string/line (with MULTILINE)
- `$` — end of string/line (with MULTILINE)
- `\A` / `\Z` — absolute start/end of string
- `\b` — word boundary
- `\B` — not a word boundary

### Groups  
- `(abc)` — capturing group 1
- `(?:abc)` — **non‑capturing** group
- `(?P<name>abc)` — named group (Python)
- `\1`, `\2`, ... — backreference by number
- `\k<name>` — backreference by name (Python)

### Alternation  
- `a|b` — a or b
- Use **grouping**: `gr(a|e)y` → `gray` or `grey`

### Lookarounds  
- `(?=...)` — positive lookahead
- `(?!...)` — negative lookahead
- `(?<=...)` — positive lookbehind
- `(?<!...)` — negative lookbehind  
  
---  
  
## Common Patterns (Copy‑Paste Ready)

### 1) Email
```
\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b
```
- Add `i` / `re.I` to ignore case.

### 2) IPv4
```
\b(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)\b
```

### 3) ISO Date (YYYY‑MM‑DD) basic check
```
\b\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])\b
```

### 4) Hex Color (#RGB or #RRGGBB)
```
#(?:[0-9a-fA-F]{3}){1,2}\b
```

### 5) URL (simplified)
```
\bhttps?:\/\/[^\s/$.?#].[^\s]*\b
```

### 6) Slug / Identifier
```
^[a-z0-9]+(?:-[a-z0-9]+)*$
```

### 7) Password policy (≥8 chars, 1 upper, 1 lower, 1 digit)
```
^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$
```

### 8) Duplicated word (e.g., "the the")
```
\b(\w+)\s+\1\b
```

### 9) Trim extra spaces (capture + replace)
- **Find**: `\s+`
- **Replace**: single space `" "`
- Or use: `^\s+|\s+$` to trim ends

### 10) CSV line split respecting quotes (simple)
```
("(?:[^"]|"")*"|[^,]*)(?:,|$)
```

### 11) Numbers with optional decimals and sign
```
[+-]?(?:\d+(?:\.\d+)?|\.\d+)
```

---  
  
## Lookaround Recipes

- **Require suffix**: `\w+(?=\.csv\b)` → captures csv filename without `.csv`
- **Forbid suffix**: `\w+\.(?!exe\b)\w+` → file extensions not `.exe`
- **Capture if preceded by**: `(?<=ID:)\d+`
- **Negative lookbehind**: `(?<!\\)n` → `n` not preceded by backslash

---


## Substitutions (Search & Replace)

### Insert captured parts
- Find: `(\d{4})-(\d{2})-(\d{2})`
- Replace:
  - Python: `r"\3/\2/\1"` → `DD/MM/YYYY`
  

### Add comma to `1 0` → `1,0`
- Find: `(\d+)\s+(\d+)`
- Replace: `"\1,\2"` 

### Wrap words in `<b>`
- Find: `\b(\w+)\b`
- Replace: `<b>\1</b>`


---

## Validation vs Extraction

- **Validation**: anchor the whole string, e.g. `^[A-F0-9]{8}$`
- **Extraction**: use groups to capture parts, e.g. `ID:([A-F0-9]{8})`

---



## Quick Usage

### Python
```python
import re

# find all
emails = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)

# search one
m = re.search(r"(?m)^\d{4}-\d{2}-\d{2}$", line)
if m:
    print("date ok")

# substitute
new = re.sub(r"(\d{4})-(\d{2})-(\d{2})", r"\3/\2/\1", date)

# compile for reuse
pat = re.compile(r"(\w+)\s+\1")
if pat.search("the the"):
    print("dup word")
```


---


### Multi-line sample
```text
BEGIN
user: alice
email: alice@example.com
color: #1e90ff
END
```

- Block capture (dotall): `(?s)BEGIN(.*?)END`
- Extract email: `[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}`
- Extract hex color: `#(?:[0-9a-fA-F]{3}){1,2}\b`
