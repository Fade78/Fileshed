# SPECIFICATION - Fileshed Tool

## Overview

Fileshed is an Open WebUI tool that allows users to store, manipulate, and organize their files persistently between conversations. The tool offers **three personal zones** for individual work plus **shared group spaces** for collaboration.

## Philosophy

### Personal space = Workshop

Your personal space is your **private workshop**. You can:

- Import files from chat (Uploads)
- Work freely with any file operation (Storage)
- Extract archives, run batch operations, experiment
- Keep versioned documents (Documents)

**It's okay to be messy here** — it's your space.

### Group space = Collaboration

Group spaces are for **sharing finalized documents** with your team. They are:

- **Documents only** (Git versioned)
- Clean and organized
- Collaborative with clear ownership

**Why no "Storage" in groups?**

- Each member already has personal Storage for messy work
- Group space is for publishing/collaborating on documents
- Avoids "who left this .tmp file?" issues
- Keeps collaboration focused

### Shell Commands First

Fileshed emphasizes using shell commands for all shell-doable operations:

```python
# ✅ CORRECT - use mkdir for directories
shed_exec(zone="storage", cmd="mkdir", args=["-p", "projects/2024"])

# ❌ WRONG - don't use patch_text to create directories
shed_patch_text(zone="storage", path="projects/2024/.keep", content="")
```

- **Reading files**: `shed_exec(cmd="cat/head/tail/sed", ...)`
- **Writing files**: `shed_patch_text()` (direct) or `shed_lockedit_*()` (with locking)

### Workflow

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Your Uploads   │────▶│  Your Storage   │────▶│  Group Space    │
│  (import)       │     │  (work)         │     │  (collaborate)  │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌─────────────────┐
                        │ Your Documents  │
                        │ (version)       │
                        └─────────────────┘
```

## Architecture

### Personal zones (3 zones per user)

```
{storage_base_path}/
├── users/                     # User personal spaces
│   └── {user_id}/
│       ├── Uploads/           # Import zone (read-only + delete)
│       │   └── {conv_id}/     # Isolated per conversation
│       │       └── files...
│       ├── Storage/           # Free zone (all operations)
│       │   ├── data/          # User files
│       │   ├── editzone/      # Temporary working copies
│       │   │   └── {conv_id}/
│       │   └── locks/         # Edit locks
│       └── Documents/         # Versioned zone (auto Git)
│           ├── data/          # Git repository
│           │   └── .git/
│           ├── editzone/
│           │   └── {conv_id}/
│           └── locks/
```

### Group zones (1 zone per group)

```
{storage_base_path}/
├── users/                     # User personal spaces
│   └── ...
├── groups/                    # Group shared spaces
│   ├── {group_id}/
│   │   ├── data/              # Git repository (Documents only)
│   │   │   └── .git/
│   │   ├── editzone/
│   │   │   └── {conv_id}/
│   │   └── locks/
│   └── {group_id_2}/
│       └── ...
└── access_auth.sqlite         # Permission database
```

### Paths

| Path | Description |
| --- | --- |
| `{storage_base_path}/` | Storage root |
| `{storage_base_path}/users/{user_id}/` | User personal space |
| `{user}/Uploads/{conv_id}/` | Import zone |
| `{user}/Storage/data/` | Free workspace |
| `{user}/Documents/data/` | Versioned documents |
| `{storage_base_path}/groups/{group_id}/data/` | Group documents |
| `{storage_base_path}/access_auth.sqlite` | Permission database |

## Code architecture

The tool follows a strict layered architecture for maintainability and security.

All internal methods are in a separate `_FileshedCore` class, preventing the LLM from seeing them.

```
┌─────────────────────────────────────────────────────────────────┐
│                  class Tools (PUBLIC API)                       │
│              async def shed_*() — 37 functions                  │
│                                                                 │
│  These are the ONLY functions visible to the LLM.               │
│  Handle: parameter validation, zone resolution, response format │
│  Access internal methods via: self._core._method()              │
├─────────────────────────────────────────────────────────────────┤
│               class _FileshedCore (INTERNAL)                    │
│        _exec_command()  _git_run()  _validate_*()               │
│        _format_response()  _resolve_zone()  _db_*()             │
│                                                                 │
│  Internal methods, NOT visible to LLM.                          │
│  Provide: subprocess wrapper, path validation, Git operations   │
│  Instantiated in Tools.__init__: self._core = _FileshedCore()   │
├─────────────────────────────────────────────────────────────────┤
│                  LAYER 3: INFRASTRUCTURE                        │
│        subprocess.run()    sqlite3    shutil    pathlib         │
│                                                                 │
│  External dependencies. Never called directly from Tools.       │
└─────────────────────────────────────────────────────────────────┘
```

**Why `_FileshedCore`?**

- Open WebUI exposes ALL methods of the `Tools` class to the LLM
- Without separation, LLM could see `_exec_command`, `_validate_path`, etc.
- LLMs sometimes attempted to call these internal methods directly
- Now only `shed_*` functions are visible to the LLM

**Critical rules:**

1. **Tools class calls _FileshedCore** — `self._core._exec_command()`, not `subprocess.run()`
2. **All paths use `_resolve_chroot_path()`** — Prevents path traversal attacks
3. **All user input is validated** — `_validate_command()`, `_validate_args()`, `_validate_relative_path()`

### Zone Resolution

The `_resolve_zone()` method centralizes all zone-specific logic and returns a `ZoneContext` dataclass:

```python
@dataclass
class ZoneContext:
    zone_root: Path          # Data directory path
    zone_name: str           # Canonical name (Storage, Documents, Uploads, Group:xxx)
    zone_lower: str          # Lowercase (storage, documents, uploads, group)
    editzone_base: Path      # Base for editzones (None for uploads)
    conv_id: str             # Conversation ID
    group_id: Optional[str]  # Group ID if zone=group, else None
    git_commit: bool         # Auto-commit after modifications
    readonly: bool           # True for uploads
    whitelist: set           # Allowed commands for this zone
```

Usage:

```python
ctx = self._core._resolve_zone(zone, group, __user__, __metadata__, require_write=True)
# Now use ctx.zone_root, ctx.git_commit, ctx.whitelist, etc.
```

### Key internal methods (in _FileshedCore)

| Method | Purpose |
| --- | --- |
| `_resolve_zone(zone, group, ...)` | Zone resolution, returns ZoneContext |
| `_exec_command(cmd, args, cwd, timeout)` | Subprocess wrapper with timeout, output truncation |
| `_git_run(args, cwd)` | Git operations for Documents zone versioning |
| `_validate_command(cmd)` | Whitelist check against `allowed_commands` |
| `_validate_args(args)` | Block dangerous patterns (`;`, ` |
| `_resolve_chroot_path(root, path)` | Resolve path within zone, prevent escape |
| `_format_response(success, data, message)` | Standardized JSON response format |

## API Design

### Unified Zone Parameter

All operations use a `zone=` parameter to specify the target zone:

```python
shed_exec(zone="storage", cmd="ls", args=["-la"])
shed_exec(zone="documents", cmd="git", args=["log"])
shed_exec(zone="uploads", cmd="cat", args=["file.txt"])
shed_exec(zone="group", group="team-alpha", cmd="ls", args=["-la"])
```

### Zone-Specific Parameters

Some parameters only apply to certain zones and are ignored otherwise:

| Parameter | Zones | Purpose |
| --- | --- | --- |
| `group` | group only | Required group identifier |
| `message` | documents, group | Git commit message |
| `mode` | group only | Ownership mode (owner, group, owner_ro) |

### Function Categories

**Core Operations (10 functions):**

- `shed_exec` — Execute shell commands (including reading files with cat/head/tail, stdout_file= for output redirection)
- `shed_patch_text` — Write/create text files (THE standard write function)
- `shed_patch_bytes` — Write binary data to files
- `shed_delete` — Delete files/folders
- `shed_rename` — Rename/move files
- `shed_lockedit_open` — Lock file for editing (locked edit workflow)
- `shed_lockedit_exec` — Run command on locked file
- `shed_lockedit_overwrite` — Overwrite locked file content
- `shed_lockedit_save` — Save changes and unlock
- `shed_lockedit_cancel` — Discard changes and unlock

**Zone-Aware Builtins (9 functions):**

- `shed_tree` — Directory tree view
- `shed_sqlite` — SQLite queries and CSV import
- `shed_zip` — Create ZIP archives
- `shed_unzip` — Extract ZIP archives
- `shed_zipinfo` — List ZIP contents
- `shed_file_type` — Detect file MIME type
- `shed_convert_eol` — Convert line endings
- `shed_hexdump` — Hex dump of binary files
- `shed_force_unlock` — Force unlock a stuck file

**Download Links (3 functions):**

- `shed_link_create` — Create download link (returns clickable_link in Markdown)
- `shed_link_list` — List your download links
- `shed_link_delete` — Delete a download link

**Group Functions (4 functions):**

- `shed_group_list` — List user's groups
- `shed_group_info` — Group details and members
- `shed_group_set_mode` — Change file permissions
- `shed_group_chown` — Transfer file ownership

**Zone Bridges (5 functions):**

- `shed_move_uploads_to_storage` — Move from Uploads to Storage
- `shed_move_uploads_to_documents` — Move from Uploads to Documents
- `shed_copy_storage_to_documents` — Copy from Storage to Documents
- `shed_move_documents_to_storage` — Move from Documents to Storage
- `shed_copy_to_group` — Copy to a group

**Utilities (6 functions):**

- `shed_import` — Import uploaded files
- `shed_help` — Documentation and guides
- `shed_stats` — Storage usage statistics
- `shed_parameters` — Configuration info
- `shed_allowed_commands` — List allowed shell commands
- `shed_maintenance` — Cleanup expired locks

**Total: 37 functions**

## Group permissions

### Access model

**Simple rule**: All members of an Open WebUI group can access the group's storage space.

Group membership is checked via Open WebUI's Groups API:

```python
from open_webui.models.groups import Groups

def _is_group_member(self, user_id: str, group_id: str) -> bool:
    """Check if user is member of group via Open WebUI API."""
    user_groups = Groups.get_groups_by_member_id(user_id)
    return any(g.id == group_id for g in user_groups)
```

### File ownership model

When a member uploads/creates a file in the group space, they choose the **write mode**:

| Mode | Description | Read | Write | Delete |
| --- | --- | --- | --- | --- |
| `owner` | I share but keep control | Everyone | Owner only | Owner only |
| `group` | Full collaboration | Everyone | Everyone | Everyone |
| `owner_ro` | I publish and protect | Everyone | Nobody | Nobody |

**Use cases:**

- `owner`: Share a template others can read but not modify
- `group`: Collaborative document everyone edits
- `owner_ro`: Finalized document (change mode first to modify or delete)

### Permission database (access_auth.sqlite)

```sql
-- File ownership in group spaces
CREATE TABLE file_ownership (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id TEXT NOT NULL,
    file_path TEXT NOT NULL,          -- Relative path in data/
    owner_id TEXT NOT NULL,           -- Who created/uploaded
    write_access TEXT NOT NULL        -- 'owner' | 'group' | 'owner_ro'
        CHECK(write_access IN ('owner', 'group', 'owner_ro')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(group_id, file_path)
);

CREATE INDEX idx_file_ownership_group ON file_ownership(group_id);
CREATE INDEX idx_file_ownership_owner ON file_ownership(owner_id);
```

## Security

### Command whitelist

Commands are separated into two whitelists:

**WHITELIST_READONLY** (for Uploads zone):

Reading: `cat`, `head`, `tail`, `less`, `more`, `nl`, `wc`, `stat`, `file`, `du`, `tac`
Navigation: `ls`, `tree`, `find`
Text search: `grep`, `egrep`, `fgrep`, `rg`, `awk`, `sed`
Text transformation: `sort`, `uniq`, `cut`, `paste`, `tr`, `fold`, `fmt`, `column`, `rev`, `shuf`, `expand`, `unexpand`, `pr`, `join`
Comparison: `diff`, `diff3`, `cmp`, `comm`
Archives (list): `tar`, `unzip`, `zipinfo`, `7z`
Compression (stdout): `zcat`, `bzcat`, `xzcat`
Checksums: `md5sum`, `sha1sum`, `sha256sum`, `sha512sum`, `b2sum`, `cksum`
Encoding: `base32`, `base64`, `basenc`
Binary/Hex: `strings`, `od`, `hexdump`, `xxd`
JSON/XML/YAML: `jq`, `xmllint`, `yq`
Misc: `iconv`, `bc`, `dc`, `expr`, `factor`, `numfmt`, `basename`, `dirname`, `realpath`, `echo`, `printf`
Media info: `ffprobe`, `identify`, `exiftool`
Database: `sqlite3`

**WHITELIST_READWRITE** (for Storage, Documents, Groups):

All of READONLY plus:
Additional reading: `df`, `locate`, `which`, `whereis`
Split: `split`, `csplit`
Additional comparison: `sdiff`, `patch`, `colordiff`
Archives: `zip`, `7za`
Compression: `gzip`, `gunzip`, `bzip2`, `bunzip2`, `xz`, `unxz`, `lz4`, `zstd`
Checksums: `sum`
Encoding: `uuencode`, `uudecode`
File modification: `touch`, `mkdir`, `rm`, `rmdir`, `mv`, `cp`, `truncate`, `mktemp`, `install`, `shred`, `rename`
Permissions: `chmod`
Document conversion: `pandoc`, `dos2unix`, `unix2dos`, `recode`
Misc: `seq`, `date`, `cal`, `readlink`, `pathchk`, `pwd`, `uname`, `nproc`, `sleep`, `yes`, `tee`, `gettext`, `tsort`, `true`, `false`
Media: `ffmpeg`, `magick`, `convert`
Versioning: `git`
Network (if enabled): `curl`, `wget`

### Forbidden patterns

The following patterns are blocked in all arguments:

- Shell metacharacters: `;`, `|`, `&&`, `&`, `>`, `>>`, `$(`, `` ` ``
- Path traversal: `..` (normalized away)
- Dangerous options: `find -exec`, `awk system()`, `xargs`

### Network modes

| Mode | Description |
| --- | --- |
| `disabled` | No network access (default) |
| `safe` | Downloads only (curl -o, wget -O, git clone) |
| `all` | Full network access (⚠️ enables data exfiltration) |

### Quotas

| Setting | Default | Description |
| --- | --- | --- |
| `quota_per_user_mb` | 1000 | Personal space limit |
| `quota_per_group_mb` | 2000 | Group space limit |
| `max_file_size_mb` | 300 | Maximum single file size |

## Configuration (Valves)

| Setting | Default | Description |
| --- | --- | --- |
| `storage_base_path` | `/app/backend/data/user_files` | Root storage path |
| `quota_per_user_mb` | 1000 | User quota in MB |
| `quota_per_group_mb` | 2000 | Group quota in MB |
| `max_file_size_mb` | 300 | Max file size |
| `lock_max_age_hours` | 24 | Lock expiration time |
| `exec_timeout_default` | 30 | Default command timeout (seconds) |
| `exec_timeout_max` | 300 | Maximum command timeout (seconds) |
| `exec_memory_limit_mb` | 512 | Memory limit for subprocesses (MB) |
| `exec_cpu_limit_seconds` | 60 | CPU time limit for subprocesses (seconds) |
| `group_default_mode` | `group` | Default write mode for new group files |
| `network_mode` | `disabled` | `disabled`, `safe`, or `all` |
| `openwebui_api_url` | `http://localhost:8080` | Open WebUI base URL for download links |
| `max_output_default` | 50000 | Default output truncation (~50KB) |
| `max_output_absolute` | 5000000 | Absolute max output (~5MB) |
| `sqlite_readonly` | `false` | Restrict SQLite to SELECT only |

## Error Handling

All errors use the `StorageError` class with structured JSON responses:

```python
class StorageError(Exception):
    def __init__(self, code: str, message: str, details: dict = None, hint: str = None):
        self.code = code
        self.message = message
        self.details = details or {}
        self.hint = hint
```

Response format:

```json
{
  "success": false,
  "error": {
    "code": "FILE_NOT_FOUND",
    "message": "File not found: config.json",
    "details": {"path": "config.json", "zone": "storage"},
    "hint": "Check the path and try again"
  }
}
```

### Error Codes Reference

| Code | Description |
| --- | --- |
| `FILE_NOT_FOUND` | Path does not exist |
| `FILE_EXISTS` | Destination already exists |
| `FILE_TOO_LARGE` | File exceeds max_file_size_mb limit |
| `FILE_LOCKED` | File locked by another user/conversation |
| `PATH_ESCAPE` | Path traversal or symlink escape attempt blocked |
| `INVALID_PATH` | Path is invalid for operation (e.g., zone root) |
| `PROTECTED_PATH` | Path is protected and cannot be modified (e.g., .git) |
| `PATH_STARTS_WITH_ZONE` | Path incorrectly starts with zone name (see howto="paths") |
| `PERMISSION_DENIED` | Group ownership check failed |
| `ACCESS_DENIED` | Access denied (e.g., not your download link) |
| `COMMAND_FORBIDDEN` | Command not in whitelist or network disabled |
| `ARGUMENT_FORBIDDEN` | Dangerous argument pattern or URL when network disabled |
| `ARGUMENT_REQUIRED` | Required argument missing (e.g., curl/wget need -o/-O) |
| `QUOTA_EXCEEDED` | Storage quota exceeded |
| `INVALID_ZONE` | Unknown zone parameter |
| `ZONE_FORBIDDEN` | Invalid zone for this operation |
| `ZONE_READONLY` | Write operation on read-only zone (Uploads) |
| `MISSING_PARAMETER` | Required parameter missing (including group for zone="group") |
| `INVALID_PARAMETER` | Invalid parameter value |
| `GROUP_ACCESS_DENIED` | User is not a member of the group |
| `NOT_A_FILE` | Expected file but found directory |
| `NOT_IN_EDIT_MODE` | File not open for locked editing |
| `NOT_A_FILESHED_LINK` | File was not created by Fileshed |
| `PATTERN_NOT_FOUND` | Regex pattern not found in file |
| `EXEC_ERROR` | Command execution failed |
| `TIMEOUT` | Command exceeded timeout |
| `INVALID_FORMAT` | Invalid file format for operation |
| `INVALID_OWNER` | Invalid owner ID for chown |
| `CSV_PARSE_ERROR` | Failed to parse CSV file |
| `TABLE_EXISTS` | SQLite table already exists (use if_exists) |
| `ZIP_BOMB` | ZIP file may be a decompression bomb |
| `NO_USER_ID` | User ID not available (internal error) |
| `INVALID_USER` | User ID is missing, empty, or invalid format |
| `INVALID_GROUP_ID` | Group ID contains forbidden characters |
| `INVALID_MODE` | Invalid write mode (not owner/group/owner_ro) |
| `DB_ERROR` | Database operation failed |
| `GROUP_NOT_FOUND` | Group not found by name |
| `GROUP_NOT_AVAILABLE` | Group features unavailable (API not found) |
| `INTERNAL_API_ERROR` | Internal API error |
| `NOT_FILE_OWNER` | User is not the file owner |
| `NOT_LOCK_OWNER` | User does not own the lock |
| `MISSING_FILE_ID` | File ID required but not provided |
| `LOCK_ERROR` | Failed to acquire lock |
| `CSV_EMPTY` | CSV file has no data rows |
| `CSV_TOO_WIDE` | CSV has too many columns (max 5000) |
| `COMMAND_NOT_FOUND` | Command not found on system |
| `GIT_NOT_AVAILABLE` | Git is not available on system |
| `EXECUTION_ERROR` | Command execution error |
| `OPENWEBUI_API_UNAVAILABLE` | Open WebUI internal API unavailable |
| `OPENWEBUI_INSERT_ERROR` | Failed to create download link |
| `OPENWEBUI_GET_ERROR` | Failed to retrieve file metadata |
| `OPENWEBUI_DELETE_ERROR` | Failed to delete download link |

## Response Format

All functions return JSON with consistent structure:

**Success:**

```json
{
  "success": true,
  "data": { ... },
  "message": "Operation completed"
}
```

**Error:**

```json
{
  "success": false,
  "error": { ... }
}
```

## Design Rationale

This section documents deliberate design decisions and their justifications. It helps auditors understand intentional trade-offs and avoid false positives.

### General Principles

- **No logging.** Errors are raised to the calling LLM, not logged to files. This keeps the system simple and avoids log management complexity.
- **No system data in errors.** Error messages never expose internal identifiers, UUIDs, or absolute disk paths. Only user-facing information is returned.
- **LLM-oriented documentation.** All functions include detailed docstrings and contextual error hints to help even small LLMs understand correct usage patterns.

### LLM Guardrails

Each tool call is expensive (API latency, token consumption, context pollution). The goal is to **minimize round-trips** between the LLM and the tool by making errors self-correcting.

**When documentation fails, error messages must succeed.**

An error response must include:
1. **The faulty parameter name** — so the LLM knows what to fix
2. **The received value** (with type if ambiguous) — so the LLM sees what it passed
3. **The expected format** — so the LLM knows how to correct it
4. **A concrete example** in the hint — so even a small LLM (8B) can copy-paste

Example of a **bad** error (causes retry loops):
```json
{"error": "EXEC_ERROR", "message": "Execution error", "hint": null}
```

Example of a **good** error (self-correcting):
```json
{
  "error": "INVALID_PARAMETER",
  "message": "max_output must be an integer or None, got: '' (empty string)",
  "hint": "Omit max_output or use an integer like max_output=50000"
}
```

**Type coercion rules:**
- Falsy values for optional list parameters (`args=0`, `args=""`) are silently converted to `[]`
- Falsy values for optional string parameters (`message=""`) use the default value
- Invalid types for numeric parameters (`line=""`, `offset=""`) raise `INVALID_PARAMETER` with the parameter name
- `overwrite=True` silently ignores positioning parameters (`line`, `end_line`, `pattern`) to avoid spurious errors

### Performance and Quotas

- **No quota caching.** Every write operation recalculates disk usage in real-time (O(n) files). This is intentional: simplicity and reliability over performance. A cache would introduce invalidation problems, undetected quota overruns, and subtle bugs. The usage context (LLM tool, not high-performance filesystem) doesn't justify the complexity.

### SQLite Security

- **ATTACH DATABASE, DETACH, and LOAD_EXTENSION are blocked.** These commands could access files outside the intended scope or load malicious code. Blocking is implemented via pattern detection in SQL queries.
- **SQL comment stripping.** Before checking for dangerous patterns, SQL comments are removed (both `/* */` blocks and `-- ...` lines). This prevents bypass attacks like `AT/**/TACH` or `LOAD_EX--bypass\nTENSION`.
- **No SQL query whitelist.** The `sqlite_readonly` valve restricts to SELECT-only when needed. In read-write mode, the LLM needs to create tables, insert data, etc. Only specific dangerous operations (ATTACH, LOAD_EXTENSION) are blocked individually.

### ZIP Archive Security

- **Magic bytes verification.** Beyond the `.zip` extension, Fileshed verifies file headers match ZIP format (PK signatures). This prevents attacks via renamed files.
- **First-level extraction only.** `shed_unzip` extracts only the ZIP passed as parameter. Nested `.zip` files are extracted as regular files (not automatically decompressed). If the user wants to extract them, they must call `shed_unzip` again — and all protections (max size, file count, compression ratio) apply again. This is not a "nested ZIP bomb" vulnerability.
- **Symlink check before extraction.** Just before `extractall()`, Fileshed verifies the destination directory is not a symlink (TOCTOU protection).

### CSV Protection

- **Column limit (5000 max).** CSV files with extreme column counts could cause DoS via memory consumption. The 5000 column limit is large enough for legitimate edge cases while protecting against abuse.

### Specific Error Codes

- **FILE_OWNER_ONLY and FILE_READ_ONLY** are internal permission check return values, not error codes raised to users. They allow the code to distinguish permission failure reasons internally, then raise appropriate `PERMISSION_DENIED` errors with descriptive messages.
- **INVALID_PATH and PROTECTED_PATH** distinguish invalid paths (e.g., zone root) from protected paths (e.g., `.git` directory).

### Architecture and LLM Exposure

- **Only `shed_*` methods are exposed to the LLM.** The `_FileshedCore` class contains all internal logic and is never directly callable. This separation relies on OpenWebUI's architecture which only exposes `Tools` class methods.
- **Monolithic file.** All code is in a single file because OpenWebUI Tools are deployed as single Python files. Splitting into multiple modules would create deployment risks: version mismatches between files, incomplete updates, import path issues. The single-file approach ensures atomic deployment — the tool either works completely or fails cleanly.

### Shell Commands

- **Strict whitelist.** Allowed commands are explicitly listed. Dangerous commands (shells, interpreters, upload-capable network tools) are blacklisted.
- **printenv and envsubst removed.** These commands exposed environment variables, potentially containing secrets.
- **Pattern-based validation.** Dangerous arguments (shell metacharacters, injections) are detected via regex. This is defense-in-depth, not absolute protection. The command whitelist remains the primary protection.

### Locking and Concurrency

- **File-based locks.** Locks use `os.open()` with `O_CREAT | O_EXCL` for atomic acquisition. This mechanism works for a single OpenWebUI instance.
- **No distributed locks.** File locks are unreliable across multiple instances/containers sharing NFS storage. For multi-instance deployments, an external locking mechanism (Redis, database) would be needed. This use case is not supported in the current version.

### OpenWebUI Dependencies

- **Internal APIs.** Fileshed uses OpenWebUI internal APIs (`open_webui.models.*`). These APIs may change between versions. Current target version is OpenWebUI 0.4.0+.
- **Bridge pattern.** `_OpenWebUIBridge` isolates version-specific imports to facilitate adaptation to future versions.

---

## Authors

- **Fade78** — Original author
- **Claude Opus 4.5** — Co-developer
