# Tests

## `test_openwebui_compat.py`

Detects incompatibilities between Fileshed and Open WebUI's internal models API.

```sh
python3 tests/test_openwebui_compat.py                # check Fileshed.py
python3 tests/test_openwebui_compat.py path/to/file   # check a candidate file
```

Exit code is 0 when everything passes, 1 otherwise. No test framework, no
network, no fixtures to install. `pydantic` is used when present and stubbed
otherwise, so the checks run outside an Open WebUI environment.

### Why this exists

Open WebUI 0.9.0 turned its models layer (`Files`, `Groups`, ...) into coroutine
functions. Calling one without awaiting returns a coroutine object: the database
operation silently never happens, and a coroutine is truthy, so `if not result:`
guards do not catch it.

That is how [issue #8](https://github.com/Fade78/Fileshed/issues/8) presented:
`shed_link_create()` reported success and returned a well-formed URL, but the
row was never written, so opening the link returned Open WebUI's 404,
`{"detail":"We could not find what you're looking for :/"}`. Nothing failed at
the point of the mistake — which is precisely why it needs a test.

### What it checks

| | |
|---|---|
| **A. Static** | Every `Files`/`Groups` call in the source goes through `_owui_call()`, and no call to a Fileshed coroutine method is left un-awaited. Catches a direct call added later even when no runtime path exercises it. |
| **B. Async runtime** | Fileshed driven against a fake Open WebUI 0.9+ API. Every coroutine the fake hands out is tracked; any left un-awaited is named and fails. Also asserts the database side effects actually happened. |
| **C. Sync runtime** | The same scenario against a fake pre-0.9 synchronous API, so compatibility with older deployments cannot regress. |
| **D. Live** | When run inside a real Open WebUI install, checks that every symbol Fileshed depends on still exists, reports whether each is sync or async, and verifies the fakes above still match the real signatures. Skipped elsewhere — it then self-checks that logic against the fake so it does not rot. |

### Adding an Open WebUI call

Route it through `await _owui_call(...)` and add its name to
`REQUIRED_FILES_METHODS` or `REQUIRED_GROUPS_METHODS`, plus a method on the
corresponding `Sync*` fake with the same signature as upstream. Check A fails on
a direct call; check D fails when a fake drifts from the real signature.

### Keeping the fakes honest

The fakes mirror Open WebUI 0.11.0. They are only as good as that snapshot, and
nothing outside a real install can tell you they have drifted — which is what
check D is for. Run this suite inside the target Open WebUI version before
release: that is the run where check D actually reports.
