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

- `cat`, `head`, `tail`, `less`, `more`
- `ls`, `find`, `tree`, `stat`, `file`
- `grep`, `wc`, `diff`, `sort`, `uniq`
- `md5sum`, `sha256sum`, `base64`
- `hexdump`, `xxd`, `strings`, `od`

**WHITELIST_READWRITE** (for Storage, Documents, Groups):

- All of READONLY plus:
- `cp`, `mv`, `rm`, `mkdir`, `touch`
- `sed`, `awk`, `cut`, `tr`, `paste`
- `tar`, `gzip`, `gunzip`, `zip`, `unzip`
- `git` (for Documents/Groups)
- `curl`, `wget` (if network_mode allows)

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

Common error codes:

- `FILE_NOT_FOUND` — Path does not exist
- `FILE_EXISTS` — Destination already exists
- `FILE_TOO_LARGE` — File exceeds max_file_size_mb limit
- `PATH_ESCAPE` — Path traversal attempt blocked
- `PERMISSION_DENIED` — Group ownership check failed
- `COMMAND_FORBIDDEN` — Command not in whitelist
- `QUOTA_EXCEEDED` — Storage quota exceeded
- `FILE_LOCKED` — File locked by another user/conversation
- `INVALID_ZONE` — Unknown zone parameter
- `ZONE_READONLY` — Write operation on read-only zone (Uploads)
- `MISSING_PARAMETER` — Required parameter missing
- `GROUP_ACCESS_DENIED` — User is not a member of the group

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

## Authors

- **Fade78** — Original author
- **Claude Opus 4.5** — Co-developer
