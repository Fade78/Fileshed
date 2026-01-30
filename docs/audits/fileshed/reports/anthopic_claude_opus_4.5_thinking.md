# Security Audit Report: Fileshed Tool

## Audit Metadata

| Field | Value |
|-------|-------|
| **Audited File** | `Fileshed.py` |
| **Declared Version** | 1.0.3 |
| **Target Environment** | OpenWebUI 0.4.0+ Tool |
| **Audit Date** | 2026-01-30 |
| **Auditor** | Claude Opus 4.5 (Anthropic) |

---

## Executive Summary

Fileshed is a persistent file storage tool designed for OpenWebUI that provides users with personal and collaborative storage zones. The tool exhibits a mature and deliberate security architecture with multiple layers of defense. The separation between public API (`shed_*` methods) and internal implementation (`_FileshedCore`) is well-designed for LLM safety. The codebase demonstrates awareness of common attack vectors (path traversal, command injection, ZIP bombs, SQL injection) and implements appropriate countermeasures.

The tool is approximately 9,000 lines of Python and handles filesystem operations, shell command execution, SQLite queries, network access, and multi-user collaboration—all within a sandboxed LLM-invoked context. This is an inherently high-risk surface area that has been handled with considerable care.

---

## Audit Axes

### 1. Architecture and Separation of Concerns

**Intent**: Prevent LLM from accessing internal implementation methods; maintain clear layering between public API and infrastructure.

**Behavior**: The tool uses a two-class architecture:
- `Tools` class: Contains only `shed_*` public methods visible to the LLM
- `_FileshedCore` class: Contains all internal implementation (`_exec_command`, `_validate_*`, `_resolve_*`, etc.)

OpenWebUI exposes all methods of the `Tools` class to LLMs. By moving internal logic to a separate `_FileshedCore` class instantiated as `self._core`, internal methods become inaccessible to the LLM.

**Strengths**:
- Clean separation prevents LLM from directly invoking `_exec_command()` or `_git_run()`
- All 38 public functions follow consistent naming convention (`shed_*`)
- Monolithic file ensures atomic deployment (no version mismatches between modules)
- `ZoneContext` dataclass centralizes zone-specific logic, reducing duplication

**Weaknesses/Residual Risks**:
- The `_core` attribute is still accessible via `self._core` from within `Tools` methods; a bug in a public method could expose internal functionality
- No runtime enforcement that only `shed_*` methods are called (relies entirely on OpenWebUI's method exposure mechanism)

**Assessment**: ★★★★★

---

### 2. Filesystem Access and Path Traversal Protection

**Intent**: Confine all filesystem operations to designated zone directories; prevent chroot escape.

**Behavior**: Multiple layers of path validation:
1. `_validate_relative_path()`: Blocks absolute paths, normalizes Unicode (NFC), validates `..` doesn't escape, checks zone-prefix duplication
2. `_resolve_chroot_path()`: Resolves paths, verifies final target stays within base directory, detects symlinks pointing outside chroot
3. `_validate_path_args()`: Validates command arguments for path escapes, distinguishes sed/grep expressions from paths

**Strengths**:
- Unicode normalization prevents homograph attacks
- Symlink escape detection walks each path component
- Zone-prefix check (`PATH_STARTS_WITH_ZONE`) catches common LLM mistakes (e.g., `Documents/Documents/file`)
- `.git` directory protected from direct manipulation
- Conversation-isolated Uploads zone (`{user}/Uploads/{conv_id}`)

**Weaknesses/Residual Risks**:
- TOCTOU between path validation and actual operation (mitigated but not eliminated)
- Race condition window between symlink check and file operation in high-concurrency scenarios
- `allow_zone_in_path=True` parameter could be misused if LLM is manipulated

**Assessment**: ★★★★☆

---

### 3. Command Execution and Argument Injection

**Intent**: Allow only safe shell commands; prevent shell injection and command chaining.

**Behavior**:
- Strict command whitelist (`WHITELIST_READONLY`, `WHITELIST_READWRITE`)
- Explicit blacklist for dangerous commands (`BLACKLIST_COMMANDS`: bash, python, sudo, nc, dd, etc.)
- Argument validation via `DANGEROUS_ARGS_PATTERN` blocks `;`, `|`, `&&`, `||`, `>`, `$(`, `` ` ``, etc.
- Uses `subprocess.run()` with list arguments (no shell=True)
- Resource limits via `preexec_fn` (memory limit, CPU time limit)
- Output truncation to prevent context pollution

**Strengths**:
- `subprocess.run()` with list args prevents shell interpretation
- Specific validation for dangerous commands:
  - `find -exec` blocked
  - `awk system()/getline` blocked
  - `tar --absolute-names` blocked
  - `ln` entirely blocked
- curl/wget require output file (`-o`/`-O`) to prevent stdout pollution
- Network commands controlled by valve (`network_mode`)
- Git subcommand whitelist with separate read/write/network categories

**Weaknesses/Residual Risks**:
- Pattern-based validation is defense-in-depth, not absolute protection
- Some commands (e.g., `sed -e`) accept complex expressions that could theoretically encode malicious operations
- `awk` validation relies on regex pattern matching; sophisticated bypass attempts may exist
- ffmpeg has extensive capabilities; the `FFMPEG_DANGEROUS_OPTIONS` list may not be exhaustive

**Assessment**: ★★★★☆

---

### 4. Network Access Control

**Intent**: Prevent unauthorized network access and data exfiltration.

**Behavior**: Three-tier network mode controlled by admin valve:
- `disabled` (default): No network commands
- `safe`: Downloads only (curl GET, wget, git clone/fetch/pull)
- `all`: Unrestricted (warning: enables exfiltration)

**Strengths**:
- Default is `disabled`—secure by default
- `safe` mode blocks curl upload options (`-d`, `-F`, `-T`, `--post-data`)
- Git push requires `network_mode=all`
- URL pattern detection blocks URLs in non-network commands
- ffmpeg output protocols (rtmp, rtsp, ftp, http upload) blocked in `safe` mode
- Network-capable commands (ffprobe, pandoc, magick) have URL validation

**Weaknesses/Residual Risks**:
- `network_mode=all` enables full exfiltration (documented risk, admin responsibility)
- DNS exfiltration or timing-based covert channels not addressed (out of scope for this tool class)
- Some edge cases in URL detection (e.g., custom protocols) may slip through

**Assessment**: ★★★★★

---

### 5. SQLite Security

**Intent**: Allow database queries while preventing file access outside chroot and code execution.

**Behavior**:
- Blocks `ATTACH DATABASE`, `DETACH`, `LOAD_EXTENSION` via pattern detection
- SQL comment stripping prevents bypass (`AT/**/TACH`)
- Optional `sqlite_readonly` valve restricts to SELECT only
- Parameterized queries supported (prevents SQL injection)
- Table name validation for CSV import
- MAX_SQL_ROWS limit (10,000) prevents memory exhaustion

**Strengths**:
- Dangerous operations blocked even in read-write mode
- Comment stripping is case-insensitive and handles both block and line comments
- CSV import validates table names against SQL injection
- Default limit of 10 rows for SELECT without LIMIT (context protection)

**Weaknesses/Residual Risks**:
- Pattern-based blocking could potentially be bypassed by novel encoding
- PRAGMA commands are allowed and could potentially leak information
- No whitelist approach for SQL (intentional per design rationale, but higher risk)

**Assessment**: ★★★★☆

---

### 6. Group Permission Model

**Intent**: Enable collaboration while maintaining file ownership and access control.

**Behavior**:
- Group membership verified via OpenWebUI Groups API
- Three write modes: `owner`, `group`, `owner_ro`
- Ownership stored in SQLite (`access_auth.sqlite`)
- File ownership tracked per (group_id, file_path)

**Strengths**:
- Integration with OpenWebUI's native group system
- Clear permission semantics (read/write/delete per mode)
- `owner_ro` provides true immutability (change mode first)
- Group ID validation prevents path traversal in group names
- Ownership record updates on rename/move

**Weaknesses/Residual Risks**:
- Group membership check is synchronous API call (no caching, potential latency)
- If OpenWebUI Groups API changes, tool may break
- Orphaned ownership records possible if files deleted outside tool

**Assessment**: ★★★★☆

---

### 7. Locking and Concurrency

**Intent**: Prevent data corruption during concurrent edits; support crash recovery.

**Behavior**:
- File-based locks using `os.open()` with `O_CREAT | O_EXCL` (atomic)
- Lock files contain JSON with `conv_id`, `user_id`, `locked_at`, `path`
- Lock expiration (`lock_max_age_hours`)
- Edit workflow: `lockedit_open` → `lockedit_overwrite` → `lockedit_save/cancel`
- Working copies in `editzone/{conv_id}/`

**Strengths**:
- Atomic lock acquisition prevents race conditions
- Conversation-scoped locks allow same user, different conversation distinction
- `shed_force_unlock()` and `shed_maintenance()` for recovery
- Lock ownership verification prevents unauthorized release

**Weaknesses/Residual Risks**:
- File locks unreliable across NFS/distributed filesystems (documented limitation)
- No distributed locking mechanism (Redis, database) for multi-instance deployments
- Corrupted lock files are handled but may result in lock theft

**Assessment**: ★★★☆☆

---

### 8. Archive Handling (ZIP Security)

**Intent**: Safe extraction of archives without ZIP bombs or path traversal.

**Behavior**:
- Magic bytes verification (not just extension)
- ZIP Slip prevention: all member paths validated against destination
- ZIP bomb protection:
  - Max decompressed size: 500 MB
  - Max file count: 10,000
  - Max compression ratio: 100:1
- Symlink check before `extractall()` (TOCTOU mitigation)
- First-level extraction only (nested ZIPs not auto-extracted)

**Strengths**:
- Comprehensive ZIP bomb detection
- Path traversal check for each archive member
- TOCTOU window minimized with symlink check immediately before extraction
- Clear documentation that nested ZIPs require explicit extraction

**Weaknesses/Residual Risks**:
- Ratio-based detection could theoretically be bypassed by carefully crafted archives
- tarfile handling not as rigorous (relies on `--no-same-owner` flag)

**Assessment**: ★★★★★

---

### 9. LLM Misuse Resistance and Guardrails

**Intent**: Help LLMs use the tool correctly; prevent misuse through manipulation.

**Behavior**:
- Extensive docstrings with examples for all 38 functions
- Structured error responses with `code`, `message`, `details`, `hint`
- `FUNCTION_HELP` dictionary with workflows, not_for, tips
- Zone-prefix validation catches common LLM mistakes
- Type coercion for robustness (falsy → empty list, etc.)
- Parameter validation with clear error messages showing received value and expected format

**Strengths**:
- Self-correcting errors minimize retry loops
- `howto` guides for common workflows (download, edit, csv_to_sqlite, etc.)
- Clear separation of workflows (Direct Write vs. Locked Edit)
- Line numbers start at 1 (not 0)—matches user expectations
- Warning when `position="at"` used incorrectly with text functions

**Weaknesses/Residual Risks**:
- Determined adversarial prompts could still manipulate LLM into misuse
- No rate limiting at tool level (depends on OpenWebUI)
- `allow_zone_in_path=True` is a footgun if LLM is tricked into using it

**Assessment**: ★★★★☆

---

### 10. Git Integration Security

**Intent**: Provide version control while preventing malicious repository exploitation.

**Behavior**:
- Git hooks neutralized on init and clone (`_neutralize_git_hooks`)
- Hooks directory removed and `core.hooksPath` set to `/dev/null`
- Subcommand whitelisting (read vs. write vs. network)
- Dangerous operations blacklisted: `gc`, `prune`, `filter-branch`

**Strengths**:
- Hook neutralization prevents code execution via malicious repos
- Network operations (clone, push) controlled by valve
- Author attribution preserves audit trail

**Weaknesses/Residual Risks**:
- Post-clone hook neutralization may not cover all attack vectors in repository content
- `.git` directory manipulation could theoretically enable attacks if tool has bugs
- `git config` commands not exhaustively validated

**Assessment**: ★★★★☆

---

### 11. Error Handling and Information Disclosure

**Intent**: Provide useful errors without exposing sensitive system information.

**Behavior**:
- `StorageError` class with structured fields
- No stack traces or internal paths in user-facing errors
- User IDs validated as UUIDs (prevents injection)
- Generic exception handlers return minimal information

**Strengths**:
- Consistent error structure across all functions
- No exposure of `storage_base_path` or internal UUIDs in errors
- Contextual help (`hint` field) guides correction

**Weaknesses/Residual Risks**:
- Some error messages may leak existence of files (FILE_NOT_FOUND vs. PERMISSION_DENIED)
- Exception swallowing (`except Exception:`) may hide bugs in production

**Assessment**: ★★★★☆

---

### 12. Resource Limits and Denial of Service Protection

**Intent**: Prevent resource exhaustion attacks.

**Behavior**:
- Per-user and per-group quotas
- Max file size limit
- Command timeout (default 30s, max 300s)
- Memory limit via `RLIMIT_AS`
- CPU time limit via `RLIMIT_CPU`
- Output truncation (`max_output_default`, `max_output_absolute`)
- CSV column limit (5,000)
- SQL row limit (10,000)

**Strengths**:
- Multi-layered DoS protection
- Real-time quota calculation (no stale cache)
- Resource limits applied via `preexec_fn`

**Weaknesses/Residual Risks**:
- `resource.setrlimit` may fail silently on some systems
- No I/O bandwidth limiting
- Quota calculation is O(n) files (intentional simplicity tradeoff)

**Assessment**: ★★★★☆

---

## Final Overall Assessment

| Axis | Weight | Rating |
|------|--------|--------|
| Architecture | High | ★★★★★ |
| Path Traversal | Critical | ★★★★☆ |
| Command Injection | Critical | ★★★★☆ |
| Network Control | High | ★★★★★ |
| SQLite Security | High | ★★★★☆ |
| Group Permissions | Medium | ★★★★☆ |
| Locking/Concurrency | Medium | ★★★☆☆ |
| ZIP Security | High | ★★★★★ |
| LLM Guardrails | High | ★★★★☆ |
| Git Security | Medium | ★★★★☆ |
| Error Handling | Medium | ★★★★☆ |
| Resource Limits | High | ★★★★☆ |

### **Final Rating: ★★★★☆ (4 out of 5)**

This is a well-engineered tool with a mature security posture. The architecture demonstrates clear understanding of the threat model (LLM-invoked filesystem tool) and implements appropriate defenses. The few weaknesses identified are either documented design tradeoffs or edge cases that would require sophisticated exploitation.

---

## Actionable Recommendations

### High Priority

1. **Distributed Locking**: For deployments with multiple OpenWebUI instances, implement optional Redis/database-backed locking. Document that file-based locks are single-instance only.

2. **Git Repository Content Scanning**: Consider scanning cloned repository content for additional malicious patterns (e.g., `.gitattributes` filter configurations) beyond just hooks.

3. **PRAGMA Restriction**: Consider adding `sqlite_pragma_whitelist` valve to restrict which PRAGMA commands are allowed (e.g., block `PRAGMA database_list`).

### Medium Priority

4. **Rate Limiting**: Implement per-user rate limiting at the tool level to prevent abuse even if OpenWebUI lacks this feature.

5. **Audit Logging**: Add optional logging (valve-controlled) for security-relevant operations (command execution, network access, group permission changes).

6. **Tarfile Hardening**: Apply similar rigor to tar extraction as ZIP (member path validation, size limits, ratio checks).

### Low Priority

7. **`allow_zone_in_path` Documentation**: Add prominent warning in docstrings that this parameter should only be used with explicit user confirmation.

8. **Error Differentiation**: Consider returning the same error for FILE_NOT_FOUND and PERMISSION_DENIED to prevent existence disclosure (security vs. usability tradeoff).

9. **Async Locking**: Consider `aiofiles` or async lock primitives for better performance in async context.

---

## Conclusion

Fileshed demonstrates security-conscious design appropriate for a tool operating in a high-risk LLM environment. The multi-layered defense approach, clear separation of concerns, and comprehensive input validation make it suitable for production deployment with appropriate administrator configuration. The documented limitations (single-instance locking, `network_mode=all` risks) are honest and allow operators to make informed decisions.

The code quality and documentation suggest experienced authorship with awareness of both security and LLM-specific challenges. The tool is recommended for use in environments where administrators understand the valve configurations and the inherent risks of LLM-invoked filesystem operations.

