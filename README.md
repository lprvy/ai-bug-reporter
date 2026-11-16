# 🤖 ai-bug-reporter

Turn messy bug notes into a clean, reproducible bug report, ready to paste into a GitHub issue.

[![tests](https://github.com/lprvy/ai-bug-reporter/actions/workflows/tests.yml/badge.svg)](https://github.com/lprvy/ai-bug-reporter/actions/workflows/tests.yml) [![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

```text
checkout crashes when i apply coupon          ## Checkout crashes when i apply coupon
1. login as test user                         **Severity:** 🟠 high
2. add 2 items to cart              ──▶       **Component:** checkout
3. go to checkout, enter SAVE10               ### Steps to reproduce
expected: 10% discount                        1. login as test user ...
actual: white screen, TypeError               ### Expected / ### Actual / ### Environment
chrome 131 on windows 11                      (+ ❓ questions when something is missing)
```

<details>
<summary>Full output for <code>examples/notes.txt</code> (offline engine)</summary>

```markdown
## Checkout crashes when i apply coupon

**Severity:** 🟠 high
**Component:** checkout
**Labels:** `auth`, `crash`, `payment`

### Steps to reproduce
1. login as test user
2. add 2 items to cart
3. go to checkout, enter SAVE10

### Expected
10% discount

### Actual
white screen, TypeError in console

### Environment
| | |
|---|---|
| Browser | Chrome 131 |
| OS | Windows 11 |
```

Nothing is missing here, so there are no follow-up questions. Leave out the expected result or the browser and the report ends with a **❓ Missing information** list instead.

</details>

## Two engines

| Engine | How | Needs |
|---|---|---|
| `offline` | Keyword and pattern rules: severity, steps, expected/actual, browser/OS/device, labels. Understands English and common Turkish phrasing. | Nothing |
| `claude` | Claude (`claude-opus-5-5`) with **structured outputs**: the reply is validated against the same Pydantic `BugReport` model. Told never to invent facts; anything missing becomes a question in `missing_info`. | `pip install ".[ai]"` + `ANTHROPIC_API_KEY` |

`--engine auto` (default) uses Claude when credentials are present and **falls back to the offline rules** if the API is unreachable or declines.

## Usage

```bash
pip install -e .            # offline only
pip install -e ".[ai]"      # with Claude

bugreport examples/notes.txt              # Markdown
bugreport examples/notes.txt -f json      # JSON
cat notes.txt | bugreport -e offline      # stdin, force offline
```

## Output schema

```python
class BugReport(BaseModel):
    title: str
    severity: Literal["low", "medium", "high", "critical"]
    component: str | None
    environment: Environment          # browser, os, device, app_version
    steps_to_reproduce: list[str]
    expected: str | None
    actual: str | None
    labels: list[str]
    missing_info: list[str]           # questions to ask the reporter
```

## Tests

```bash
pip install -e ".[ai,dev]" && pytest     # 32 tests, no network needed
ruff check .                              # lint (also runs in CI)
```

- rule engine: severity rules, step parsing (numbered lists and `a -> b -> c` chains), Turkish notes, truncation, OS name normalisation, whole-word keyword matching
- Claude engine: the SDK client is **mocked**; tests check the request shape (model, schema, fallbacks) and that refusals, truncated replies and empty input are handled
- CLI: file/stdin input, size limit, JSON/Markdown output, auto-fallback

## License

MIT
