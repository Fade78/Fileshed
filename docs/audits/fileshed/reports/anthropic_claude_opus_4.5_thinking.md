# Security Audit Report: Fileshed Tool

## Audited File
**Filename:** `Fileshed.py`  
**Version:** 1.0.5  
**Lines of Code:** ~9,143  
**Target Platform:** OpenWebUI 0.4.0+

---

## Executive Summary

Fileshed is a comprehensive file management tool designed to execute within OpenWebUI as an LLM-invokable tool. It provides persistent storage, multi-zone file management, group collaboration, shell command execution, and SQLite operations. The tool demonstrates significant security awareness in its design, with multiple defense-in-depth mechanisms. However, several architectural and security considerations merit attention.

---

## Audit Axes

### 1. Architecture and LLM Exposure Separation

**Intent:** Prevent the LLM from invoking internal methods directly by separating public API (`Tools.shed_*`) from implementation (`_FileshedCore`).

**Strengths:**
- Clean separation between `Tools` class (38 public `shed_*` methods) and `_FileshedCore` (internal implementation).
- OpenWebUI only exposes methods of the `Tools` class to the LLM, making `_FileshedCore` methods effectively inaccessible.
- Comprehensive docstrings with examples designed to help LLMs use the API correctly.
- Extensive inline warnings in code comments (lines 21-49) explicitly instructing LLMs not to call internal methods.
- `FUNCTION_HELP` dictionary (lines 578-977) provides contextual help that is returned with errors to guide LLM self-correction.

**Weaknesses/Limitations:**
- The separation relies entirely on OpenWebUI's behavior of only exposing `Tools` class methods. If OpenWebUI's introspection mechanism changes, internal methods could become exposed.
- The `_core` attribute is technically accessible via `self._core` from any `Tools` method; while this is intentional, it creates a single point of trust in OpenWebUI's isolation.

**Assessment:** ★★★★☆

---

### 2. Filesystem Access and Path Traversal Protection

**Intent:** Confine all file operations within designated zone directories (chroot-like isolation) and prevent escape attacks.

**Strengths:**
- `_resolve_chroot_path()` (lines 2011-2063) performs multi-layer validation:
  - Strips leading slashes
  - Walks path components checking for symlinks that escape chroot
  - Uses `Path.resolve()` to canonicalize and then verifies containment via `relative_to()`
- `_validate_relative_path()` (lines 2065-2129) adds:
  - Unicode normalization to NFC (prevents path confusion attacks)
  - Virtual resolution of `..` components to catch escape attempts
  - Detection of paths starting with zone names (common LLM mistake)
- Symlink detection before extraction in `shed_unzip()` (line 6283) provides TOCTOU protection.
- Explicit rejection of absolute paths in arguments (`_validate_path_args()` lines 2487-2546).
- `ln` command explicitly blocked (lines 2259-2269) to prevent hard/soft link attacks.

**Weaknesses/Limitations:**
- Race condition window between path validation and file operation (inherent to filesystem operations).
- No explicit checking for special device files (`/dev/*`) though this is implicitly handled by chroot confinement.
- Path validation logic is duplicated across multiple methods rather than centralized, increasing maintenance burden.

**Assessment:** ★★★★★

---

### 3. Command Execution and Argument Safety

**Intent:** Allow controlled shell command execution while preventing command injection and dangerous operations.

**Strengths:**
- Strict command whitelist system (`WHITELIST_READONLY`, `WHITELIST_READWRITE`) with ~100+ curated commands (lines 147-232).
- Explicit blacklist of dangerous commands (`BLACKLIST_COMMANDS` lines 300-317): shells, interpreters, privilege escalation tools, raw network tools.
- `DANGEROUS_ARGS_PATTERN` regex (line 325) blocks shell metacharacters: `; & | ` && || >> << > $( ${`.
- Separate pattern (`DANGEROUS_ARGS_PATTERN_ALLOW_PIPE`) for commands like `jq`, `awk`, `grep` that legitimately use `|` in their syntax.
- Git subcommand validation with separate whitelists for read/write/network operations (lines 234-255).
- Specific blocking of dangerous options:
  - `find -exec/-execdir/-ok/-okdir` (line 2237-2245)
  - `awk system()/getline pipes/ENVIRON` (lines 2249-2257)
  - `tar --absolute-names/-P` (lines 2272-2276)
- Resource limits via `preexec_fn` in subprocess (lines 2724-2741): memory limit (`RLIMIT_AS`), CPU time limit (`RLIMIT_CPU`).
- Timeout enforcement with configurable max (default 30s, max 300s).
- Commands are executed via `subprocess.run()` with list arguments (no shell interpretation).
- Removed dangerous commands: `xargs`, `timeout`, `env`, `printenv`, `envsubst` (documented in comments).

**Weaknesses/Limitations:**
- `subprocess.run()` with list arguments doesn't prevent all forms of argument injection (e.g., `--option=value` patterns could be exploited in some commands).
- `sed -i` is only blocked in readonly mode (line 2442); in write mode, it could be used for arbitrary file modification within the zone.
- The regex-based pattern detection is a defense-in-depth measure, not absolute protection. A sufficiently creative attack vector might bypass pattern matching.
- No explicit sandboxing (containers, namespaces) beyond the chroot-like path validation.

**Assessment:** ★★★★☆

---

### 4. Network Access and Data Exfiltration Controls

**Intent:** Provide granular control over network access to prevent unauthorized data exfiltration while allowing legitimate downloads.

**Strengths:**
- Three-tier `network_mode` valve: `disabled` (default), `safe`, `all` — controlled exclusively by administrators.
- `safe` mode specifically designed to block exfiltration:
  - `curl`/`wget`: GET-only operations enforced via `_validate_curl_args_get_only()` (lines 2209-2221).
  - `CURL_FORBIDDEN_GET_OPTS` blacklist (lines 261-272) blocks `-d`, `--data`, `-F`, `--form`, `-T`, `--upload-file`, `--post-data`, etc.
  - `git push` blocked in safe mode (lines 2569-2578).
  - `ffmpeg` output protocols blocked (`FFMPEG_OUTPUT_PROTOCOLS` lines 274-286): rtmp, rtsp, udp, tcp, ftp, http, tee.
  - `ffmpeg` dangerous options blocked (`FFMPEG_DANGEROUS_OPTIONS` lines 353-366): `-metadata`, `-filter_complex`, `-method`, `-headers`.
- Mandatory output file for `curl`/`wget` (lines 2666-2692) prevents stdout pollution and forces explicit file destination.
- URL pattern detection (`URL_PATTERN` line 341) blocks URLs in non-network commands when network is disabled.
- Network-capable commands (`ffprobe`, `pandoc`, `convert`, `identify`) allowed for local files but URLs blocked when network disabled.

**Weaknesses/Limitations:**
- Exfiltration via DNS tunneling or timing side-channels is not addressed (out of scope for this tool).
- `safe` mode trusts the URL parameter validation; a malicious URL could still download malicious content (acceptable risk).
- If `network_mode=all` is enabled by admin, full exfiltration is possible (documented as intentional).

**Assessment:** ★★★★★

---

### 5. SQLite Security and SQL Injection Protection

**Intent:** Provide safe SQLite database operations while preventing SQL injection and dangerous database commands.

**Strengths:**
- Parameterized queries via `params` argument (line 7129-7131) — proper SQL injection prevention.
- `sqlite_readonly` valve restricts to SELECT/PRAGMA/EXPLAIN only when enabled (lines 7637-7644).
- Dangerous command blocking (lines 7654-7673):
  - `ATTACH DATABASE` blocked (could access files outside scope).
  - `DETACH` blocked.
  - `LOAD_EXTENSION` blocked (could load arbitrary code).
- SQL comment stripping (`_strip_sql_comments()` lines 1838-1854) prevents bypass attacks like `AT/**/TACH` or `LOAD_EX--\nTENSION`.
- Table name validation for CSV import uses regex whitelist (line 7228): `^[a-zA-Z_][a-zA-Z0-9_]*$`.
- Column sanitization during CSV import (lines 7370-7376, 7441-7447) prevents SQL injection via column names.
- Row count limits (`MAX_SQL_ROWS = 10000` line 115) prevent memory exhaustion.
- Automatic retry with exponential backoff on transient errors (`_db_execute()` lines 3222-3261).
- Configurable journal mode (WAL, delete, truncate, memory) for NFS compatibility.

**Weaknesses/Limitations:**
- Dynamic table names in CSV import use string formatting with quotes (`f'"{table}"'`), but table name is already validated.
- No explicit protection against extremely long queries that could cause DoS (though SQLite has internal limits).
- The comment stripping regex handles common cases but might not catch all edge cases (e.g., nested comments on some SQL variants, though SQLite doesn't support nested comments).

**Assessment:** ★★★★★

---

### 6. ZIP Archive Security

**Intent:** Safely handle ZIP archives while preventing ZIP bombs and path traversal attacks.

**Strengths:**
- Magic bytes verification (line 6642-6650, 102-103) ensures file is actually a ZIP, not just renamed.
- ZIP bomb protection (lines 6254-6280):
  - Max decompressed size: 500 MB (`ZIP_MAX_DECOMPRESSED_SIZE`)
  - Max file count: 10,000 (`ZIP_MAX_FILES`)
  - Max compression ratio: 100:1 (`ZIP_MAX_COMPRESSION_RATIO`)
- Path traversal prevention (lines 6229-6251):
  - Absolute paths in ZIP rejected
  - Each member path resolved and verified to stay within destination
- Symlink check before extraction (line 6282-6289) prevents TOCTOU race condition.
- First-level extraction only — nested ZIPs extracted as regular files requiring explicit `shed_unzip()` call (documented in SPEC.md line 587).
- Cleanup on partial extraction failure (lines 6296-6315).

**Weaknesses/Limitations:**
- No protection against quine ZIPs (ZIP containing itself) though the compression ratio limit provides partial mitigation.
- Memory consumption during validation (reading all `infolist()` at once) could be problematic for archives with millions of entries at the 10k file limit.

**Assessment:** ★★★★★

---

### 7. Locking and Concurrency Control

**Intent:** Provide file locking to prevent data corruption during concurrent edits.

**Strengths:**
- Atomic lock acquisition using `os.open()` with `O_CREAT | O_EXCL` (lines 2906-2924) — proper exclusive file creation.
- Lock metadata stored in JSON includes conv_id, user_id, timestamp, and path.
- Lock ownership verification (`_check_lock_owner()` lines 2951-2967).
- Lock expiration configurable via `lock_max_age_hours` valve (default 24 hours).
- `shed_force_unlock()` function for crash recovery.
- `shed_maintenance()` function for cleaning expired locks.
- Group Git operations use `fcntl.flock()` (lines 3167-3183) to prevent concurrent commit corruption.
- Corrupted lock file handling — overwrites if JSON parsing fails.

**Weaknesses/Limitations:**
- File-based locks do not work reliably across NFS or multi-instance deployments (documented limitation in SPEC.md lines 612-615).
- Theoretical TOCTOU race between permission check and file write in group operations (documented and accepted in SPEC.md line 614).
- Personal Documents zone does not use Git lock — simultaneous commits may interleave (documented and accepted).
- No distributed locking mechanism (Redis, database) for multi-instance scenarios.

**Assessment:** ★★★★☆

---

### 8. Group Permission Model

**Intent:** Implement role-based file ownership within shared group spaces.

**Strengths:**
- Three-tier ownership model: `owner` (creator only), `group` (all members), `owner_ro` (read-only for all).
- Permission database (`access_auth.sqlite`) with proper schema and indexes (lines 3199-3213).
- Group membership validated against OpenWebUI Groups API (lines 3272-3305).
- Ownership transfer supported via `shed_group_chown()`.
- Mode changes supported via `shed_group_set_mode()`.
- Ownership records automatically updated on file rename/delete.
- Recursive ownership deletion for directory removal.
- SQL injection protection in ownership database queries via parameterized queries.

**Weaknesses/Limitations:**
- Group membership is checked at operation time; changes to group membership mid-operation could cause inconsistency (rare edge case).
- New owner validation in `shed_group_chown()` blocks dangerous characters but uses a simple character blacklist rather than UUID validation (line 8966).
- No audit trail for permission changes (ownership history not preserved, only Git commits).

**Assessment:** ★★★★☆

---

### 9. Input Validation and LLM Guardrails

**Intent:** Handle malformed LLM inputs gracefully and provide self-correcting error messages.

**Strengths:**
- Comprehensive type validation before operations:
  - `max_output` (line 2603-2608)
  - `timeout` (lines 3466-3472)
  - `line`, `end_line` (lines 3877-3909)
  - `offset`, `length` (lines 4237-4255)
  - `skip_rows` (lines 7195-7202)
- Falsy value coercion: empty strings/zeros for optional parameters silently converted to defaults (documented in SPEC.md lines 565-568).
- Detailed error messages include:
  - Parameter name
  - Received value with type
  - Expected format
  - Concrete example in hint
- `FUNCTION_HELP` dictionary provides contextual guidance on errors.
- Path prefix detection catches common LLM mistake of including zone name in path.
- `allow_zone_in_path` parameter for intentional override.

**Weaknesses/Limitations:**
- Very large string inputs (megabytes of content) could cause memory issues during validation (no explicit size check before processing in some functions).
- Error messages in some cases reveal internal structure (acceptable for LLM interaction but could leak info if exposed elsewhere).

**Assessment:** ★★★★★

---

### 10. Git Repository Security

**Intent:** Provide version control while preventing code execution via malicious repositories.

**Strengths:**
- Git hooks neutralization (`_neutralize_git_hooks()` lines 3142-3154):
  - Removes all hook files from cloned repositories
  - Sets `core.hooksPath` to `/dev/null` as defense-in-depth
- Git subcommand whitelisting prevents dangerous operations:
  - `gc`, `prune`, `filter-branch` always forbidden (`GIT_BLACKLIST` lines 245-247)
  - Network operations controlled by valves
- Git commits include user attribution for group operations (lines 3161-3183).
- Separate git locking (`fcntl.flock`) for group repos to prevent commit interleaving.

**Weaknesses/Limitations:**
- Git config manipulation could potentially be exploited (though path validation limits file access).
- No protection against repository size explosion (user quota limits provide indirect protection).
- Hook neutralization happens after `git init` but relies on immediate execution without race condition.

**Assessment:** ★★★★☆

---

### 11. Quota and Resource Management

**Intent:** Prevent resource exhaustion and ensure fair usage across users and groups.

**Strengths:**
- Per-user quota (`quota_per_user_mb`, default 1000 MB).
- Per-group quota (`quota_per_group_mb`, default 2000 MB).
- Per-file size limit (`max_file_size_mb`, default 300 MB).
- Output truncation limits (`max_output_default` 50KB, `max_output_absolute` 5MB).
- Memory limit for subprocesses (`exec_memory_limit_mb`, default 512 MB).
- CPU time limit for subprocesses (`exec_cpu_limit_seconds`, default 60s).
- CSV column limit (5000 columns) prevents DoS via wide files.
- SQL row limit (10,000 rows) prevents memory exhaustion.
- Hexdump length limit (4096 bytes).
- ZIP file limits (500MB decompressed, 10k files, 100:1 ratio).

**Weaknesses/Limitations:**
- Quota calculation is O(n) files and performed on every write (no caching, documented intentional design decision in SPEC.md line 572).
- Resource limits (`RLIMIT_*`) may not work on all systems (silently ignored on failure).
- No rate limiting on API calls (could be exploited for DoS via rapid tool invocations).

**Assessment:** ★★★★☆

---

### 12. Error Handling and Information Disclosure

**Intent:** Provide useful error information without leaking sensitive system details.

**Strengths:**
- Structured error format with code, message, details, and hint.
- Internal paths (UUIDs, absolute disk paths) not exposed in error messages.
- Generic "Unexpected error" messages for unhandled exceptions (lines like 4862-4863).
- No stack traces exposed to users/LLM.
- User-facing zone names (Storage, Documents, Uploads) used instead of internal paths.

**Weaknesses/Limitations:**
- No centralized logging (documented intentional decision in SPEC.md line 534).
- Some error hints reveal parameter expectations which could aid in crafting malicious inputs (acceptable for LLM tool usage).

**Assessment:** ★★★★★

---

### 13. OpenWebUI Integration Safety

**Intent:** Integrate safely with OpenWebUI internal APIs without creating security vulnerabilities.

**Strengths:**
- `_OpenWebUIBridge` class (lines 404-550) isolates all OpenWebUI API interactions.
- Singleton pattern prevents repeated imports.
- Lazy initialization with graceful fallback on import failure.
- User ID validation using UUID format check (line 1805).
- Conversation ID validation blocks path traversal characters (lines 1884-1891).
- Group ID validation prevents path traversal and control characters (lines 2131-2164).

**Weaknesses/Limitations:**
- Relies on OpenWebUI's `__user__` and `__metadata__` being trustworthy (reasonable assumption for tool execution context).
- API version coupling — relies on specific OpenWebUI 0.6.x API signatures.
- No explicit validation of file paths returned by OpenWebUI's Files API (trusts OpenWebUI).

**Assessment:** ★★★★☆

---

### 14. Download Link Security

**Intent:** Provide secure file download capabilities through OpenWebUI's file system.

**Strengths:**
- Uses OpenWebUI's internal Files API via Python bridge (no HTTP request deadlock risk).
- User ID attached to created files for ownership tracking.
- Files registered with proper metadata (content type, size).
- Deletion restricted to link creator (ownership check via `Files.get_file_by_id()`).
- Link listing filtered by user ID (only shows own links).

**Weaknesses/Limitations:**
- Download URLs are session-authenticated, not file-specific tokens (relies on OpenWebUI's session security).
- No automatic link expiration (files persist until explicitly deleted or cleaned).
- Metadata includes `fileshed_source` marker but relies on convention rather than cryptographic binding.

**Assessment:** ★★★★☆

---

## Overall Assessment

**Final Rating: ★★★★☆ (4 out of 5 stars)**

Fileshed demonstrates a mature security architecture with multiple defense-in-depth layers. The codebase shows clear security awareness in its design decisions, with explicit documentation of intentional tradeoffs (SPEC.md). The separation between public API and internal implementation, combined with comprehensive input validation and command whitelisting, creates a robust security posture appropriate for its intended use as an LLM-invokable tool.

The deduction from a perfect score reflects:
1. Inherent limitations of file-based locking for distributed deployments
2. Reliance on regex-based pattern matching for some security controls
3. Lack of explicit rate limiting
4. O(n) quota calculation without caching

These are documented design decisions with justified tradeoffs rather than security oversights.

---

## Actionable Recommendations

### High Priority
1. **Rate Limiting:** Consider implementing basic rate limiting on tool invocations to prevent DoS via rapid API calls, especially for resource-intensive operations like `shed_sqlite` or `shed_unzip`.

2. **Content Size Validation:** Add explicit size limits for string parameters (e.g., `content` in `shed_patch_text`) before processing to prevent memory exhaustion from very large inputs.

### Medium Priority
3. **Centralized Path Validation:** Refactor duplicated path validation logic into a single source of truth to reduce maintenance burden and potential for inconsistencies.

4. **Lock File Monitoring:** Consider adding telemetry or lightweight logging (optional valve) for lock acquisition/release events to aid debugging in production.

5. **Download Link Expiration:** Add optional automatic expiration for download links (configurable valve) to prevent accumulation of orphaned files.

### Low Priority
6. **UUID Validation for new_owner:** Strengthen `shed_group_chown` to validate `new_owner` as a proper UUID format rather than just blocking dangerous characters.

7. **Async Lock Acquisition:** Consider async-compatible locking for high-concurrency scenarios (current implementation uses blocking file operations).

8. **Quota Caching:** If performance becomes an issue at scale, consider implementing a bounded cache for quota calculations with explicit invalidation on writes.

---

## Conclusion

Fileshed is a well-engineered tool that appropriately balances security with functionality. Its design demonstrates thoughtful consideration of the unique threat model inherent in LLM-invokable tools—where the invoker (LLM) may be influenced by adversarial prompts but operates within a trusted execution environment (OpenWebUI). The extensive documentation in SPEC.md showing explicit consideration of security tradeoffs indicates a mature development process. The tool is suitable for production deployment with appropriate administrator oversight of valve configurations, particularly `network_mode`.
