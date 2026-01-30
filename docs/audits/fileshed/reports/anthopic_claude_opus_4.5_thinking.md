# Security, Architecture, and Reliability Audit Report

## Audit Target

| Attribute | Value |
|-----------|-------|
| **Filename** | `Fileshed.py` |
| **Version** | 1.0.3 |
| **Required OpenWebUI Version** | 0.4.0+ |
| **Lines of Code** | ~8,745 |
| **Author** | Fade78 (with Claude Opus 4.5) |
| **License** | MIT |

---

## Executive Summary

Fileshed is a comprehensive, monolithic OpenWebUI Tool providing persistent file storage, command execution, SQLite database access, ZIP handling, and multi-user group collaboration features. The tool operates within OpenWebUI's tool execution environment and implements a defense-in-depth security model. The design demonstrates significant security awareness, but several areas require attention, particularly around edge cases in pattern-based validation and the inherent risks of shell command exposure to LLMs.

---

## Axis 1: Architecture and Separation of Concerns

### Key Strengths
- **Clear internal/external boundary**: The `_FileshedCore` class containing all internal logic is properly isolated from `shed_*` public methods. OpenWebUI's architecture only exposes methods on the `Tools` class, preventing LLMs from calling internal methods directly.
- **Centralized zone resolution**: The `_resolve_zone()` method provides a single point for all zone validation, ensuring consistent access control across all operations.
- **Layered execution model**: Git operations go through `_git_run()`, command execution through `_exec_command()`, and database operations through `_db_execute()`, creating clear abstraction layers.
- **Bridge pattern for OpenWebUI APIs**: `_OpenWebUIBridge` isolates version-specific imports, facilitating future compatibility.

### Weaknesses and Risks
- **Monolithic file complexity**: At 8,745 lines, the single-file design (justified for OpenWebUI installation simplicity) creates cognitive load and increases risk of inconsistent security patterns across the codebase.
- **No runtime interface enforcement**: The internal/external method boundary relies on naming convention (`_` prefix) rather than Python's limited access control mechanisms. While OpenWebUI respects this, there is no structural guarantee.

### Assessment: ★★★★☆

---

## Axis 2: LLM-Facing Surface Exposure

### Key Strengths
- **Comprehensive docstrings**: All `shed_*` functions include detailed parameter documentation, examples, and usage notes, reducing LLM hallucination risk.
- **Contextual error messages**: Errors include hints and link to relevant help topics via `FUNCTION_HELP`, helping LLMs self-correct.
- **Zone prefix protection**: `_validate_relative_path()` detects when an LLM incorrectly includes the zone name in paths (e.g., `Storage/file.txt` in `zone="storage"`), a common LLM mistake.
- **HOWTO documentation system**: The `shed_help(howto="...")` feature provides workflow guidance that helps LLMs understand correct usage patterns.

### Weaknesses and Risks
- **Allow overrides**: Parameters like `allow_zone_in_path=True` can be misused by a manipulated or confused LLM to bypass protections. While this is documented as an escape hatch, an adversarial prompt could convince the LLM to use it inappropriately.
- **Large API surface**: Over 35 `shed_*` functions create a broad attack surface. Each function represents a potential vector for prompt injection or misuse.

### Assessment: ★★★★☆

---

## Axis 3: Filesystem Access and Isolation

### Key Strengths
- **Chroot enforcement**: `_resolve_chroot_path()` prevents path traversal by resolving paths and verifying they remain within zone boundaries.
- **Symlink detection**: The method walks the path tree and validates symlink targets stay within the chroot, preventing symlink-based escapes.
- **Unicode normalization**: Paths are normalized to NFC form via `unicodedata.normalize()`, preventing Unicode canonicalization attacks.
- **Zone-based access control**: Four distinct zones (Uploads/read-only, Storage, Documents/Git-backed, Group) with appropriate permission models.
- **Protected path handling**: `.git` directories are protected from modification while still allowing Git commands.

### Weaknesses and Risks
- **TOCTOU window**: While symlink checks occur before operations, a race condition window exists between validation and actual file operations. The `shed_unzip` function explicitly addresses this with a final symlink check before `extractall()`, but other operations may be vulnerable.
- **Hardlink risk acknowledged**: The `ln` command is blocked entirely (good), but other tools like `cp --link` might still create hard links if available on the system.

### Assessment: ★★★★☆

---

## Axis 4: Command Execution and Input Validation

### Key Strengths
- **Strict whitelist approach**: Commands must be in `WHITELIST_READONLY` or `WHITELIST_READWRITE` to execute. Dangerous commands (shells, interpreters, network tools) are explicitly blacklisted.
- **Shell metacharacter blocking**: `DANGEROUS_ARGS_PATTERN` blocks `;`, `|`, `&`, backticks, `$(`, `${`, and output redirection characters.
- **Command-specific validation**:
  - `find`: `-exec`, `-execdir`, `-ok`, `-okdir` blocked
  - `awk`: `system()`, `getline |`, `ENVIRON` blocked
  - `tar`: `-P`/`--absolute-names` blocked
  - `git`: subcommand whitelisting with separate read/write/network lists
  - `curl/wget`: requires `-o` output flag, blocks upload options in safe mode
- **Resource limits**: `RLIMIT_AS` and `RLIMIT_CPU` are set via `preexec_fn` to prevent DoS.
- **Git hooks neutralization**: `_neutralize_git_hooks()` removes hooks and sets `core.hooksPath=/dev/null`, preventing malicious hook execution from cloned repos.

### Weaknesses and Risks
- **Pattern-based SQL blocking is bypassed easily**: The dangerous pattern check for SQL (`ATTACH`, `DETACH`, `LOAD_EXTENSION`) uses simple substring matching on uppercased queries:
  ```python
  for pattern in dangerous_patterns:
      if pattern in query_stripped:
  ```
  This can be bypassed with comments, e.g., `AT/**/TACH` or using SQLite's pragma mechanism.
  
- **AWK pattern bypass potential**: While `AWK_DANGEROUS_PATTERNS` blocks `system(` and `getline <`, creative awk constructs might evade detection.
  
- **Environment variable leakage**: While `env`, `printenv`, and `envsubst` are blocked, commands like `set` (if available) or awk's `ENVIRON` (blocked but via regex) could leak secrets. The regex `\bENVIRON\b` could be bypassed with Unicode lookalikes in some configurations.

- **Pipe character allowance**: Commands in `COMMANDS_ALLOWING_PIPE` (jq, awk, grep) use a relaxed pattern that allows `|`. While `subprocess.run()` with list arguments doesn't interpret shell syntax, this creates a documentation inconsistency where users might believe pipes work.

### Assessment: ★★★☆☆

---

## Axis 5: Network Access and Data Exfiltration Risks

### Key Strengths
- **Three-tier network model**: `disabled` (default), `safe` (downloads only), `all` (full access) provides granular control.
- **ffmpeg output protocol blocking**: In safe mode, protocols like `rtmp://`, `udp://`, `ftp://` are blocked to prevent streaming exfiltration.
- **curl/wget upload blocking**: POST/PUT-capable options (`-d`, `-F`, `-T`, `--data`, etc.) are blocked in safe mode.
- **Git push isolation**: `git push` requires `network_mode="all"`, preventing casual data exfiltration.
- **URL pattern detection**: Network access via ffmpeg, pandoc, imagemagick URLs is blocked unless network mode allows it.

### Weaknesses and Risks
- **DNS exfiltration vector**: With `network_mode="safe"`, curl can still perform DNS lookups. An attacker could encode data in DNS queries (e.g., `data.attacker.com`). This is a known limitation of network filtering.
- **Metadata exfiltration via HTTP headers**: While `-metadata` is blocked for ffmpeg in safe mode, curl's `--header` could potentially be used to exfiltrate small amounts of data in request headers to legitimate-looking URLs.
- **Safe mode still allows download from anywhere**: A malicious actor could direct the LLM to download malware or exploit payloads for later processing.

### Assessment: ★★★★☆

---

## Axis 6: Concurrency, Locking, and State Management

### Key Strengths
- **Atomic lock acquisition**: Uses `os.open()` with `O_CREAT | O_EXCL` for atomic file lock creation, preventing race conditions.
- **Lock ownership tracking**: Locks store `conv_id`, `user_id`, and timestamp in JSON, enabling ownership verification.
- **Lock expiration**: `lock_max_age_hours` valve allows stale locks to be cleaned via `shed_maintenance()`.
- **SQLite isolation**: Uses `isolation_level="IMMEDIATE"` for write operations, preventing concurrent modification issues.

### Weaknesses and Risks
- **Single-instance limitation acknowledged**: File locks don't work across NFS or distributed deployments. The design doc explicitly states this limitation.
- **No distributed coordination**: For multi-instance OpenWebUI deployments, race conditions could occur between different instances.
- **Lock cleanup relies on user action**: Stale locks require manual `shed_maintenance()` or `shed_force_unlock()` calls.

### Assessment: ★★★★☆

---

## Axis 7: Data Processing and Persistence

### Key Strengths
- **ZIP bomb protection**: Checks decompressed size (500MB max), file count (10,000 max), and compression ratio (100:1 max).
- **ZIP Slip prevention**: All archive members are validated to stay within the extraction directory.
- **Magic bytes verification**: ZIP files are validated by header, not just extension.
- **CSV column limit**: 5,000 column max prevents DoS via wide CSV files.
- **SQL parameterization**: The `params` argument enables parameterized queries to prevent injection.
- **Output truncation**: Command output is limited by `max_output_default`/`max_output_absolute` to prevent context pollution.

### Weaknesses and Risks
- **No recursive bomb protection**: Nested ZIP files are extracted as files (good), but the design doc notes this as intentional. However, if a user manually extracts nested ZIPs, each extraction consumes quota independently, which could be used for amplification attacks.
- **Memory consumption during CSV import**: Large CSV files are loaded into pandas DataFrame memory before SQLite insertion. For files approaching the quota limit, this could cause OOM conditions.

### Assessment: ★★★★☆

---

## Axis 8: Multi-User and Group Access Control

### Key Strengths
- **Per-file ownership model**: Group files track owner and write mode (`owner`, `group`, `owner_ro`) in SQLite.
- **Group membership validation**: Uses OpenWebUI's `Groups.get_groups_by_member_id()` to verify membership before access.
- **Explicit permission codes**: `FILE_OWNER_ONLY` and `FILE_READ_ONLY` provide clear feedback to users and LLMs.
- **Group quota isolation**: Separate quotas for users and groups prevent one user from exhausting shared space.

### Weaknesses and Risks
- **Ownership transfer validation**: While `shed_group_chown()` validates the new owner is a group member, there's no audit trail for ownership changes.
- **No fine-grained permissions**: The three-mode system (`owner`/`group`/`owner_ro`) is simple but doesn't support more complex ACLs that larger organizations might need.

### Assessment: ★★★★☆

---

## Axis 9: OpenWebUI Integration and API Stability

### Key Strengths
- **Bridge pattern**: `_OpenWebUIBridge` isolates version-specific API calls, making future updates easier.
- **Graceful degradation**: Groups features check `GROUPS_AVAILABLE` and fail gracefully if the API isn't present.
- **Version documentation**: Comments indicate tested version (0.6.40+) and minimum required version (0.4.0+).

### Weaknesses and Risks
- **Internal API dependency**: Heavy reliance on `open_webui.models.files` and `open_webui.models.groups` internal APIs that may change without notice.
- **Singleton pattern risk**: `_OpenWebUIBridge` uses a class-level singleton that could cause issues if OpenWebUI reloads tools dynamically.

### Assessment: ★★★☆☆

---

## Axis 10: Resistance to LLM Misuse and Manipulation

### Key Strengths
- **Defense against common LLM mistakes**: Zone prefix detection, comprehensive help system, and descriptive error messages reduce accidental misuse.
- **Read-only zone enforcement**: Uploads zone restrictions prevent LLMs from modifying user-uploaded files.
- **Timeout limits**: Both default and maximum timeouts prevent runaway commands.

### Weaknesses and Risks
- **Prompt injection via filenames**: If a user uploads a file with a malicious name containing shell metacharacters, the validation should catch it, but edge cases in path validation could be exploited.
- **LLM persuasion to use `allow_zone_in_path`**: An adversarial prompt could convince the LLM that the user "explicitly confirmed" wanting this override.
- **No rate limiting**: A compromised or manipulated LLM could issue thousands of commands in rapid succession, consuming resources.

### Assessment: ★★★☆☆

---

## Axis 11: Design Decision Consistency

### Observations

Reviewing the provided design decisions document against the implementation:

| Decision | Implementation | Verdict |
|----------|---------------|---------|
| No logging | ✓ Errors raised, not logged | Consistent |
| No cache for quota | ✓ `_check_quota()` recalculates each time | Consistent |
| ATTACH/DETACH/LOAD_EXTENSION blocked | ⚠ Simple substring match, bypassable | Partially implemented |
| No whitelist for SQL | ✓ `sqlite_readonly` valve for SELECT-only mode | Consistent |
| Magic bytes verification | ✓ Implemented in `shed_unzip` | Consistent |
| First-level ZIP extraction only | ✓ Nested ZIPs extracted as files | Consistent |
| Symlink check before extractall | ✓ Final check at line 5972 | Consistent |
| CSV column limit (5000) | ✓ Implemented with DoS rationale | Consistent |
| Explicit error codes | ✓ FILE_OWNER_ONLY, FILE_READ_ONLY distinct | Consistent |
| Only shed_* exposed | ✓ Architecture relies on OpenWebUI behavior | Consistent |
| Monolithic file | ✓ 8,745 lines in single file | Consistent |
| Command whitelist | ✓ Implemented with blacklist fallback | Consistent |
| printenv/envsubst removed | ✓ Not in whitelists | Consistent |
| File-based locks | ✓ O_CREAT\|O_EXCL atomic creation | Consistent |
| No distributed locks | ✓ Documented limitation | Acknowledged |
| OpenWebUI Bridge | ✓ `_OpenWebUIBridge` class exists | Consistent |

### Assessment: ★★★★☆

---

## Critical Findings Summary

### High Priority

1. **SQL blocking is bypassable**: The substring-based detection for `ATTACH`, `DETACH`, `LOAD_EXTENSION` can be bypassed with SQL comments or alternative syntax. Recommendation: Use SQLite's `PRAGMA` to disable dangerous features programmatically, or parse SQL properly.

2. **TOCTOU vulnerability window**: Between path validation and file operations, symlinks or files could be modified. For security-critical operations, consider using file descriptors instead of paths.

### Medium Priority

3. **No rate limiting**: Add per-user, per-conversation rate limits for command execution to prevent resource exhaustion.

4. **Memory consumption in CSV import**: Consider streaming CSV parsing for large files or implementing a size check before pandas load.

### Low Priority

5. **DNS exfiltration in safe mode**: Document this limitation or consider DNS-level controls in deployment guidance.

6. **Audit trail for ownership changes**: Consider logging ownership transfers for compliance needs.

---

## Final Overall Rating

| Weight | Axis | Rating | Weighted Score |
|--------|------|--------|----------------|
| 15% | Command Execution & Validation | ★★★☆☆ | 0.45 |
| 15% | Filesystem Isolation | ★★★★☆ | 0.60 |
| 15% | Network & Exfiltration | ★★★★☆ | 0.60 |
| 10% | LLM Surface Exposure | ★★★★☆ | 0.40 |
| 10% | Data Processing | ★★★★☆ | 0.40 |
| 10% | Concurrency & Locking | ★★★★☆ | 0.40 |
| 8% | Multi-User Access | ★★★★☆ | 0.32 |
| 7% | Architecture | ★★★★☆ | 0.28 |
| 5% | LLM Misuse Resistance | ★★★☆☆ | 0.15 |
| 5% | OpenWebUI Integration | ★★★☆☆ | 0.15 |

**Weighted Total: 3.75 / 5.0**

## Final Rating: ★★★★☆ (3.75/5)

### Justification

Fileshed demonstrates a mature security posture for an LLM-integrated tool, with well-considered defense-in-depth mechanisms across most axes. The architecture cleanly separates internal logic from the LLM-facing API, path validation is thorough with symlink detection, and network controls provide meaningful protection against data exfiltration.

The primary deductions stem from:
- Pattern-based security checks (SQL blocking, AWK patterns) that sophisticated attackers can bypass
- Inherent risks of exposing shell command execution to LLMs, even with whitelisting
- Some race condition windows in file operations

The tool is suitable for deployment in controlled environments where the LLM is trusted and users are authenticated. For high-security deployments, additional hardening (SQL statement parsing, sandboxed execution) would be recommended.
