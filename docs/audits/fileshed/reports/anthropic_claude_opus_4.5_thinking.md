# Security Audit Report

**Audited File:** `Fileshed.py`  
**Tool Version:** 1.0.4  
**Required OpenWebUI Version:** 0.4.0+  
**Audit Date:** January 31, 2026

---

## Executive Summary

Fileshed is a mature, security-conscious OpenWebUI tool for persistent file management with multi-user collaboration. The implementation demonstrates substantial engineering effort in establishing defense-in-depth against both accidental misuse and adversarial LLM-driven attacks. The code reveals deliberate design choices that prioritize isolation, predictable behavior, and fail-safe defaults, with most critical attack surfaces well-protected through layered defenses.

---

## Axis 1: Architecture and API Surface Isolation

### Intent and Behavior

The tool employs a two-class architecture: `Tools` (public API) and `_FileshedCore` (internal implementation). This separation exploits OpenWebUI's convention of only exposing `Tools` class methods to the LLM, thereby hiding internal primitives like `_exec_command()`, `_resolve_chroot_path()`, and `_git_run()` from the model's callable interface.

### Strengths

- **Hard API boundary:** 38 public `shed_*` functions represent the only attack surface reachable by LLM-generated tool calls
- **No internal method exposure:** The `_FileshedCore` class pattern prevents the LLM from invoking validation-bypass methods
- **Monolithic file deployment:** Single-file architecture eliminates version mismatch risks between modules
- **Comprehensive docstrings:** Each public function includes parameter documentation and examples designed to guide LLM usage correctly

### Weaknesses

- The architecture relies on OpenWebUI's method discovery behavior; future OpenWebUI versions exposing underscore-prefixed methods would silently break this isolation
- No runtime verification that internal methods remain unexposed

### Assessment: ★★★★☆

---

## Axis 2: Filesystem Isolation and Path Traversal Defense

### Intent and Behavior

All file operations are constrained to user-specific or group-specific directories via `_resolve_chroot_path()`. The implementation employs multiple layers: input sanitization, Unicode normalization, symlink detection along path components, and post-resolution verification against the zone root.

### Strengths

- **Unicode normalization (NFC):** Prevents path confusion attacks using Unicode lookalikes (line 2064)
- **Symlink traversal detection:** Walks path components to detect and block symlinks pointing outside chroot (lines 2007-2030)
- **Both pre- and post-resolution checks:** Path escapes are detected via logical path analysis (virtual `..` resolution) AND `Path.resolve()` comparison
- **Zone prefix detection:** Catches common LLM mistakes where paths redundantly include zone names (e.g., `Storage/file.txt` in zone="storage")
- **Protected paths:** `.git` directories explicitly protected from deletion (line 4947-4948)

### Weaknesses

- TOCTOU window exists between path validation and file operation, though exploiting this requires filesystem-level race conditions
- Hard links within the storage root could theoretically reference sensitive files on the same filesystem (mitigated by blocking `ln` command)

### Assessment: ★★★★★

---

## Axis 3: Command Execution Security

### Intent and Behavior

Shell commands are executed via `subprocess.run()` with list arguments (no shell=True), constrained by whitelists (WHITELIST_READONLY/WHITELIST_READWRITE), a blacklist, and pattern-based argument validation.

### Strengths

- **No shell interpretation:** `subprocess.run()` with list arguments eliminates shell metacharacter injection
- **Layered validation:** Commands pass through whitelist check → blacklist check → command-specific validation (git subcommands, find options, awk patterns, tar flags) → argument pattern validation
- **Resource limits:** Memory (RLIMIT_AS) and CPU time (RLIMIT_CPU) limits enforced via `preexec_fn`
- **Network-capable command handling:** ffmpeg, pandoc, imagemagick have separate URL and protocol validation
- **Git hooks neutralization:** Cloned repositories have hooks removed and `core.hooksPath` set to `/dev/null`
- **Comprehensive dangerous pattern detection:** Shell metacharacters (`;|&`, backticks, `$(`, `${`) blocked via regex

### Weaknesses

- **Pattern-based validation is inherently incomplete:** Novel bypass techniques may exist for complex commands like `awk`
- **AWK ENVIRON blocking:** While `ENVIRON` is blocked, other awk data sources (e.g., reading arbitrary files) remain possible
- **tar --absolute-names blocking:** Only `-P` and `--absolute-names` are blocked; other tar options that could extract to unintended locations may exist

### Assessment: ★★★★☆

---

## Axis 4: SQLite Security

### Intent and Behavior

`shed_sqlite()` provides LLM-controlled SQL execution against user-owned databases. Security measures include blocking dangerous operations (ATTACH, DETACH, LOAD_EXTENSION), optional readonly mode, and comment stripping to prevent bypass attacks.

### Strengths

- **Comment stripping before pattern matching:** Prevents bypass attacks like `AT/**/TACH` (line 1822-1838)
- **Case-insensitive pattern detection:** Prevents `attach` vs `ATTACH` bypasses
- **Parameterized queries supported:** `params` argument enables safe value binding
- **Table name validation:** Regex validation prevents SQL injection in table names during CSV import
- **Context protection:** SELECT queries default to 10-row limit; explicit `output_csv` parameter for large exports
- **Readonly valve:** Admin can restrict to SELECT-only queries

### Weaknesses

- **No query whitelist:** Beyond the specific blocked patterns, arbitrary SQL (including complex recursive CTEs, triggers, views) is permitted
- **PRAGMA exposure:** While PRAGMA is allowed (needed for legitimate use), some PRAGMA commands could theoretically leak information
- **No row-level security:** Any query can access any data in the database file

### Assessment: ★★★★☆

---

## Axis 5: Network Access Controls

### Intent and Behavior

Network access is governed by the `network_mode` valve with three levels: `disabled` (default), `safe` (downloads only), and `all` (unrestricted). The implementation enforces these controls across curl/wget, git network subcommands, and protocol-capable multimedia tools.

### Strengths

- **Default-deny:** Network disabled by default
- **Exfiltration-aware "safe" mode:** Blocks POST/PUT/upload options for curl/wget, git push, and ffmpeg output protocols
- **Comprehensive protocol blocking:** ffmpeg output protocols (rtmp, ftp, http with method override) blocked in safe mode
- **URL detection in arguments:** Prevents indirect network access via tools like pandoc, imagemagick

### Weaknesses

- **Safe mode is not foolproof:** Novel exfiltration techniques via allowed tools may exist (e.g., timing-based, DNS tunneling if curl DNS queries are permitted)
- **Metadata exfiltration in "all" mode:** `network_mode=all` explicitly enables data exfiltration as documented, but the warning is only in the description string

### Assessment: ★★★★☆

---

## Axis 6: ZIP Archive Security

### Intent and Behavior

`shed_unzip()` provides ZIP extraction with protection against ZIP bombs and path traversal.

### Strengths

- **Magic bytes verification:** ZIP files verified by header, not just extension (line 6176)
- **ZIP bomb protection:** Decompressed size limit (500MB), file count limit (10,000), compression ratio limit (100:1)
- **Path traversal in archive:** Each member path validated against destination before extraction (lines 6218-6231)
- **Pre-extraction symlink check:** Final symlink verification on destination (TOCTOU mitigation) at line 6262
- **Nested ZIP handling:** Nested ZIPs extracted as files, not recursively decompressed (by design)
- **Cleanup on partial failure:** Rollback of extracted files on error

### Weaknesses

- **No streaming validation:** Files are validated by metadata before extraction, but malformed metadata could theoretically mismatch actual content
- **extractall() used:** Python's `extractall()` is used after validation, relying on prior member path checks

### Assessment: ★★★★★

---

## Axis 7: Locking and Concurrency

### Intent and Behavior

The locked edit workflow (`shed_lockedit_*`) uses file-based locks with atomic creation (`O_CREAT | O_EXCL`) and conversation isolation via editzones.

### Strengths

- **Atomic lock acquisition:** Uses `os.open()` with exclusive creation flags
- **Lock metadata:** Locks record conversation ID, user ID, and timestamp for diagnostics
- **Automatic cleanup:** `shed_maintenance()` cleans expired locks
- **Git commit locking:** Group repositories use `fcntl.flock()` for concurrent commit protection
- **Rollback on failure:** Lock released and editzone cleaned on operation failure

### Weaknesses

- **Single-instance assumption:** File locks are unreliable across NFS or multiple container instances (documented limitation)
- **Personal Documents no Git lock:** Acknowledged TOCTOU for personal Documents zone concurrent commits
- **Group permission TOCTOU:** Race condition between permission check and write operation (documented and accepted given Git versioning)

### Assessment: ★★★☆☆

---

## Axis 8: Group Permission Model

### Intent and Behavior

Group spaces use a permission database (`access_auth.sqlite`) with three modes per file: `owner` (creator-only write), `group` (all members write), `owner_ro` (read-only).

### Strengths

- **Group membership validation:** Uses OpenWebUI's Groups API for access control
- **Mode flexibility:** Three permission modes cover common collaboration patterns
- **Git versioning:** All group changes are Git-committed with user attribution
- **Ownership transfer:** `shed_group_chown()` allows ownership handoff
- **Parameterized DB queries:** Permission database uses parameterized queries

### Weaknesses

- **No hierarchical permissions:** Folder-level permissions not supported; each file tracked individually
- **New file creation open:** Any group member can create files (no create restriction mode)
- **Group name injection:** Group names resolved case-sensitively; no validation against special characters beyond path separators

### Assessment: ★★★★☆

---

## Axis 9: LLM Misuse Resistance

### Intent and Behavior

The tool includes extensive guardrails to prevent LLM-driven misuse: type coercion for falsy values, descriptive error messages with hints, workflow documentation in docstrings, and default-safe parameter values.

### Strengths

- **Self-correcting errors:** Error messages include parameter name, received value, expected format, and example (lines 549-560 in SPEC)
- **Contextual help system:** `_get_function_help()` provides workflow guidance on errors
- **Type guardrails:** Invalid types for numeric parameters raise explicit errors with parameter names
- **Falsy value handling:** Empty strings/zeros for optional lists coerced to safe defaults
- **Output truncation:** Large outputs truncated with hint to use file redirection

### Weaknesses

- **Complex function signatures:** Some functions (e.g., `shed_patch_text`) have 15+ parameters, increasing LLM confusion risk
- **Workflow state not enforced:** Nothing prevents an LLM from calling `shed_lockedit_save` without prior `shed_lockedit_open`

### Assessment: ★★★★☆

---

## Axis 10: Input Validation and Sanitization

### Intent and Behavior

All user-provided inputs undergo validation: user IDs (UUID format), group IDs (path character restrictions), paths (traversal prevention), commands (whitelist), arguments (dangerous patterns), SQL (blocked operations).

### Strengths

- **UUID validation:** User IDs validated against UUID regex pattern
- **Control character rejection:** Group IDs and conversation IDs reject characters with ord < 32
- **Consistent validation:** `_validate_relative_path()` used uniformly across all operations
- **Input length limits:** Owner IDs limited to 255 characters

### Weaknesses

- **No filename sanitization for display:** Error messages may include unsanitized paths (though not executable context)
- **Conversation ID fallback:** Invalid conversation IDs default to "unknown" rather than failing

### Assessment: ★★★★☆

---

## Axis 11: Resource Exhaustion Protection

### Intent and Behavior

Multiple mechanisms prevent denial-of-service: execution timeouts, memory limits, output truncation, quota enforcement, and CSV column limits.

### Strengths

- **Configurable limits:** All limits adjustable via valves (admin-controlled)
- **Multi-layer protection:** Command timeout (exec_timeout_max), subprocess memory limit (exec_memory_limit_mb), CPU time limit (exec_cpu_limit_seconds)
- **Output truncation:** Default 50KB output limit, absolute 5MB maximum
- **Storage quotas:** Per-user and per-group quotas with real-time enforcement
- **CSV protection:** 5000-column limit prevents memory exhaustion

### Weaknesses

- **No per-command resource profiles:** All commands share the same limits; a legitimate ffmpeg operation may need more resources than the limit allows
- **Quota calculation cost:** Real-time quota calculation (O(n) files) acknowledged as potential performance concern for large directories

### Assessment: ★★★★☆

---

## Axis 12: Error Handling and Information Disclosure

### Intent and Behavior

Errors use structured JSON responses with consistent format. Internal paths and system identifiers are not exposed to users.

### Strengths

- **Structured error format:** All errors return consistent JSON with code, message, details, hint
- **No path disclosure:** Zone roots and internal paths not exposed; only relative paths shown
- **Generic fallback errors:** `except Exception` blocks return generic messages without stack traces
- **No logging to files:** Errors raised to LLM, not logged (avoiding log management complexity)

### Weaknesses

- **Some detail leakage:** Command arguments in error messages could reveal internal patterns
- **No error rate limiting:** Repeated failures don't trigger escalating delays

### Assessment: ★★★★☆

---

## Final Overall Assessment

### Rating: ★★★★☆ (4 out of 5)

Fileshed demonstrates security-conscious design throughout, with layered defenses against the primary threats in an LLM-tool context: path traversal, command injection, resource exhaustion, and unauthorized data access. The architecture effectively hides internal methods from the LLM, and the implementation shows attention to edge cases like Unicode normalization, symlink traversal, and ZIP bombs.

The primary residual risks are:
1. **Concurrency in distributed deployments** (documented limitation)
2. **Pattern-based validation incompleteness** (inherent to whitelist/blacklist approaches)
3. **Complex function signatures** increasing LLM confusion potential

These are reasonable tradeoffs for the tool's scope and target environment.

---

## Actionable Recommendations

1. **Add runtime verification** that `_FileshedCore` methods are not exposed via OpenWebUI introspection (defensive check in `__init__`)

2. **Consider reducing function signature complexity** by splitting `shed_patch_text` into separate `shed_append`, `shed_insert_at`, `shed_replace_pattern` functions to reduce LLM parameter confusion

3. **Add workflow state validation** in `shed_lockedit_save`/`shed_lockedit_cancel` to verify a lock exists before attempting operations

4. **Document the "all" network mode warning** more prominently, potentially requiring explicit acknowledgment or a separate enable step

5. **Add rate limiting for errors** to slow down potential automated exploitation attempts via malicious prompts

6. **Consider adding SHA256 hash to lock files** to detect external file modifications during locked edits

7. **Add integration tests** for concurrency scenarios to validate lock behavior under race conditions
