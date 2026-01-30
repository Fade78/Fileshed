"""
title: Fileshed
description: Persistent file storage with group collaboration. FIRST: Run shed_help() for quick reference or shed_help(howto="...") for guides: download, csv_to_sqlite, upload, share, edit, commands, network, paths, large_files, full. Config: shed_parameters().
author: Fade78 (with Claude Opus 4.5)
version: 1.0.3
license: MIT
required_open_webui_version: 0.4.0

SETUP INSTRUCTIONS:
==================
For this tool to work properly, you must enable Native Function Calling:

Option 1 - Per Model (recommended):
  Admin Panel > Settings > Models > [Select Model] > Advanced Parameters > Function Calling > "Native"

Option 2 - Per Chat:
  Chat Controls (gear icon) > Advanced Params > Function Calling > "Native"
"""

# =============================================================================
# ⚠️  LLM WARNING - READ THIS FIRST  ⚠️
# =============================================================================
#
# YOU CAN ONLY CALL FUNCTIONS STARTING WITH "shed_" !
#
# ✅ CORRECT (public API):
#    shed_exec(zone="storage", cmd="ls", args=["-la"])
#    shed_exec(zone="storage", cmd="mkdir", args=["-p", "projects"])
#    shed_exec(zone="documents", cmd="git", args=["log"])
#    shed_patch_text(zone="storage", path="notes.txt", content="Hello")
#    shed_import(import_all=True)
#    shed_sqlite(zone="storage", path="db.sqlite", query="SELECT * FROM t")
#
# ❌ WRONG (internal methods - will NOT work):
#    _exec_command(...)      <- INTERNAL, don't call!
#    _git_run(...)           <- INTERNAL, don't call!
#    _validate_path(...)     <- INTERNAL, don't call!
#
# ⚠️ SHELL COMMANDS FIRST:
#    Use shed_exec() for ALL shell-doable operations!
#    ✓ mkdir: shed_exec(zone="storage", cmd="mkdir", args=["-p", "dir"])
#    ✗ WRONG: shed_patch_text(path="dir/.keep", content="")
#
# Methods starting with "_" are INTERNAL IMPLEMENTATION DETAILS.
# They are NOT callable by the LLM. Only "shed_*" functions are available.
#
# Run shed_help() for the list of available functions!
#
# =============================================================================

# =============================================================================
# 🔧 DEV NOTES
# =============================================================================
#
# 1. ARCHITECTURE: All public tools are in `class Tools`. Internal methods
#    MUST be in `class _FileshedCore` to hide them from Open WebUI/LLM.
#
# 2. PATHS: Internally we use {Zone}/data/ but externally it's just {Zone}/.
#    NEVER expose "data/" in help, messages, or errors. The LLM sees:
#      Storage/myfile.txt  (not Storage/data/myfile.txt)
#
# =============================================================================

import json
import mimetypes
import os
import re
import resource
import shutil
import sqlite3
import subprocess
import unicodedata
import uuid
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional
from pydantic import BaseModel, Field

# Try to import Open WebUI Groups API
GROUPS_AVAILABLE = False
try:
    from open_webui.models.groups import Groups
    GROUPS_AVAILABLE = True
except ImportError:
    pass


# =============================================================================
# CONSTANTS
# =============================================================================

# Size conversion
BYTES_PER_KB = 1024
BYTES_PER_MB = 1024 * 1024

# ZIP bomb protection limits
ZIP_MAX_DECOMPRESSED_SIZE = 500 * BYTES_PER_MB  # 500 MB max decompressed
ZIP_MAX_FILES = 10000                            # Max files in archive
ZIP_MAX_COMPRESSION_RATIO = 100                  # Max compression ratio (100:1)
ZIP_MAGIC_BYTES = (b'PK\x03\x04', b'PK\x05\x06', b'PK\x07\x08')  # Valid ZIP signatures

# CSV protection limits
CSV_MAX_COLUMNS = 5000  # Prevent DoS with extremely wide CSV files

# Output limits
MAX_HEXDUMP_BYTES = 4096
DEFAULT_HEXDUMP_BYTES = 256

# Validation patterns
UUID_PATTERN = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.IGNORECASE)

# SQL protection limits
MAX_SQL_ROWS = 10000  # Hard limit even when user requests unlimited (limit=0)


# =============================================================================
# ZONE CONTEXT
# =============================================================================

@dataclass
class ZoneContext:
    """Result of zone resolution - contains all zone-specific info."""
    zone_root: Path          # Data directory path
    zone_name: str           # Canonical name (Storage, Documents, Uploads, group:xxx)
    zone_lower: str          # Lowercase (storage, documents, uploads, group)
    editzone_base: Path      # Base for editzones (None for uploads)
    conv_id: str             # Conversation ID
    group_id: Optional[str]  # Group ID if zone=group, else None
    git_commit: bool         # Auto-commit after modifications
    readonly: bool           # True for uploads
    whitelist: set           # Allowed commands for this zone


# =============================================================================
# CONFIGURATION
# =============================================================================
# Valves are defined inside Tools class (required by Open WebUI)
# See: Tools.Valves (inner class)

# =============================================================================
# WHITELISTS
# =============================================================================

# Read-only commands (Uploads)
WHITELIST_READONLY = {
    # Reading
    "cat", "head", "tail", "less", "more", "nl", "wc", "stat", "file", "du", "tac",
    # Navigation
    "ls", "tree", "find",
    # Text search
    "grep", "egrep", "fgrep", "rg", "awk", "sed",
    # Text transformation
    "sort", "uniq", "cut", "paste", "tr", "fold", "fmt", "column", "rev", "shuf",
    "expand", "unexpand", "pr",
    # Join
    "join",
    # Comparison
    "diff", "diff3", "cmp", "comm",
    # Archives (list)
    "tar", "unzip", "zipinfo", "7z",
    # Compression (stdout)
    "zcat", "bzcat", "xzcat",
    # Checksums
    "md5sum", "sha1sum", "sha256sum", "sha512sum", "b2sum", "cksum",
    # Encoding
    "base32", "base64", "basenc",
    # Binary/Hex
    "strings", "od", "hexdump", "xxd",
    # JSON/XML/YAML
    "jq", "xmllint", "yq",
    # Encoding conversion (stdout)
    "iconv",
    # Calculation
    "bc", "dc", "expr", "factor", "numfmt",
    # Paths
    "basename", "dirname", "realpath",
    # Misc
    "echo", "printf",
    # Media (info reading)
    "ffprobe", "identify", "exiftool",
    # Database
    "sqlite3",
    # REMOVED for security:
    # - xargs    : can execute arbitrary commands
    # - timeout  : can execute arbitrary commands (we have internal timeout)
    # - env      : can execute commands and expose secrets
}

# Read/write commands (Storage, Documents)
WHITELIST_READWRITE = WHITELIST_READONLY | {
    # Additional reading
    "df", "locate", "which", "whereis",
    # Split
    "split", "csplit",
    # Additional comparison
    "sdiff", "patch", "colordiff",
    # Archives (extraction/creation)
    "zip", "7za",
    # Compression
    "gzip", "gunzip", "bzip2", "bunzip2", "xz", "unxz", "lz4", "zstd",
    # Additional checksums
    "sum",
    # Additional encoding
    "uuencode", "uudecode",
    # File modification (ln removed - security risk with hard/soft links)
    "touch", "mkdir", "rm", "rmdir", "mv", "cp", "truncate", "mktemp",
    "install", "shred", "rename",
    # Permissions
    "chmod",
    # Document conversion
    "pandoc",
    # Encoding conversion
    "dos2unix", "unix2dos", "recode",
    # Additional calculation
    "seq",
    # Date/Time
    "date", "cal",
    # Additional paths
    "readlink", "pathchk", "pwd",
    # System (info only - env/printenv removed, can expose secrets)
    "uname", "nproc",
    # Control (timeout removed - can execute commands, we have internal timeout)
    "sleep",
    # Misc (xargs removed - can execute arbitrary commands, envsubst removed - exposes env vars)
    "yes", "tee", "gettext", "tsort", "true", "false",
    # Media
    "ffmpeg", "magick", "convert",
    # Versioning
    "git",
}

# Allowed Git subcommands
GIT_WHITELIST_READ = {
    "status", "log", "show", "diff", "branch", "tag", "blame", "ls-files",
    "ls-tree", "shortlog", "reflog", "describe", "rev-parse", "rev-list", "cat-file",
}

GIT_WHITELIST_WRITE = {
    "add", "commit", "reset", "restore", "checkout", "rm", "mv", "revert",
    "cherry-pick", "stash", "clean",
}

GIT_BLACKLIST = {
    "gc", "prune", "filter-branch",  # Always forbidden (dangerous local ops)
}

# Git network commands (controlled by curl valves)
GIT_NETWORK_GET = {
    "clone", "fetch", "pull", "submodule", "remote",  # Download operations
}
GIT_NETWORK_PUSH = {
    "push",  # Upload/exfiltration
}

# Curl/wget commands (controlled by valves)
CURL_COMMANDS = {"curl", "wget"}

# Curl/wget options forbidden in GET mode (allow data exfiltration)
CURL_FORBIDDEN_GET_OPTS = {
    # HTTP methods
    "-X", "--request",
    # Data upload
    "-d", "--data", "--data-raw", "--data-binary", "--data-urlencode", "--data-ascii",
    "-F", "--form", "--form-string",
    "-T", "--upload-file",
    # POST behavior
    "--post301", "--post302", "--post303",
    # wget upload
    "--post-data", "--post-file", "--body-data", "--body-file", "--method",
}

# ffmpeg output protocols that allow data exfiltration
# These protocols can SEND data to remote servers
FFMPEG_OUTPUT_PROTOCOLS = {
    "rtmp://", "rtmps://", "rtmpe://", "rtmpt://",  # Streaming upload
    "rtsp://", "rtsps://",  # Real-time streaming
    "srt://",  # Secure Reliable Transport
    "udp://", "tcp://",  # Raw sockets
    "rtp://", "srtp://",  # Real-time protocol
    "ftp://", "sftp://",  # File transfer
    "http://", "https://",  # Can POST/PUT with -method
    "icecast://",  # Streaming server
    "tee:",  # Can duplicate to multiple outputs including network
}

# Commands that can SEND data over network (exfiltration risk)
# These are blocked unless network_mode is "all"
NETWORK_OUTPUT_COMMANDS = {"ffmpeg"}

# Commands that can RECEIVE data from network (read-only risk)  
# These require network_mode "safe" or "all", with URL blocking if "disabled"
NETWORK_INPUT_COMMANDS = {"ffprobe", "pandoc", "magick", "convert", "identify"}

# All network-capable commands (union of above)
NETWORK_CAPABLE_COMMANDS = NETWORK_OUTPUT_COMMANDS | NETWORK_INPUT_COMMANDS

# Forbidden commands
BLACKLIST_COMMANDS = {
    # Interpreters/Shells
    "bash", "sh", "zsh", "fish", "dash", "csh", "tcsh", "ksh",
    "python", "python3", "perl", "ruby", "node", "php", "lua",
    "exec", "eval", "source",
    # Background / Fork
    "nohup", "disown", "setsid", "screen", "tmux", "at", "batch", "crontab",
    # System privileges
    "sudo", "su", "doas", "chown", "chgrp",
    # Network (curl/wget controlled separately via valves)
    "fetch", "ssh", "scp", "sftp", "rsync",
    "nc", "netcat", "ncat", "telnet", "ftp", "ping", "traceroute",
    # System / Dangerous
    "dd", "mount", "umount", "kill", "killall", "pkill",
    "reboot", "shutdown", "halt", "poweroff",
    "systemctl", "service", "mkfs", "fdisk", "parted",
    "iptables", "firewall-cmd",
}

# Pattern to detect dangerous arguments (shell metacharacters)
# Blocks: ; & | ` \n \r && || >> << > $( ${
# Note: $ alone is NOT blocked because subprocess.run() with list args doesn't expand variables
# Only $( and ${ are dangerous (command substitution / brace expansion)
# Note: < is allowed for comparisons (reading via getline < is blocked separately)
# Note: > is blocked to prevent file writes outside chroot (use stdout_file parameter instead)
DANGEROUS_ARGS_PATTERN = re.compile(r'[;&|`\n\r]|&&|\|\||>>|<<|>|\$\(|\$\{')

# Same pattern but allows | (for commands that use | in their internal syntax)
# Used for: jq (pipe operator), awk (print | "cmd" - but we block system() separately),
# grep -E (extended regex alternation)
DANGEROUS_ARGS_PATTERN_ALLOW_PIPE = re.compile(r'[;&`\n\r]|&&|>>|<<|>|\$\(|\$\{')

# Commands that use | in their internal syntax (not shell pipes)
# - jq: pipe operator for chaining filters
# - awk: print | "cmd" (but we block system() separately via AWK_DANGEROUS_PATTERNS)
# - grep/egrep/fgrep: extended regex alternation with -E or -P flags
# Safe because subprocess.run() with list args never invokes shell interpretation
COMMANDS_ALLOWING_PIPE = {"jq", "awk", "gawk", "mawk", "nawk", "grep", "egrep", "fgrep"}

# Pattern to detect URLs (network access via ffmpeg, pandoc, imagemagick, etc.)
# Blocks: http://, https://, ftp://, rtmp://, rtsp://, smb://, file://, etc.
URL_PATTERN = re.compile(r'^[a-zA-Z][a-zA-Z0-9+.-]*://', re.IGNORECASE)

# find options that can execute commands (security risk)
FIND_EXEC_OPTIONS = {"-exec", "-execdir", "-ok", "-okdir"}

# awk patterns that can execute commands or leak sensitive data (security risk)
# system() executes shell commands, getline can pipe from commands,
# ENVIRON exposes environment variables (may contain secrets)
AWK_DANGEROUS_PATTERNS = re.compile(r'\bsystem\s*\(|\|\s*getline|\bgetline\s*<|\bENVIRON\b')

# ffmpeg options that can be used for data exfiltration or other dangerous operations
# in "safe" network mode. These are blocked unless network_mode="all"
FFMPEG_DANGEROUS_OPTIONS = {
    # Metadata can be used to embed arbitrary data for exfiltration
    "-metadata", "-metadata:s", "-metadata:g",
    # filter_complex can contain network destinations
    "-filter_complex",
    # Can write to multiple outputs including network
    "-f", "tee",
    # HTTP method override (can enable POST/PUT)
    "-method",
    # Can be used to send data via HTTP headers
    "-headers",
    # Content type manipulation
    "-content_type",
}

# =============================================================================
# ERRORS
# =============================================================================

class StorageError(Exception):
    """Base storage error with contextual help."""
    def __init__(self, code: str, message: str, details: dict = None, hint: str = None, func: str = None):
        self.code = code
        self.message = message
        self.details = details or {}
        self.hint = hint
        self.func = func  # Function name for contextual help
        super().__init__(message)
    
    def to_dict(self, function_help: str = None) -> dict:
        result = {
            "success": False,
            "error": self.code,
            "message": self.message,
            "details": self.details,
            "hint": self.hint,
        }
        if function_help:
            result["help"] = function_help
        return result


# =============================================================================
# MAIN CLASS
# =============================================================================


# =============================================================================
# OPEN WEBUI BRIDGE (isolates internal API calls)
# =============================================================================

class _OpenWebUIBridge:
    """
    Bridge to Open WebUI internal Python API.
    
    This class isolates all direct interactions with Open WebUI's internal modules.
    If Open WebUI's internal API changes between versions, only this class needs updating.
    
    Supported Open WebUI versions: 0.6.x (tested with 0.6.40+)
    """
    
    _instance = None
    _initialized = False
    _files_module = None
    _files_class = None
    _file_form_class = None
    
    def __new__(cls):
        """Singleton pattern to avoid repeated imports."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def _ensure_initialized(self) -> bool:
        """Lazy initialization of Open WebUI imports."""
        if self._initialized:
            return True
        
        try:
            # Open WebUI 0.6.x API
            from open_webui.models.files import Files, FileForm
            self._files_class = Files
            self._file_form_class = FileForm
            self._initialized = True
            return True
        except ImportError:
            # Try alternative import paths for different versions
            try:
                # Hypothetical future API path
                from open_webui.core.models.files import Files, FileForm
                self._files_class = Files
                self._file_form_class = FileForm
                self._initialized = True
                return True
            except ImportError:
                pass
            raise StorageError(
                "OPENWEBUI_API_UNAVAILABLE",
                "Cannot import Open WebUI internal API",
                None,
                "Open WebUI internal modules not available. This feature requires running inside Open WebUI."
            )
    
    def insert_file(
        self,
        user_id: str,
        file_id: str,
        filename: str,
        file_path: str,
        content_type: str,
        file_size: int,
        metadata: dict = None
    ) -> Any:
        """
        Insert a new file into Open WebUI's file system.
        
        Args:
            user_id: Open WebUI user ID
            file_id: Unique file ID (UUID)
            filename: Display name of the file
            file_path: Absolute path to the file on disk
            content_type: MIME type
            file_size: Size in bytes
            metadata: Optional additional metadata
            
        Returns:
            File model object or None on failure
        """
        self._ensure_initialized()
        
        try:
            file_item = self._files_class.insert_new_file(
                user_id,
                self._file_form_class(
                    **{
                        "id": file_id,
                        "filename": filename,
                        "path": file_path,
                        "data": {},  # No RAG processing needed for download-only files
                        "meta": {
                            "name": filename,
                            "content_type": content_type,
                            "size": file_size,
                            "data": metadata or {},
                        },
                    }
                ),
            )
            return file_item
        except Exception:
            raise StorageError(
                "OPENWEBUI_INSERT_ERROR",
                "Failed to insert file into Open WebUI",
                {"file_id": file_id}
            )
    
    def get_file_by_id(self, file_id: str) -> Any:
        """Get file metadata by ID."""
        self._ensure_initialized()
        try:
            return self._files_class.get_file_by_id(file_id)
        except Exception:
            raise StorageError(
                "OPENWEBUI_GET_ERROR",
                "Failed to get file from Open WebUI",
                {"file_id": file_id}
            )

    def delete_file_by_id(self, file_id: str) -> Any:
        """Delete a file by ID."""
        self._ensure_initialized()
        try:
            return self._files_class.delete_file_by_id(file_id)
        except Exception:
            raise StorageError(
                "OPENWEBUI_DELETE_ERROR",
                "Failed to delete file from Open WebUI",
                {"file_id": file_id}
            )
    
    @classmethod
    def is_available(cls) -> bool:
        """Check if Open WebUI internal API is available."""
        try:
            instance = cls()
            instance._ensure_initialized()
            return True
        except Exception:
            return False

    @classmethod
    def get_api_version(cls) -> str:
        """Return the detected Open WebUI API version."""
        try:
            from open_webui import __version__
            return __version__
        except ImportError:
            return "unknown"


# =============================================================================
# INTERNAL CORE (not exposed to LLM)
# =============================================================================

class _FileshedCore:
    """
    Internal implementation class containing all private methods.
    This class is NOT exposed to the LLM - only Tools.shed_* methods are visible.
    """
    
    def __init__(self, tools):
        self._tools = tools  # Reference to parent Tools instance
        self._commands_cache = None
        self._db_initialized = False
    
    @property
    def valves(self):
        """Access valves from parent Tools (ensures sync with Open WebUI updates)."""
        return self._tools.valves
    

    # =========================================================================
    # FUNCTION HELP INDEX (for contextual error messages)
    # =========================================================================
    
    FUNCTION_HELP = {
        # === DIRECT WRITE FUNCTIONS ===
        "shed_create_file": {
            "usage": "shed_create_file(zone, path, content, file_type='text', content_format='hex')",
            "desc": "Create or overwrite a file. Simplest way to write a file!",
            "workflows": ["Direct Write"],
            "howtos": ["edit"],
            "not_for": ["Appending to file (use shed_patch_text)", "Patching specific lines (use shed_patch_text)"],
            "tips": [
                "Creates parent directories automatically",
                "file_type='text' (default) or 'bytes'",
                "For bytes: content_format='hex' (default), 'base64', or 'raw'",
                "For appending: use shed_patch_text(zone, path, content) instead",
            ],
        },
        "shed_patch_text": {
            "usage": "shed_patch_text(zone, path, content, position='end', overwrite=False, ...)",
            "desc": "THE standard function to write/create text files. Use this for all file writing!",
            "workflows": ["Direct Write"],
            "howtos": ["edit"],
            "not_for": ["Locked Edit workflow (shed_lockedit_*)"],
            "tips": [
                "💡 To CREATE a file: use shed_create_file(zone, path, content) instead!",
                "Append to file: shed_patch_text(zone, path, content)  # position='end' by default",
                "To READ files: use shed_exec(cmd='cat', args=['file']) or head/tail/sed",
                "⚠️ CSV: quote fields with comma/newline/quotes. Escape quotes by doubling: \"\"",
                "position: 'start', 'end', 'before', 'after', 'replace' (NOT 'at' - that's for bytes!)",
                "For 'before'/'after'/'replace': use line=N (first line is 1) or pattern='...'",
            ],
        },
        "shed_patch_bytes": {
            "usage": "shed_patch_bytes(zone, path, content, position='end', offset=None)",
            "desc": "Write binary data (hex string) to a file",
            "workflows": ["Direct Write"],
            "howtos": ["edit", "large_files"],
            "not_for": ["Locked Edit workflow (shed_lockedit_*)"],
            "tips": ["content must be a hex string like '48454C4C4F'"],
        },
        
        # === SAFE EDIT WORKFLOW ===
        "shed_lockedit_open": {
            "usage": "shed_lockedit_open(zone, path)",
            "desc": "Step 1/3: Lock file and create working copy",
            "workflows": ["Locked Edit"],
            "howtos": ["edit"],
            "not_for": ["Direct Write workflow (shed_patch_*)"],
            "tips": [
                "WORKFLOW: shed_lockedit_open → shed_lockedit_overwrite → shed_lockedit_save",
                "After this, use shed_lockedit_overwrite (NOT shed_patch_text!)",
            ],
        },
        "shed_lockedit_overwrite": {
            "usage": "shed_lockedit_overwrite(zone, path, content, append=False)",
            "desc": "Step 2/3: Write to locked file (working copy)",
            "workflows": ["Locked Edit"],
            "howtos": ["edit"],
            "not_for": ["Direct Write workflow (shed_patch_*)"],
            "tips": [
                "REQUIRES shed_lockedit_open() first!",
                "NO position/pattern/line params - those are for shed_patch_text!",
                "Use append=True to append instead of overwrite",
            ],
        },
        "shed_lockedit_save": {
            "usage": "shed_lockedit_save(zone, path, message=None)",
            "desc": "Step 3/3: Save changes and unlock file",
            "workflows": ["Locked Edit"],
            "howtos": ["edit"],
            "not_for": ["Direct Write workflow (shed_patch_*)"],
            "tips": [
                "⚠️ THIS CLOSES EDIT MODE! File is unlocked after save.",
                "To edit again, call shed_lockedit_open() first!",
            ],
        },
        "shed_lockedit_cancel": {
            "usage": "shed_lockedit_cancel(zone, path)",
            "desc": "Discard changes and unlock file",
            "workflows": ["Locked Edit"],
            "howtos": ["edit"],
            "not_for": ["Direct Write workflow (shed_patch_*)"],
            "tips": ["Use instead of shed_lockedit_save to discard changes"],
        },
        "shed_lockedit_exec": {
            "usage": "shed_lockedit_exec(zone, path, cmd, args=[])",
            "desc": "Run command on locked file (in working copy)",
            "workflows": ["Locked Edit", "Shell Commands"],
            "howtos": ["edit", "commands"],
            "not_for": ["Direct Write workflow (shed_patch_*)"],
            "tips": ["REQUIRES shed_lockedit_open() first!"],
        },
        
        # === SHELL COMMANDS ===
        "shed_exec": {
            "usage": "shed_exec(zone, cmd, args=[], timeout=None, stdout_file=None, stderr_file=None, group=None)",
            "desc": "Execute shell command in zone. Use for reading files and shell operations!",
            "workflows": ["Shell Commands", "Download"],
            "howtos": ["commands", "large_files", "download"],
            "not_for": ["Locked Edit workflow (use shed_lockedit_exec instead if file is locked)"],
            "tips": [
                "READ files: cmd='cat', args=['file.txt'] (or head/tail/sed for partial reads)",
                "DOWNLOAD files or call APIs: use curl (saves full content to disk for processing)",
                "Download: cmd='curl', args=['-L', '-o', 'data.csv', 'URL']",
                "REDIRECT output to file: stdout_file='output.txt' (like shell > redirection)",
                "Check available commands: shed_allowed_commands()",
            ],
        },
        
        # === FILE OPERATIONS ===
        "shed_delete": {
            "usage": "shed_delete(zone, path, group=None, message=None)",
            "desc": "Delete a file or empty directory",
            "workflows": ["File Operations"],
            "howtos": ["commands"],
            "not_for": ["Locked Edit workflow", "Direct Write workflow"],
            "tips": [
                "Cannot delete non-empty directories",
                "message: Git commit message (for documents/group zones)",
            ],
        },
        "shed_rename": {
            "usage": "shed_rename(zone, old_path, new_path)",
            "desc": "Rename or move a file within same zone",
            "workflows": ["File Operations"],
            "howtos": ["commands"],
            "not_for": ["Locked Edit workflow", "Direct Write workflow"],
            "tips": ["For cross-zone moves, use shed_copy_* or shed_move_* bridges"],
        },
        "shed_tree": {
            "usage": "shed_tree(zone, path='.', depth=3)",
            "desc": "Show directory tree (builtin, always works)",
            "workflows": ["File Operations", "Shell Commands"],
            "howtos": ["commands"],
            "not_for": [],
            "tips": ["Use when 'tree' command is not available"],
        },
        
        # === SQLITE ===
        "shed_sqlite": {
            "usage": "shed_sqlite(zone, path, query=None, import_csv=None, table=None, ...)",
            "desc": "Execute SQL or import CSV into SQLite",
            "workflows": ["CSV Import", "Data Processing"],
            "howtos": ["csv_to_sqlite"],
            "not_for": ["Locked Edit workflow", "Direct Write workflow"],
            "tips": [
                "For CSV import: shed_sqlite(..., import_csv='data.csv', table='mytable')",
                "Auto-detects delimiter and encoding!",
                "⚠️ Creating CSV: quote fields with comma/newline/quotes. Escape \" as \"\" (RFC 4180)",
            ],
        },
        
        # === UPLOADS/BRIDGES ===
        "shed_import": {
            "usage": "shed_import(filename=None, import_all=False, dest_subdir='')",
            "desc": "Import uploaded files to Uploads zone",
            "workflows": ["Upload Handling"],
            "howtos": ["upload"],
            "not_for": ["Locked Edit workflow", "Direct Write workflow"],
            "tips": [
                "filename: specific file to import, or None to see available files",
                "import_all=True: import all files at once",
                "After import, use shed_move_uploads_to_storage() to move files",
            ],
        },
        "shed_move_uploads_to_storage": {
            "usage": "shed_move_uploads_to_storage(src, dest, overwrite=False)",
            "desc": "Move file from Uploads to Storage",
            "workflows": ["Upload Handling", "File Operations"],
            "howtos": ["upload"],
            "not_for": ["Locked Edit workflow"],
            "tips": [
                "Uploads zone is read-only, move files to Storage for editing",
                "overwrite=True to replace existing destination file",
            ],
        },
        "shed_move_uploads_to_documents": {
            "usage": "shed_move_uploads_to_documents(src, dest, message=None, overwrite=False)",
            "desc": "Move file from Uploads to Documents (versioned)",
            "workflows": ["Upload Handling", "File Operations"],
            "howtos": ["upload"],
            "not_for": ["Locked Edit workflow"],
            "tips": [
                "Documents zone has Git versioning",
                "overwrite=True to replace existing destination file",
            ],
        },
        "shed_copy_storage_to_documents": {
            "usage": "shed_copy_storage_to_documents(src, dest, message=None, overwrite=False)",
            "desc": "Copy file from Storage to Documents (versioned)",
            "workflows": ["File Operations"],
            "howtos": ["upload"],
            "not_for": ["Locked Edit workflow"],
            "tips": ["overwrite=True to replace existing destination file"],
        },
        "shed_move_documents_to_storage": {
            "usage": "shed_move_documents_to_storage(src, dest, message=None, overwrite=False)",
            "desc": "Move file from Documents to Storage (removes versioning)",
            "workflows": ["File Operations"],
            "howtos": ["upload"],
            "not_for": ["Locked Edit workflow"],
            "tips": [
                "message: Git commit message for the removal from Documents",
                "overwrite=True to replace existing destination file",
            ],
        },
        
        # === LINKS ===
        "shed_link_create": {
            "usage": "shed_link_create(zone, path, group=None)",
            "desc": "Create download link for a file",
            "workflows": ["Share Files"],
            "howtos": ["share"],
            "not_for": ["Locked Edit workflow", "Direct Write workflow"],
            "tips": [
                "Returns clickable_link in Markdown format - show it directly to user!",
                "Links require authentication - not public!",
                "Use group= for files in group zones",
            ],
        },
        "shed_link_list": {
            "usage": "shed_link_list()",
            "desc": "List all your download links",
            "workflows": ["Share Files"],
            "howtos": ["share"],
            "not_for": [],
            "tips": [],
        },
        "shed_link_delete": {
            "usage": "shed_link_delete(file_id)",
            "desc": "Delete a download link",
            "workflows": ["Share Files"],
            "howtos": ["share"],
            "not_for": [],
            "tips": ["Get file_id from shed_link_list()"],
        },
        
        # === GROUPS ===
        "shed_group_list": {
            "usage": "shed_group_list()",
            "desc": "List groups you belong to",
            "workflows": ["Collaboration"],
            "howtos": [],
            "not_for": [],
            "tips": ["Group names are case-sensitive!"],
        },
        "shed_group_info": {
            "usage": "shed_group_info(group)",
            "desc": "Get group details and members",
            "workflows": ["Collaboration"],
            "howtos": [],
            "not_for": [],
            "tips": [],
        },
        "shed_copy_to_group": {
            "usage": "shed_copy_to_group(src_zone, src_path, group, dest_path, message=None, overwrite=False)",
            "desc": "Copy file to a group",
            "workflows": ["Collaboration", "File Operations"],
            "howtos": [],
            "not_for": ["Locked Edit workflow", "Direct Write workflow"],
            "tips": ["overwrite=True to replace existing destination file"],
        },
        
        # === ZIP ===
        "shed_zip": {
            "usage": "shed_zip(zone, src, dest='', include_empty_dirs=False)",
            "desc": "Create ZIP archive from file or folder",
            "workflows": ["File Operations"],
            "howtos": ["commands"],
            "not_for": ["Locked Edit workflow", "Direct Write workflow"],
            "tips": [
                "src: file or folder to compress",
                "dest: output ZIP path (default: src + '.zip')",
                "include_empty_dirs=True: preserve empty directories in archive",
            ],
        },
        "shed_unzip": {
            "usage": "shed_unzip(zone, src, dest='')",
            "desc": "Extract ZIP archive",
            "workflows": ["File Operations", "Download"],
            "howtos": ["commands", "download"],
            "not_for": ["Locked Edit workflow"],
            "tips": [
                "src: path to ZIP file",
                "dest: extraction folder (default: same folder as ZIP)",
                "After curl download, use shed_unzip to extract",
            ],
        },
        "shed_zipinfo": {
            "usage": "shed_zipinfo(zone, path)",
            "desc": "List ZIP contents without extracting",
            "workflows": ["File Operations"],
            "howtos": ["commands"],
            "not_for": [],
            "tips": [],
        },
        
        # === INFO ===
        "shed_stats": {
            "usage": "shed_stats()",
            "desc": "Show storage usage statistics",
            "workflows": ["Info"],
            "howtos": [],
            "not_for": [],
            "tips": [],
        },
        "shed_parameters": {
            "usage": "shed_parameters()",
            "desc": "Show configuration limits (quota, file size, etc.)",
            "workflows": ["Info"],
            "howtos": ["network"],
            "not_for": [],
            "tips": [],
        },
        "shed_allowed_commands": {
            "usage": "shed_allowed_commands()",
            "desc": "List available shell commands",
            "workflows": ["Info", "Shell Commands"],
            "howtos": ["commands"],
            "not_for": [],
            "tips": [],
        },
        "shed_file_type": {
            "usage": "shed_file_type(zone, path)",
            "desc": "Detect file MIME type and extension",
            "workflows": ["Download", "File Operations"],
            "howtos": ["download"],
            "not_for": [],
            "tips": ["Useful after downloading files with unknown type"],
        },
        "shed_convert_eol": {
            "usage": "shed_convert_eol(zone, path, to='unix')",
            "desc": "Convert line endings (CRLF ↔ LF)",
            "workflows": ["File Operations"],
            "howtos": ["commands"],
            "not_for": [],
            "tips": [
                "to='unix': Convert to LF (\\n)",
                "to='windows': Convert to CRLF (\\r\\n)",
            ],
        },
        "shed_hexdump": {
            "usage": "shed_hexdump(zone, path, offset=0, length=256)",
            "desc": "Show hex dump of file (for binary inspection)",
            "workflows": ["File Operations"],
            "howtos": ["large_files"],
            "not_for": [],
            "tips": ["Useful for inspecting binary files without loading them"],
        },
        "shed_force_unlock": {
            "usage": "shed_force_unlock(zone, path, group=None)",
            "desc": "Force unlock a stuck file (crash recovery)",
            "workflows": ["Locked Edit"],
            "howtos": ["edit"],
            "not_for": [],
            "tips": [
                "Use if a file is stuck in edit mode after a crash",
                "For group files, use group= instead of zone=",
            ],
        },
        "shed_group_set_mode": {
            "usage": "shed_group_set_mode(group, path, mode)",
            "desc": "Change file permission mode in group",
            "workflows": ["Collaboration"],
            "howtos": [],
            "not_for": [],
            "tips": [
                "mode: 'owner' (only owner), 'group' (all members), 'owner_ro' (read-only for others)",
            ],
        },
        "shed_group_chown": {
            "usage": "shed_group_chown(group, path, new_owner)",
            "desc": "Transfer file ownership in group",
            "workflows": ["Collaboration"],
            "howtos": [],
            "not_for": [],
            "tips": ["new_owner: user ID of the new owner"],
        },
        "shed_help": {
            "usage": "shed_help(howto=None)",
            "desc": "Get help (general or specific topic)",
            "workflows": ["Info"],
            "howtos": [],
            "not_for": [],
            "tips": [
                "shed_help() for quick reference",
                "shed_help(howto='edit') for editing guide",
                "shed_help(howto='download') for download guide",
            ],
        },
        "shed_maintenance": {
            "usage": "shed_maintenance()",
            "desc": "Cleanup expired locks and orphan editzones",
            "workflows": ["Info"],
            "howtos": [],
            "not_for": [],
            "tips": [
                "Runs automatically, but can be called manually",
                "Cleans locks older than lock_max_age_hours",
            ],
        },
    }
    
    def _get_function_help(self, func_name: str) -> str:
        """Generate contextual help for a function."""
        if func_name not in self.FUNCTION_HELP:
            return ""
        
        info = self.FUNCTION_HELP[func_name]
        lines = [
            f"\n📖 HELP for {func_name}:",
            f"   Usage: {info['usage']}",
            f"   → {info['desc']}",
        ]
        
        # Workflows this function belongs to (most important for LLM!)
        if info.get("workflows"):
            wf_list = ", ".join(info["workflows"])
            lines.append(f"   🔧 Belongs to workflow(s): {wf_list}")
        
        # What this function is NOT for (avoid confusion)
        if info.get("not_for"):
            not_list = ", ".join(info["not_for"])
            lines.append(f"   ⛔ NOT for: {not_list}")
        
        # Tips
        if info.get("tips"):
            lines.append("   💡 Tips:")
            for tip in info["tips"]:
                lines.append(f"      • {tip}")
        
        # Related howto guides
        if info.get("howtos"):
            howto_list = ", ".join(f'shed_help(howto="{h}")' for h in info["howtos"])
            lines.append(f"   📚 More info: {howto_list}")
        
        return "\n".join(lines)

    # HOWTO Guides
    HOWTO_GUIDES = {
        "download": """
# HOWTO: Download and work with files from the internet

## When to use curl

**Use curl to download files you need to WORK with** (save, process, import, convert):
- Datasets (CSV, JSON, XML)
- API responses
- Repositories
- Any file to process locally

curl saves the full content to disk for further processing.

## Quick Recipe
```
shed_exec(zone="storage", cmd="curl", args=["-L", "-o", "data.csv", "URL"])
```

## Common data sources

### World/country data
```
# REST Countries API (JSON with population, area, etc.)
shed_exec(zone="storage", cmd="curl", args=["-L", "-o", "countries.json", 
    "https://restcountries.com/v3.1/all?fields=name,area,population"])
```

### GitHub raw files
```
shed_exec(zone="storage", cmd="curl", args=["-L", "-o", "data.csv", 
    "https://raw.githubusercontent.com/user/repo/main/data.csv"])
```

## Download + import to SQLite
```
shed_exec(zone="storage", cmd="curl", args=["-L", "-o", "data.csv", "URL"])
shed_sqlite(zone="storage", path="db.sqlite", import_csv="data.csv", table="mytable")
```

## Important
- `-o filename` saves to file (mandatory!)
- `-L` follows redirects
- Requires network_mode = "safe" or "all"
""",

        "csv_to_sqlite": """
# HOWTO: Insert CSV data into SQLite

## ⚠️ CRITICAL: When CREATING CSV files (RFC 4180)

If you generate a CSV file, follow these quoting rules:

**Quote a field if it contains:**
- The delimiter (`,` or `;`)
- A newline
- Double quotes

**Inside quoted fields, escape quotes by doubling them:**

```
✅ CORRECT:
name,location,comment
"Acme Corp","New York, NY","Contains ""quotes"" here"
"Café du Monde","Paris, France","Great coffee"
Simple Value,Boston,No quotes needed

❌ WRONG (extra columns / broken parsing):
name,location,comment
Acme Corp,New York, NY,No quotes
Café,Said "hello",Unescaped quote
```

**Rules summary:**
- Field with comma → `"New York, NY"`
- Field with quote → `"Contains ""quotes"" inside"`
- Field with newline → `"Line1\nLine2"` (whole field quoted)
- Simple field → `Boston` (no quotes needed)

## Quick Recipe (RECOMMENDED)
```
# Basic import (auto-detects delimiter and encoding)
shed_sqlite(zone="storage", path="database.db",
            import_csv="data.csv", table="users")
```

## Why use shed_sqlite with import_csv?
1. **No context pollution**: CSV stays on disk, not in your context
2. **Fast**: Batch INSERT (1000 rows at a time), uses pandas if available
3. **Smart auto-detection**: Delimiter, encoding, separators detected automatically
4. **Auto-creates table**: Column names from CSV headers

## All CSV Parameters

| Parameter | Values | Description |
|-----------|--------|-------------|
| `import_csv` | path | CSV file path (in same zone) |
| `table` | name | Target table name (required) |
| `if_exists` | `"fail"` / `"replace"` / `"append"` | What to do if table exists (default: "fail") |
| `delimiter` | `","` `;` `"\\t"` `"|"` | CSV delimiter. `None` = auto-detect |
| `encoding` | `"utf-8"` `"latin-1"` `"cp1252"` | File encoding. `None` = auto-detect |
| `date_columns` | `["col1", "col2"]` | Columns to parse as dates |
| `date_format` | `"dayfirst"` / `"monthfirst"` / `"%d/%m/%Y"` | Date format |
| `decimal` | `","` | Decimal separator (European: `","`) |
| `skip_rows` | `0`, `1`, `2`... | Skip N rows before header |
| `has_header` | `True` / `False` | ⚠️ Does first row contain column names? Default: True. If False → columns named col_1, col_2... |

## Common Scenarios

### Standard CSV (comma-separated, UTF-8)
```
shed_sqlite(zone="storage", path="db.sqlite",
            import_csv="data.csv", table="data")
```

### French/European CSV (semicolon, comma decimal, ISO-8859-1)
```
shed_sqlite(zone="storage", path="db.sqlite",
            import_csv="french.csv", table="ventes",
            delimiter=";", decimal=",", encoding="latin-1")
```

### Excel export (often semicolon + Windows encoding)
```
shed_sqlite(zone="storage", path="db.sqlite",
            import_csv="export.csv", table="data",
            delimiter=";", encoding="cp1252")
```

### TSV file (tab-separated)
```
shed_sqlite(zone="storage", path="db.sqlite",
            import_csv="data.tsv", table="data",
            delimiter="\\t")
```

### With European dates (DD/MM/YYYY)
```
shed_sqlite(zone="storage", path="db.sqlite",
            import_csv="orders.csv", table="orders",
            date_columns=["order_date", "ship_date"],
            date_format="dayfirst")
```

### With US dates (MM/DD/YYYY)
```
shed_sqlite(zone="storage", path="db.sqlite",
            import_csv="orders.csv", table="orders",
            date_columns=["order_date"],
            date_format="monthfirst")
```

### Skip title rows (file has title + blank line before headers)
```
shed_sqlite(zone="storage", path="db.sqlite",
            import_csv="report.csv", table="report",
            skip_rows=2)
```

### CSV without header row (data only)
⚠️ If your CSV has NO column names on first line, use `has_header=False`.
Otherwise the first data row will be interpreted as column names!
```
shed_sqlite(zone="storage", path="db.sqlite",
            import_csv="raw_data.csv", table="raw",
            has_header=False)
# → Creates columns: col_1, col_2, col_3, ...
```

### Replace existing table
```
shed_sqlite(zone="storage", path="db.sqlite",
            import_csv="updated.csv", table="users",
            if_exists="replace")
```

## Step-by-step Example

### 1. Check your CSV structure first
```
shed_exec(zone="storage", cmd="head", args=["-5", "data.csv"])
shed_exec(zone="storage", cmd="file", args=["data.csv"])  # Check encoding
```

### 2. Import (auto-detection usually works)
```
shed_sqlite(zone="storage", path="mydb.db",
            import_csv="data.csv", table="users")
```

### 3. Check the response for detection info
```json
{
  "import_info": {
    "method": "pandas",
    "detected_encoding": "latin-1",
    "detected_delimiter": "';'"
  }
}
```

### 4. Query the data
```
shed_sqlite(zone="storage", path="mydb.db", query="SELECT COUNT(*) FROM users")
shed_sqlite(zone="storage", path="mydb.db", query="SELECT * FROM users LIMIT 5")
```

## ⚠️ SELECT Query Limits (Context Protection)

**By default, SELECT without LIMIT returns only 10 rows** to protect your context.

### Getting more rows
```
# Request more rows explicitly
shed_sqlite(..., query="SELECT * FROM users", limit=100)

# Or use LIMIT in SQL (respected as-is)
shed_sqlite(..., query="SELECT * FROM users LIMIT 50")
```

### Export ALL results to CSV (no context pollution!)
```
# Writes all rows to file, returns only stats
shed_sqlite(zone="storage", path="db.sqlite",
            query="SELECT * FROM users",
            output_csv="users_export.csv")
# → {"rows_exported": 5432, "output_csv": "users_export.csv"}

# Then use the CSV file
shed_exec(zone="storage", cmd="head", args=["-20", "users_export.csv"])
```

### Disable limit (use with caution!)
```
shed_sqlite(..., query="SELECT * FROM users", limit=0)
# → Returns ALL rows - be careful with large tables!
```

## Troubleshooting

### "UnicodeDecodeError"
→ Try `encoding="latin-1"` or `encoding="cp1252"`

### Wrong columns / data in wrong fields
→ Check delimiter: `delimiter=";"` or `delimiter="\\t"`

### Numbers with commas (1.234,56)
→ Add `decimal=","`

### Dates not parsed correctly
→ Add `date_columns=["col"]` and `date_format="dayfirst"`

### Headers on line 3 (title rows above)
→ Add `skip_rows=2`

## NEVER do this (pollutes context, very slow):
```
# BAD: Reading file content then inserting row by row
content = shed_exec(zone="storage", cmd="cat", args=["huge.csv"])  # Pollutes context!
for row in content:  # Slow!
    shed_sqlite(query="INSERT INTO...")  # One call per row!
```
""",

        "upload": """
# HOWTO: Handle user-uploaded files

## Quick Recipe
```
# Step 1: Import the file (MANDATORY)
shed_import(import_all=True)

# Step 2: Move to Storage for processing
shed_move_uploads_to_storage(src="filename.csv", dest="filename.csv")

# Step 3: Now you can work with it
shed_exec(zone="storage", cmd="head", args=["-10", "filename.csv"])
```

## Why is shed_import() mandatory?
Files uploaded by users are NOT automatically accessible. They must be imported first.

## Workflow for multiple files
```
# Import all at once
shed_import(import_all=True)

# Move each file
shed_move_uploads_to_storage(src="data.csv", dest="data.csv")
shed_move_uploads_to_storage(src="config.json", dest="config.json")
```

## Workflow for specific file
```
shed_import(filename="report.pdf")
shed_move_uploads_to_storage(src="report.pdf", dest="reports/report.pdf")
```

## Check what was uploaded
```
shed_exec(zone="uploads", cmd="ls", args=["-la"])
```

## Move to Documents (version-controlled)
```
shed_import(import_all=True)
shed_move_uploads_to_documents(src="important.docx", dest="important.docx")
```
""",

        "share": """
# HOWTO: Share files with the user

## shed_link - Create download links

Three functions to manage download links:

| Function | Description |
|----------|-------------|
| `shed_link_create()` | Create download link |
| `shed_link_list()` | List your download links |
| `shed_link_delete()` | Remove a download link |

## shed_link_create - Create a link
```
shed_link_create(zone="storage", path="report.pdf")
shed_link_create(zone="storage", path="archive.zip")
shed_link_create(zone="documents", path="presentation.pptx")
shed_link_create(zone="group", group="team", path="shared/data.csv")
```
- Works for ANY file type (PDF, ZIP, images, CSV, etc.)
- Returns `clickable_link` in Markdown format → **show it directly to the user!**
- Example response: `"clickable_link": "[📥 Download report.pdf](https://...)"`

## shed_link_list - List links
```
shed_link_list()
```
- Returns list of all download links you've created
- Each link has a `clickable_link` field ready to display

## shed_link_delete - Remove a download link
```
shed_link_delete(file_id="abc123-...")
```
- Removes file from Open WebUI
- Use file_id from shed_link_create() or shed_link_list()
""",

        "edit": """
# HOWTO: Edit files

## 🔥 CHOOSE YOUR WORKFLOW

### WORKFLOW 1: Direct Write (simple, no locking)
For quick edits when you don't need locking:

```
# Create or overwrite a file (simplest way!)
shed_create_file(zone="storage", path="file.txt", content="New content")

# Append to file
shed_patch_text(zone="storage", path="file.txt", content="\\nNew line", position="end")

# Replace pattern
shed_patch_text(zone="storage", path="config.py", content="DEBUG=False", pattern="DEBUG=True", position="replace")
```

💡 **Use `shed_create_file()` for creating files** - it's simpler than `shed_patch_text(..., overwrite=True)`

### WORKFLOW 2: Locked Edit (with locking)
For concurrent access or when you need rollback:

```
# Step 1: Open (locks file)
shed_lockedit_open(zone="storage", path="config.json")

# Step 2: Modify (use shed_lockedit_overwrite, NOT shed_patch_text!)
shed_lockedit_overwrite(zone="storage", path="config.json", content="new content")

# Step 3: Save OR Cancel
shed_lockedit_save(zone="storage", path="config.json")    # ⚠️ CLOSES edit mode!
# OR
shed_lockedit_cancel(zone="storage", path="config.json")  # Discard changes
```

⚠️ **CRITICAL**: `shed_lockedit_save()` CLOSES edit mode!
To edit again, you MUST call `shed_lockedit_open()` first.

```
❌ WRONG (will fail):
shed_lockedit_save(...)
shed_lockedit_save(...)  # ERROR: NOT_IN_EDIT_MODE

✅ CORRECT:
shed_lockedit_save(...)
shed_lockedit_open(...)  # Reopen first!
shed_lockedit_overwrite(...)
shed_lockedit_save(...)
```

## Quick Reference

| Task | Command |
|------|---------|
| Create/overwrite file | `shed_create_file(zone, path, content)` |
| Append to file | `shed_patch_text(..., position="end")` |
| Prepend to file | `shed_patch_text(..., position="start")` |
| Insert before line N | `shed_patch_text(..., position="before", line=N)` |
| Insert after line N | `shed_patch_text(..., position="after", line=N)` |
| Replace pattern | `shed_patch_text(..., pattern="...", position="replace")` |
| Replace line N | `shed_patch_text(..., position="replace", line=N)` |
| Safe edit (lock) | `shed_lockedit_open` → `shed_lockedit_overwrite` → `shed_lockedit_save` |

📌 **Line numbers start at 1** (first line = line=1, NOT line=0)

⚠️ **position="at" is for shed_patch_bytes (binary), NOT for text!**

## ⚠️ Creating CSV files (RFC 4180)

**Quote a field if it contains:** delimiter (`,`), newline, or double quotes.
**Escape quotes by doubling them:** `""` inside quoted fields.

```
✅ CORRECT:
name,location,comment
"Acme Corp","New York, NY","Has ""quotes"" inside"
Simple,Boston,No quotes needed

❌ WRONG:
name,location,comment
Acme Corp,New York, NY,Unquoted comma
```

Unquoted special characters break CSV parsing!
""",

        "commands": """
# HOWTO: Available commands by zone

## Check what's available
```
shed_allowed_commands()
```

## Uploads zone (READ-ONLY)
cat, head, tail, less, wc, stat, file, du, ls, find, grep, awk, sed (read),
sort, uniq, cut, diff, tar (list), unzip (list), md5sum, sha256sum, jq, etc.

## Storage zone (READ-WRITE)
All read-only commands PLUS:
cp, mv, rm, mkdir, rmdir, touch, chmod, tar (create/extract),
zip, gzip, gunzip, patch, split, csplit, truncate, etc.

Network commands (if enabled): curl, wget, git

## Documents zone (READ-WRITE + VERSIONED)
Same as Storage, with automatic Git commits.

## Group zone
Same as Documents, with ownership/permission checks.

## Builtins (ALWAYS available, no system dependency)
These work even if system commands are missing:

| Builtin | Replaces | Use when... |
|---------|----------|-------------|
| `shed_tree(zone, path, depth)` | `tree` | tree command missing |
| `shed_zip(zone, src, dest, include_empty_dirs=False)` | `zip` | zip command missing |
| `shed_unzip(zone, src, dest)` | `unzip` | unzip command missing |
| `shed_zipinfo(zone, path)` | `zipinfo` | zipinfo command missing |
| `shed_file_type(zone, path)` | `file` | file command missing |
| `shed_convert_eol(zone, path, to)` | `dos2unix` | dos2unix/unix2dos missing |
| `shed_hexdump(zone, path, offset, length)` | `xxd`/`hexdump` | hex tools missing |
| `shed_sqlite(zone, path, query, params)` | `sqlite3` | sqlite3 CLI missing |
| `shed_sqlite(zone, path, import_csv, table)` | `sqlite3 .import` | Import CSV into SQLite (fast!) |

## Workarounds for missing commands

### No `jq`? Use grep/sed for simple JSON
```
shed_exec(zone="storage", cmd="grep", args=['"key":', "file.json"])
```

### No `tree`? Use builtin
```
shed_tree(zone="storage", path=".", depth=3)
```

### No `sqlite3` CLI? Use builtin for queries
```
shed_sqlite(zone="storage", path="db.sqlite", query="SELECT * FROM users")
```

### Import CSV to SQLite (RECOMMENDED - no context pollution!)
```
shed_sqlite(zone="storage", path="db.sqlite", import_csv="data.csv", table="mytable")
```

### No `unzip`? Use builtin
```
shed_unzip(zone="storage", src="archive.zip", dest="extracted/")
```

### No `file`? Use builtin
```
shed_file_type(zone="storage", path="unknown.bin")
```

### Large file processing without loading into context
```
# Count lines
shed_exec(zone="storage", cmd="wc", args=["-l", "huge.csv"])

# Get first/last lines
shed_exec(zone="storage", cmd="head", args=["-100", "huge.csv"])
shed_exec(zone="storage", cmd="tail", args=["-100", "huge.csv"])

# Search without reading whole file
shed_exec(zone="storage", cmd="grep", args=["pattern", "huge.csv"])

# Extract specific columns (CSV)
shed_exec(zone="storage", cmd="cut", args=["-d,", "-f1,3", "data.csv"])

# Process with awk (no context pollution)
shed_exec(zone="storage", cmd="awk", args=["-F,", "{sum+=$2} END {print sum}", "data.csv"])
```
""",

        "network": """
# HOWTO: Network access

## Check if network is enabled
```
shed_parameters()
# Look for: "network_mode": "disabled" | "safe" | "all"
```

## Network modes

### disabled (default)
- No network access
- curl, wget, git clone all blocked

### safe (downloads only)
- curl/wget GET requests allowed
- git clone/fetch/pull allowed
- git push BLOCKED
- No data exfiltration possible

### all (full access - ⚠️ risky)
- Everything allowed including uploads
- git push allowed
- Use with caution

## Download with curl (requires "safe" or "all")
```
shed_exec(zone="storage", cmd="curl", args=["-L", "-o", "file.zip", "https://..."])
```

## Clone git repo (requires "safe" or "all")
```
shed_exec(zone="storage", cmd="git", args=["clone", "https://github.com/user/repo.git"])
```
""",

        "paths": """
# HOWTO: Path rules

## ⚠️ CRITICAL: Never include the zone name in the path!

The `zone` parameter already specifies WHERE to operate. The path in `args` is RELATIVE to that zone.

**Fileshed automatically rejects paths that start with the zone name** (error code: PATH_STARTS_WITH_ZONE).

### Example of the mistake

User asks: "In Documents, create a folder MyProject"

```
❌ REJECTED (would create Documents/Documents/MyProject):
shed_exec(zone="Documents", cmd="mkdir", args=["-p", "Documents/MyProject"])
→ Error: PATH_STARTS_WITH_ZONE

✅ CORRECT (creates Documents/MyProject):
shed_exec(zone="Documents", cmd="mkdir", args=["-p", "MyProject"])
```

### Why this happens

The zone parameter already points to the Documents folder:
- zone="Documents" → You're working INSIDE Documents
- args=["MyProject"] → Creates MyProject/ inside Documents
- args=["Documents/MyProject"] → Creates Documents/MyProject/ inside Documents (WRONG!)

### More examples

```
✅ CORRECT: shed_exec(zone="storage", cmd="cat", args=["projects/file.txt"])
❌ REJECTED: shed_exec(zone="storage", cmd="cat", args=["Storage/projects/file.txt"])

✅ CORRECT: shed_exec(zone="documents", cmd="ls", args=["reports"])
❌ REJECTED: shed_exec(zone="documents", cmd="ls", args=["Documents/reports"])

✅ CORRECT: shed_exec(zone="documents", cmd="mkdir", args=["-p", "Projects/2024"])
❌ REJECTED: shed_exec(zone="documents", cmd="mkdir", args=["-p", "Documents/Projects/2024"])
```

## Exception: allow_zone_in_path

In rare cases where the user explicitly wants a subfolder named after the zone
(e.g., a "Storage" folder inside Storage), use the `allow_zone_in_path` parameter:

```
# User explicitly wants: Storage/Storage/backup/
shed_exec(zone="storage", cmd="mkdir", args=["-p", "Storage/backup"], allow_zone_in_path=True)
```

This parameter is available on: `shed_exec`, `shed_patch_text`, `shed_patch_bytes`,
`shed_delete`, `shed_rename`, all `shed_lockedit_*` functions, `shed_copy_to_group`,
and all `shed_move_*/shed_copy_*` bridge functions.

**Only use this when the user explicitly confirms they want a subfolder with that name.**

## Zone roots

Paths are always relative to the zone root:
- Uploads: per-conversation (auto-managed)
- Storage: your personal workspace
- Documents: your versioned documents
- Group: shared group space

## Case sensitivity

- **Zone parameter**: case-insensitive ("Storage" = "storage" = "STORAGE")
- **Group name**: ⚠️ **CASE-SENSITIVE** ("MyTeam" ≠ "myteam" ≠ "MYTEAM")
- **File paths**: depends on filesystem (usually case-sensitive on Linux)

## Creating folders

```
shed_exec(zone="storage", cmd="mkdir", args=["-p", "projects/webapp/src"])
```

## Listing contents

```
shed_exec(zone="storage", cmd="ls", args=["-la"])           # Root of Storage
shed_exec(zone="storage", cmd="ls", args=["-la", "projects"]) # Subfolder
shed_tree(zone="storage", path=".", depth=3)        # Tree view
```
""",

        "large_files": """
# HOWTO: Process large files without context pollution

## Golden Rule
NEVER read a large file into your context. Use tools that process files on disk.

## ❌ WRONG (pollutes context)
```
content = shed_exec(zone="storage", cmd="cat", args=["huge.csv"])  # 100MB in context!
# Then trying to process it...
```

## ✅ CORRECT (data stays on disk)

### Get file info without reading
```
shed_exec(zone="storage", cmd="wc", args=["-l", "huge.csv"])       # Line count
shed_exec(zone="storage", cmd="du", args=["-h", "huge.csv"])       # File size
shed_exec(zone="storage", cmd="head", args=["-5", "huge.csv"])     # First 5 lines (structure)
```

### Search without loading
```
shed_exec(zone="storage", cmd="grep", args=["error", "huge.log"])           # Find lines
shed_exec(zone="storage", cmd="grep", args=["-c", "error", "huge.log"])     # Count matches
shed_exec(zone="storage", cmd="grep", args=["-n", "pattern", "file.txt"])   # With line numbers
```

### Extract specific data (CSV)
```
# Get specific columns
shed_exec(zone="storage", cmd="cut", args=["-d,", "-f1,3,5", "data.csv"])

# Filter rows
shed_exec(zone="storage", cmd="awk", args=["-F,", "$3 > 100", "data.csv"])

# Sum a column
shed_exec(zone="storage", cmd="awk", args=["-F,", "{sum+=$2} END {print sum}", "data.csv"])

# Count unique values
shed_exec(zone="storage", cmd="cut", args=["-d,", "-f2", "data.csv"])
# then pipe conceptually via multiple commands or awk
shed_exec(zone="storage", cmd="awk", args=["-F,", "{a[$2]++} END {for(k in a) print k,a[k]}", "data.csv"])
```

### Transform files on disk
```
# Sort a file (output to new file)
shed_exec(zone="storage", cmd="sort", args=["input.csv", "-o", "sorted.csv"])

# Remove duplicates
shed_exec(zone="storage", cmd="sort", args=["-u", "input.txt", "-o", "unique.txt"])

# Convert encoding
shed_exec(zone="storage", cmd="iconv", args=["-f", "ISO-8859-1", "-t", "UTF-8", "old.txt", "-o", "new.txt"])
```

### Split large files
```
# Split by line count (1000 lines per file)
shed_exec(zone="storage", cmd="split", args=["-l", "1000", "huge.csv", "part_"])

# Split by size (10MB per file)
shed_exec(zone="storage", cmd="split", args=["-b", "10M", "huge.bin", "chunk_"])
```

### Process into database (best for structured data)
```
# Import CSV directly into SQLite (see howto="csv_to_sqlite")
shed_exec(zone="storage", cmd="sqlite3", args=[
    "data.db", "-cmd", ".mode csv", "-cmd", ".import huge.csv mytable"
])

# Then query without loading everything
shed_sqlite(zone="storage", path="data.db", 
    query="SELECT category, COUNT(*), AVG(value) FROM mytable GROUP BY category")
```

### JSON processing
```
# Extract specific field (if jq available)
shed_exec(zone="storage", cmd="jq", args=[".results[].name", "huge.json"])

# If jq missing, use grep for simple extraction
shed_exec(zone="storage", cmd="grep", args=["-o", '"name": "[^"]*"', "data.json"])
```

### Redirect output to file (like shell > redirection)
```
# Transform JSON to CSV and save to file (instead of returning in context)
shed_exec(zone="storage", cmd="jq", 
    args=["-r", ".[] | [.name, .value] | @csv", "data.json"],
    stdout_file="output.csv")

# Combine stderr with stdout
shed_exec(zone="storage", cmd="some_cmd", args=["..."],
    stdout_file="all_output.log", redirect_stderr_to_stdout=True)
```

## Summary: Tools for large files

| Task | Tool | Example |
|------|------|---------|
| Line count | `wc -l` | `wc -l file.csv` |
| File size | `du -h` | `du -h file.csv` |
| Preview | `head`/`tail` | `head -20 file.csv` |
| Search | `grep` | `grep pattern file` |
| Columns | `cut` | `cut -d, -f1,3 file.csv` |
| Aggregation | `awk` | `awk -F, '{sum+=$2} END {print sum}' file.csv` |
| Sort | `sort` | `sort file -o sorted` |
| Transform | `sed` | `sed 's/old/new/g' file` |
| Database | `sqlite3` | `.import file.csv table` |
| Save output | `stdout_file=` | `shed_exec(..., stdout_file="out.txt")` |
"""
    }

    def _get_user_root(self, __user__: dict) -> Path:
        """Returns the user's root directory."""
        if __user__ is None:
            __user__ = {}
        user_id = __user__.get("id", "")

        # Validate user_id: must be non-empty and valid UUID format
        if not user_id or not isinstance(user_id, str):
            raise StorageError(
                "INVALID_USER",
                "User ID is missing or invalid",
                hint="Authentication required"
            )
        user_id = user_id.strip()
        if not user_id:
            raise StorageError(
                "INVALID_USER",
                "User ID is empty",
                hint="Authentication required"
            )
        # UUID format validation (8-4-4-4-12 hex pattern)
        if not UUID_PATTERN.match(user_id):
            raise StorageError(
                "INVALID_USER",
                "User ID format is invalid",
                hint="Valid UUID required"
            )

        return Path(self.valves.storage_base_path) / "users" / user_id

    def _get_groups_root(self) -> Path:
        """Returns the groups root directory."""
        return Path(self.valves.storage_base_path) / "groups"

    def _get_db_path(self) -> Path:
        """Returns the SQLite database path."""
        return Path(self.valves.storage_base_path) / "access_auth.sqlite"

    def _strip_sql_comments(self, sql: str) -> str:
        """
        Strips SQL comments from a query string.

        Removes both block comments (/* ... */) and line comments (-- ...).
        This prevents bypass attacks like AT/**/TACH or LOAD_EX--comment
        TENSION.

        :param sql: SQL query string
        :return: Query with comments removed
        """
        import re
        # Remove block comments (non-greedy to handle multiple comments)
        result = re.sub(r'/\*.*?\*/', '', sql, flags=re.DOTALL)
        # Remove line comments (-- until end of line)
        result = re.sub(r'--[^\n]*', '', result)
        return result

    def _format_size(self, size_bytes: int, short: bool = False) -> str:
        """
        Formats a byte size as a human-readable string.

        :param size_bytes: Size in bytes
        :param short: If True, use short format (1.5M), else full (1.50 MB)
        :return: Formatted string
        """
        if short:
            if size_bytes > 1024 * 1024:
                return f"{size_bytes / 1024 / 1024:.1f}M"
            elif size_bytes > 1024:
                return f"{size_bytes / 1024:.1f}K"
            else:
                return f"{size_bytes}B"
        else:
            if size_bytes > 1024 * 1024:
                return f"{size_bytes / 1024 / 1024:.2f} MB"
            elif size_bytes > 1024:
                return f"{size_bytes / 1024:.1f} KB"
            else:
                return f"{size_bytes} B"

    def _get_conv_id(self, __metadata__: dict) -> str:
        """Returns the conversation ID, validated for safe path usage."""
        if __metadata__ is None:
            __metadata__ = {}
        conv_id = __metadata__.get("chat_id", "unknown")
        # Validate conv_id: must not contain path traversal or control characters
        if conv_id and isinstance(conv_id, str):
            conv_id = conv_id.strip()
            if ".." in conv_id or "/" in conv_id or "\\" in conv_id:
                return "unknown"  # Invalid conv_id, use safe default
            if any(ord(c) < 32 for c in conv_id):
                return "unknown"  # Contains control characters
        return conv_id if conv_id else "unknown"

    def _resolve_zone(
        self,
        zone: str,
        group: Optional[str],
        __user__: dict,
        __metadata__: dict,
        require_write: bool = False,
    ) -> ZoneContext:
        """
        Resolves a zone string to a complete ZoneContext.
        
        :param zone: "uploads", "storage", "documents", or "group"
        :param group: Group name/ID (required if zone="group")
        :param __user__: Open WebUI user context
        :param __metadata__: Conversation metadata
        :param require_write: If True, rejects uploads zone
        :return: ZoneContext with all zone-specific info
        :raises StorageError: If zone invalid or access denied
        """
        # Ensure dicts are not None (safety for mutable default args)
        if __user__ is None:
            __user__ = {}
        if __metadata__ is None:
            __metadata__ = {}

        zone_lower = zone.lower()
        user_root = self._get_user_root(__user__)
        conv_id = self._get_conv_id(__metadata__)
        
        # UPLOADS: read-only, isolated per conversation
        if zone_lower == "uploads":
            if require_write:
                raise StorageError(
                    "ZONE_READONLY",
                    "Uploads zone is read-only",
                    {"zone": zone},
                    "Use 'storage' or 'documents' for write operations"
                )
            zone_path = user_root / "Uploads" / conv_id
            return ZoneContext(
                zone_root=zone_path,
                zone_name="Uploads",
                zone_lower="uploads",
                editzone_base=None,
                conv_id=conv_id,
                group_id=None,
                git_commit=False,
                readonly=True,
                whitelist=WHITELIST_READONLY,
            )
        
        # STORAGE: read/write, no Git
        elif zone_lower == "storage":
            zone_path = user_root / "Storage" / "data"
            self._ensure_dir(zone_path)
            return ZoneContext(
                zone_root=zone_path,
                zone_name="Storage",
                zone_lower="storage",
                editzone_base=user_root / "Storage",
                conv_id=conv_id,
                group_id=None,
                git_commit=False,
                readonly=False,
                whitelist=WHITELIST_READWRITE,
            )
        
        # DOCUMENTS: read/write, auto Git
        elif zone_lower == "documents":
            zone_path = user_root / "Documents" / "data"
            self._ensure_dir(zone_path)
            self._init_git_repo(zone_path)
            return ZoneContext(
                zone_root=zone_path,
                zone_name="Documents",
                zone_lower="documents",
                editzone_base=user_root / "Documents",
                conv_id=conv_id,
                group_id=None,
                git_commit=True,
                readonly=False,
                whitelist=WHITELIST_READWRITE,
            )
        
        # GROUP: like Documents but with group validation
        elif zone_lower == "group":
            if not group:
                raise StorageError(
                    "MISSING_PARAMETER",
                    "Group parameter is required for zone='group'",
                    {"zone": zone},
                    "Use: shed_xxx(zone='group', group='team-name', ...)"
                )
            
            group_id = self._validate_group_id(group)
            self._check_group_access(__user__, group_id)
            zone_path = self._ensure_group_space(group_id)
            
            return ZoneContext(
                zone_root=zone_path,
                zone_name=f"Group:{group}",
                zone_lower="group",
                editzone_base=self._get_groups_root() / group_id,
                conv_id=conv_id,
                group_id=group_id,
                git_commit=True,
                readonly=False,
                whitelist=WHITELIST_READWRITE,
            )
        
        else:
            raise StorageError(
                "INVALID_ZONE",
                f"Invalid zone: {zone}",
                {"zone": zone, "valid": ["uploads", "storage", "documents", "group"]},
                "Use one of: uploads, storage, documents, group"
            )

    def _resolve_chroot_path(self, base: Path, relative_path: str) -> Path:
        """
        Resolves a relative path within a chroot and verifies it doesn't escape.
        Raises PATH_ESCAPE if escape attempt detected.
        Also detects symlinks that could point outside the chroot.
        """
        # Clean the path
        relative_path = relative_path.lstrip("/")

        # Build path without resolving symlinks first
        raw_path = base / relative_path

        # Check for symlinks in the path that could escape chroot
        # Walk from base to target, checking each existing component
        current = base.resolve()
        parts = Path(relative_path).parts
        for i, part in enumerate(parts):
            next_path = current / part
            if next_path.is_symlink():
                # Symlink found - resolve it and verify it stays in chroot
                link_target = next_path.resolve()
                base_resolved = base.resolve()
                try:
                    link_target.relative_to(base_resolved)
                except ValueError:
                    raise StorageError(
                        "PATH_ESCAPE",
                        "Symlink escape attempt detected",
                        {"path": relative_path},
                        "Symlinks pointing outside the zone are not allowed"
                    )
            if next_path.exists():
                current = next_path.resolve()
            else:
                # Path doesn't exist yet, remaining parts are for new file/dir
                break

        # Resolve final path
        target = raw_path.resolve()
        base_resolved = base.resolve()

        # Verify we stay in chroot
        try:
            target.relative_to(base_resolved)
        except ValueError:
            raise StorageError(
                "PATH_ESCAPE",
                "Chroot escape attempt detected",
                {"path": relative_path},
                "Use only relative paths without ../"
            )

        return target

    def _validate_relative_path(
        self,
        path: str,
        zone_name: str = None,
        allow_zone_in_path: bool = False
    ) -> str:
        """
        Validates that a relative path contains no traversal.
        Returns the cleaned and normalized path.

        :param path: The path to validate
        :param zone_name: If provided, checks that path doesn't start with zone name
        :param allow_zone_in_path: If True, allows path to start with zone name
        """
        # Normalize Unicode to NFC (prevents path confusion attacks)
        path = unicodedata.normalize("NFC", path)

        # Clean
        path = path.lstrip("/")

        # Block absolute paths
        if path.startswith("/"):
            raise StorageError(
                "PATH_ESCAPE",
                "Absolute paths forbidden",
                {"path": path},
                "Use only relative paths"
            )

        # Block .. that escapes current directory
        # Virtually resolve the path to check
        parts = []
        for part in path.split("/"):
            if part == "..":
                if not parts:
                    raise StorageError(
                        "PATH_ESCAPE",
                        "Directory escape attempt",
                        {"path": path},
                        "Paths with .. going too high are forbidden"
                    )
                parts.pop()
            elif part and part != ".":
                parts.append(part)

        cleaned_path = "/".join(parts) if parts else ""

        # Check if path starts with zone name (common LLM mistake)
        if zone_name and not allow_zone_in_path and parts:
            # Zone names to check (case-insensitive): Storage, Documents, Uploads
            # For groups, zone_name is like "group:team-name", we extract just "group"
            zone_check = zone_name.split(":")[0].lower()
            first_part_lower = parts[0].lower()

            if first_part_lower == zone_check:
                raise StorageError(
                    "PATH_STARTS_WITH_ZONE",
                    f"Path '{cleaned_path}' starts with zone name '{parts[0]}'",
                    {"zone": zone_name, "path": cleaned_path, "first_component": parts[0]},
                    f"The zone parameter already sets the working directory. "
                    f"Use '{'/'.join(parts[1:])}' instead of '{cleaned_path}'. "
                    f"If you really want a subfolder named '{parts[0]}', add allow_zone_in_path=True"
                )

        return cleaned_path

    def _validate_group_id(self, group_id: str) -> str:
        """
        Validates and resolves a group identifier.
        Accepts either a group ID (UUID) or a group name (case-sensitive).
        Returns the validated group ID.
        """
        if not group_id:
            raise StorageError(
                "INVALID_GROUP_ID",
                "Group ID cannot be empty"
            )
        
        # Block path traversal characters
        if ".." in group_id or "/" in group_id or "\\" in group_id:
            raise StorageError(
                "INVALID_GROUP_ID",
                f"Invalid group ID: contains forbidden characters",
                {"group_id": group_id},
                "Group ID cannot contain '..' or path separators"
            )
        
        # Block null bytes and other control characters
        if any(ord(c) < 32 for c in group_id):
            raise StorageError(
                "INVALID_GROUP_ID",
                "Group ID contains invalid characters"
            )
        
        # Check if it's a valid UUID (group ID)
        try:
            uuid.UUID(group_id)
            return group_id  # Already a valid UUID
        except ValueError:
            pass  # Not a UUID, try to resolve as group name
        
        # Try to resolve group name to ID (case-sensitive)
        if GROUPS_AVAILABLE:
            try:
                # Search for group by name
                groups = Groups.get_all_groups()
                case_insensitive_matches = []
                
                for g in groups:
                    if g.name == group_id:
                        return g.id  # Exact match found
                    # Collect case-insensitive matches for hint
                    if g.name.lower() == group_id.lower():
                        case_insensitive_matches.append(g.name)
                
                # No exact match - check if there's a case mismatch
                if case_insensitive_matches:
                    raise StorageError(
                        "GROUP_NOT_FOUND",
                        f"Group '{group_id}' not found (name is case-sensitive)",
                        {"requested": group_id, "similar": case_insensitive_matches},
                        f"Did you mean: {', '.join(case_insensitive_matches)}?"
                    )
            except StorageError:
                raise  # Re-raise our own errors
            except Exception:
                pass
        
        # If we get here, it's not a UUID and not a known group name
        # Return as-is and let _check_group_access handle the error
        return group_id

    def _validate_command(self, cmd: str, whitelist: set, args: list = None) -> None:
        """Validates that a command is allowed."""
        if cmd in BLACKLIST_COMMANDS:
            raise StorageError(
                "COMMAND_FORBIDDEN",
                f"Command '{cmd}' is forbidden",
                {"command": cmd},
                "See shed_help() for allowed commands"
            )
        
        # Handle curl/wget separately (controlled by valves)
        if cmd in CURL_COMMANDS:
            if self.valves.network_mode == "all":
                # All curl operations allowed
                return
            elif self.valves.network_mode == "safe":
                # Only GET operations - validate args
                self._validate_curl_args_get_only(args or [])
                return
            else:
                raise StorageError(
                    "COMMAND_FORBIDDEN",
                    f"Command '{cmd}' is disabled",
                    {"command": cmd},
                    "Ask admin to set network_mode to 'safe' or 'all'"
                )
        
        if cmd not in whitelist:
            raise StorageError(
                "COMMAND_FORBIDDEN",
                f"Command '{cmd}' is not in whitelist",
                {"command": cmd, "allowed": sorted(list(whitelist))[:20]},
                "Use shed_allowed_commands() to see available commands"
            )
        
        # If git, validate subcommands
        if cmd == "git" and args is not None:
            self._validate_git_command(args)
        
        # If find, block -exec options (can execute arbitrary commands)
        if cmd == "find" and args is not None:
            for arg in args:
                if str(arg) in FIND_EXEC_OPTIONS:
                    raise StorageError(
                        "ARGUMENT_FORBIDDEN",
                        f"Option '{arg}' is forbidden for find",
                        {"argument": str(arg)},
                        "find -exec can execute arbitrary commands. Use find + manual processing instead."
                    )
        
        # If awk (or variants), block system() and getline pipes (can execute commands)
        # gawk, mawk, nawk are all awk implementations with same dangerous capabilities
        if cmd in {"awk", "gawk", "mawk", "nawk"} and args is not None:
            for arg in args:
                if AWK_DANGEROUS_PATTERNS.search(str(arg)):
                    raise StorageError(
                        "ARGUMENT_FORBIDDEN",
                        f"{cmd} script contains forbidden patterns (system, getline pipe)",
                        {"argument": str(arg)[:100]},
                        f"{cmd} system() and getline pipes can execute commands"
                    )
        
        # Block ln entirely - both symlinks and hard links have security risks
        # - Symlinks can point outside chroot
        # - Hard links can reference sensitive files on the same filesystem
        # Use cp instead for safe file duplication
        if cmd == "ln":
            raise StorageError(
                "COMMAND_FORBIDDEN",
                "ln command is forbidden for security reasons",
                {"command": "ln"},
                "Use 'cp' instead to copy files. Both symlinks and hard links pose security risks."
            )
        
        # If tar, block --absolute-names / -P (extracts to absolute paths)
        if cmd == "tar" and args is not None:
            for arg in args:
                arg_str = str(arg)
                if arg_str == "-P" or arg_str == "--absolute-names":
                    raise StorageError(
                        "ARGUMENT_FORBIDDEN",
                        "Option --absolute-names (-P) is forbidden for tar",
                        {"argument": arg_str},
                        "This option allows extracting to absolute paths outside the allowed zone."
                    )
        
        # Handle network-capable commands (ffmpeg, pandoc, convert, etc.)
        if cmd in NETWORK_CAPABLE_COMMANDS:
            self._validate_network_command(cmd, args or [])

    def _validate_curl_args_get_only(self, args: list) -> None:
        """Validates curl/wget arguments in GET-only mode (blocks upload/POST options)."""
        for arg in args:
            arg_str = str(arg)
            
            # Check if it's a forbidden option
            # Handle both "-X" and "-XPOST" formats
            for forbidden in CURL_FORBIDDEN_GET_OPTS:
                if arg_str == forbidden:
                    raise StorageError(
                        "ARGUMENT_FORBIDDEN",
                        f"Option '{arg_str}' is forbidden in GET-only mode",
                        {"argument": arg_str, "forbidden_options": sorted(CURL_FORBIDDEN_GET_OPTS)},
                        "This option allows data upload. Ask admin to set network_mode to 'all'"
                    )
                # Handle combined format: -XPOST, --request=POST
                if arg_str.startswith(forbidden + "=") or arg_str.startswith(forbidden):
                    if forbidden in {"-X", "--request", "-d", "--data", "-F", "--form", "-T"}:
                        raise StorageError(
                            "ARGUMENT_FORBIDDEN",
                            f"Option '{arg_str}' is forbidden in GET-only mode",
                            {"argument": arg_str},
                            "This option allows data upload. Ask admin to set network_mode to 'all'"
                        )

    def _validate_network_command(self, cmd: str, args: list) -> bool:
        """
        Validates network-capable commands (ffmpeg, pandoc, convert, etc.).
        
        Returns True if URLs should be allowed in subsequent _validate_args call.
        Raises StorageError if command is not allowed with current valve settings.
        """
        # Commands that can SEND data (exfiltration risk)
        if cmd in NETWORK_OUTPUT_COMMANDS:  # ffmpeg
            if self.valves.network_mode == "all":
                # All operations allowed, URLs ok
                return True
            elif self.valves.network_mode == "safe":
                # Block output protocols that can exfiltrate data
                for arg in args:
                    arg_str = str(arg).lower()
                    for protocol in FFMPEG_OUTPUT_PROTOCOLS:
                        if protocol in arg_str:
                            raise StorageError(
                                "ARGUMENT_FORBIDDEN",
                                f"Output protocol '{protocol}' is forbidden in 'safe' mode",
                                {"argument": str(arg), "protocol": protocol},
                                "This protocol can send data to remote servers. Ask admin to set network_mode to 'all'"
                            )

                # Block dangerous ffmpeg options that can be used for exfiltration
                for i, arg in enumerate(args):
                    arg_str = str(arg)
                    # Check exact match or prefix match (e.g., -metadata:s:v)
                    for dangerous_opt in FFMPEG_DANGEROUS_OPTIONS:
                        if arg_str == dangerous_opt or arg_str.startswith(dangerous_opt + ":"):
                            raise StorageError(
                                "ARGUMENT_FORBIDDEN",
                                f"ffmpeg option '{arg_str}' is forbidden in 'safe' mode",
                                {"argument": arg_str, "option": dangerous_opt},
                                "This option can be used for data exfiltration. Ask admin to set network_mode to 'all'"
                            )
                    # Check for tee muxer in format specification
                    if arg_str == "-f" and i + 1 < len(args) and str(args[i + 1]).lower() == "tee":
                        raise StorageError(
                            "ARGUMENT_FORBIDDEN",
                            "ffmpeg tee muxer is forbidden in 'safe' mode",
                            {"argument": "-f tee"},
                            "The tee muxer can duplicate output to multiple destinations. Ask admin to set network_mode to 'all'"
                        )

                # Input URLs are ok
                return True
            else:
                # Network disabled - block ffmpeg entirely
                raise StorageError(
                    "COMMAND_FORBIDDEN",
                    f"Command '{cmd}' requires network access",
                    {"command": cmd},
                    "Ask admin to set network_mode to 'safe' or 'all'"
                )
        
        # Commands that can only RECEIVE data (read-only risk)
        if cmd in NETWORK_INPUT_COMMANDS:  # ffprobe, pandoc, convert, etc.
            if self.valves.network_mode in ("safe", "all"):
                # Network access allowed, URLs ok
                return True
            else:
                # Network disabled - block URLs in arguments
                # (command itself is ok for local files)
                for arg in args:
                    arg_str = str(arg)
                    if URL_PATTERN.match(arg_str):
                        raise StorageError(
                            "ARGUMENT_FORBIDDEN",
                            f"URLs are forbidden when network is disabled",
                            {"argument": arg_str, "command": cmd},
                            "Ask admin to set network_mode to 'safe' or 'all' for URL access"
                        )
                return False
        
        return False

    def _validate_args(self, args: list, readonly: bool = False, cmd: str = "") -> None:
        """Validates arguments to detect injections and network access."""
        # Check if URL check should be skipped for network-capable commands
        skip_url_check = False
        
        # Network-capable commands (ffmpeg, pandoc, convert, etc.)
        if cmd in NETWORK_CAPABLE_COMMANDS:
            skip_url_check = self.valves.network_mode in ("safe", "all")
        
        # curl/wget are handled separately but also need URL allowance
        if cmd in CURL_COMMANDS:
            skip_url_check = self.valves.network_mode in ("safe", "all")
        
        # git clone/fetch/pull need URLs in safe/all mode
        if cmd == "git":
            skip_url_check = self.valves.network_mode in ("safe", "all")
        
        for arg in args:
            arg_str = str(arg)
            
            # Check if this argument is a URL (for network-capable commands with network enabled)
            is_allowed_url = skip_url_check and URL_PATTERN.match(arg_str)
            
            # Choose pattern based on command (some commands use | in their internal syntax)
            dangerous_pattern = (
                DANGEROUS_ARGS_PATTERN_ALLOW_PIPE 
                if cmd in COMMANDS_ALLOWING_PIPE 
                else DANGEROUS_ARGS_PATTERN
            )
            
            # Check dangerous patterns
            # For allowed URLs, we skip this check because & is common in query strings
            if not is_allowed_url and dangerous_pattern.search(arg_str):
                raise StorageError(
                    "ARGUMENT_FORBIDDEN",
                    f"Dangerous argument detected",
                    {"argument": arg_str},
                    "Characters ; | & && || > >> << $( ${ ` are forbidden. "
                    "Use < for comparisons. To save output to a file, use stdout_file parameter instead of >"
                )
            
            # Block URLs (network access via ffmpeg, pandoc, imagemagick, etc.)
            # Skip if command is network-capable and network valves are enabled
            if not skip_url_check and URL_PATTERN.match(arg_str):
                raise StorageError(
                    "ARGUMENT_FORBIDDEN",
                    f"URLs are forbidden in arguments",
                    {"argument": arg_str},
                    "Network access via URLs is blocked. Ask admin to set network_mode to 'safe' or 'all'."
                )
            
            # In readonly mode, forbid -i/--in-place for sed (in-place editing)
            if readonly and (arg_str == "-i" or arg_str.startswith("-i") or arg_str == "--in-place" or arg_str.startswith("--in-place")):
                raise StorageError(
                    "ARGUMENT_FORBIDDEN",
                    "Option -i/--in-place is forbidden in read-only mode",
                    {"argument": arg_str},
                    "This zone is read-only"
                )

    def _is_expression_not_path(self, arg: str, cmd: str) -> bool:
        """
        Determines if an argument is a regex expression rather than a path.
        Used for sed/grep/awk commands where /pattern/ syntax is common.
        """
        # Commands that use /pattern/ expressions
        expression_commands = {"sed", "grep", "egrep", "fgrep", "awk", "perl"}

        if cmd not in expression_commands or not arg.startswith("/"):
            return False

        # Clear expression indicators:
        # - Contains space: "/Team: Eng/a new line"
        # - Contains colon: "/Team: Eng/"
        # - Ends with /: "/pattern/"
        if " " in arg:
            return True
        if ":" in arg:
            return True
        if arg.endswith("/"):
            return True

        if len(arg) > 2:
            # Check for /pattern/X format where X is a single sed command
            # Valid: /foo/d, /bar/p, /baz/a text
            # Invalid: /etc/passwd (passwd is not a single letter)
            second_slash = arg.find("/", 1)
            if second_slash > 0 and second_slash < len(arg) - 1:
                after_slash = arg[second_slash + 1:]
                # Must be a single sed command letter, alone or followed by space/text
                if len(after_slash) == 1 and after_slash in "acdipqswy":
                    return True
                if len(after_slash) > 1 and after_slash[0] in "acdipqswy" and after_slash[1] in " \t/":
                    return True

        return False

    def _validate_path_args(
        self,
        args: list,
        chroot: Path,
        cmd: str = "",
        zone_name: str = None,
        allow_zone_in_path: bool = False
    ) -> list:
        """
        Validates that arguments don't allow escaping the chroot.
        Blocks: absolute paths and .. that escape chroot.

        For sed/grep/awk, expressions starting with / are NOT treated as paths.

        :param args: List of command arguments
        :param chroot: The zone root path
        :param cmd: The command being executed
        :param zone_name: If provided, checks that paths don't start with zone name
        :param allow_zone_in_path: If True, allows paths to start with zone name
        """
        chroot_resolved = chroot.resolve()

        for arg in args:
            arg_str = str(arg)

            # Skip flags (like -i, -e, -n, etc.)
            if arg_str.startswith("-"):
                continue

            # Skip regex expressions for sed/grep/awk
            if self._is_expression_not_path(arg_str, cmd):
                continue

            # Block absolute paths (that aren't expressions)
            if arg_str.startswith("/"):
                raise StorageError(
                    "PATH_ESCAPE",
                    "Absolute paths forbidden",
                    {"path": arg_str},
                    "Use only relative paths"
                )

            # Use _validate_relative_path for standard validation + zone prefix check
            # This validates: Unicode normalization, .., and zone prefix
            self._validate_relative_path(arg_str, zone_name, allow_zone_in_path)

            # Additional chroot escape check with resolved paths
            if ".." in arg_str:
                try:
                    target = (chroot / arg_str).resolve()
                    target.relative_to(chroot_resolved)
                except ValueError:
                    raise StorageError(
                        "PATH_ESCAPE",
                        "Chroot escape attempt detected",
                        {"path": arg_str},
                        "Resolved path escapes allowed zone"
                    )

        return list(args)

    def _validate_git_command(self, args: list) -> None:
        """Validates a Git subcommand based on whitelists and network valves."""
        if not args:
            raise StorageError(
                "ARGUMENT_FORBIDDEN",
                "Git command without subcommand",
                {},
                "Example: git status, git log"
            )
        
        subcmd = args[0]
        
        # Always forbidden (dangerous local operations)
        if subcmd in GIT_BLACKLIST:
            raise StorageError(
                "COMMAND_FORBIDDEN",
                f"Command 'git {subcmd}' is forbidden",
                {"subcommand": subcmd},
                "gc, prune, filter-branch are always forbidden"
            )
        
        # Network push (exfiltration) - requires network_mode="all"
        if subcmd in GIT_NETWORK_PUSH:
            if self.valves.network_mode != "all":
                raise StorageError(
                    "COMMAND_FORBIDDEN",
                    f"Command 'git {subcmd}' is disabled (network upload)",
                    {"subcommand": subcmd},
                    "Ask admin to set network_mode to 'all'"
                )
            return  # Allowed
        
        # Network download - requires network_mode="safe" or "all"
        if subcmd in GIT_NETWORK_GET:
            if not (self.valves.network_mode in ("safe", "all")):
                raise StorageError(
                    "COMMAND_FORBIDDEN",
                    f"Command 'git {subcmd}' is disabled (network access)",
                    {"subcommand": subcmd},
                    "Ask admin to set network_mode to 'safe' or 'all'"
                )
            return  # Allowed
        
        # Standard whitelist check for local operations
        if subcmd not in GIT_WHITELIST_READ and subcmd not in GIT_WHITELIST_WRITE:
            raise StorageError(
                "COMMAND_FORBIDDEN",
                f"Git subcommand '{subcmd}' is not allowed",
                {"subcommand": subcmd, "allowed_read": sorted(GIT_WHITELIST_READ),
                 "allowed_write": sorted(GIT_WHITELIST_WRITE)}
            )

    def _calculate_effective_max(self, max_output: int) -> int:
        """Calculate effective max output size based on user parameter and valve limits."""
        # LLM Guardrail: validate type before use
        if max_output is not None and not isinstance(max_output, int):
            raise StorageError(
                "INVALID_PARAMETER",
                f"max_output must be an integer or None, got: {repr(max_output)} ({type(max_output).__name__})",
                hint="Omit max_output or use an integer like max_output=50000"
            )
        if max_output is None:
            return self.valves.max_output_default
        elif max_output == 0:
            return self.valves.max_output_absolute
        else:
            return min(max_output, self.valves.max_output_absolute)

    def _truncate_output(self, output: str, effective_max: int) -> tuple:
        """Truncate output if it exceeds effective_max. Returns (output, was_truncated)."""
        if not output:
            return "", False
        if len(output) > effective_max:
            truncated = output[:effective_max] + f"\n\n... [TRUNCATED - {len(output)} bytes total, showing first {effective_max}] ..."
            return truncated, True
        return output, False

    def _exec_command(
        self, 
        cmd: str, 
        args: list, 
        cwd: Path, 
        timeout: int, 
        max_output: int = None,
        stdout_file: Path = None,
        stderr_file: Path = None,
        redirect_stderr_to_stdout: bool = False,
    ) -> dict:
        """Executes a command and returns the result.
        
        Args:
            cmd: Command to execute
            args: Command arguments
            cwd: Working directory
            timeout: Timeout in seconds
            max_output: Max output size in bytes (None=default, 0=unlimited up to absolute max)
            stdout_file: Path to redirect stdout to (None=capture in memory)
            stderr_file: Path to redirect stderr to (None=capture in memory)
            redirect_stderr_to_stdout: If True, redirect stderr to stdout (2>&1)
        """
        # Pre-compute args_str once for all checks
        args_str = " ".join(str(a) for a in args)

        # Handle tar extraction: add --no-same-owner to prevent ownership errors
        # This avoids "Cannot change ownership" errors that cause tar to return code 2
        # even though files are extracted successfully
        if cmd == "tar":
            is_extraction = any(x in args_str for x in ["-x", "--extract"])
            # Also check combined flags like -xJf, -xzf, etc.
            if not is_extraction:
                for arg in args:
                    arg_s = str(arg)
                    if arg_s.startswith("-") and not arg_s.startswith("--") and "x" in arg_s:
                        is_extraction = True
                        break
            if is_extraction and "--no-same-owner" not in args_str:
                args = ["--no-same-owner"] + list(args)

        # Handle curl: require -o/--output to prevent stdout pollution
        # Also add -sS to suppress progress but show errors
        if cmd == "curl":
            # Check for output redirection (allow if stdout_file is specified)
            has_output = any(x in args_str for x in ["-o", "--output", "-O", "--remote-name"]) or stdout_file
            if not has_output:
                raise StorageError(
                    "ARGUMENT_REQUIRED",
                    "curl requires -o to save to file",
                    {"command": "curl", "args": [str(a) for a in args]},
                    'Use: curl -L -o "filename" "url" to save directly to file. This prevents context pollution.'
                )
            if "-s" not in args_str and "--silent" not in args_str:
                args = ["-sS"] + list(args)  # -s=silent, -S=show-error

        # Handle wget: require -O/--output-document to prevent stdout pollution
        # Also add -q to suppress progress
        if cmd == "wget":
            # Check for output redirection (allow if stdout_file is specified)
            has_output = any(x in args_str for x in ["-O", "--output-document"]) or stdout_file
            if not has_output:
                raise StorageError(
                    "ARGUMENT_REQUIRED",
                    "wget requires -O to save to file",
                    {"command": "wget", "args": [str(a) for a in args]},
                    'Use: wget -O "filename" "url" to save directly to file. This prevents context pollution.'
                )
            if "-q" not in args_str and "--quiet" not in args_str:
                args = ["-q"] + list(args)
        
        # Build command
        full_cmd = [cmd] + [str(a) for a in args]
        
        # Prepare file handles for redirection
        stdout_handle = None
        stderr_handle = None
        files_to_close = []
        
        try:
            # Setup stdout redirection
            if stdout_file:
                stdout_file.parent.mkdir(parents=True, exist_ok=True)
                stdout_handle = open(stdout_file, 'w', encoding='utf-8')
                files_to_close.append(stdout_handle)
            else:
                stdout_handle = subprocess.PIPE
            
            # Setup stderr redirection
            if redirect_stderr_to_stdout:
                stderr_handle = subprocess.STDOUT
            elif stderr_file:
                stderr_file.parent.mkdir(parents=True, exist_ok=True)
                stderr_handle = open(stderr_file, 'w', encoding='utf-8')
                files_to_close.append(stderr_handle)
            else:
                stderr_handle = subprocess.PIPE
            
            # Create preexec function to set resource limits (DoS protection)
            def set_resource_limits():
                """Apply resource limits to prevent DoS attacks."""
                # Memory limit
                mem_limit_mb = self.valves.exec_memory_limit_mb
                if mem_limit_mb > 0:
                    mem_limit_bytes = mem_limit_mb * 1024 * 1024
                    try:
                        resource.setrlimit(resource.RLIMIT_AS, (mem_limit_bytes, mem_limit_bytes))
                    except (ValueError, resource.error):
                        pass  # May fail on some systems

                # CPU time limit
                cpu_limit = self.valves.exec_cpu_limit_seconds
                if cpu_limit > 0:
                    try:
                        resource.setrlimit(resource.RLIMIT_CPU, (cpu_limit, cpu_limit))
                    except (ValueError, resource.error):
                        pass  # May fail on some systems

            result = subprocess.run(
                full_cmd,
                cwd=str(cwd),
                stdout=stdout_handle,
                stderr=stderr_handle,
                text=True,
                timeout=timeout,
                preexec_fn=set_resource_limits,
            )
            
            # Close files before reading them
            for f in files_to_close:
                f.close()
            files_to_close = []
            
            # Get stdout content
            if stdout_file:
                stdout = f"[Output written to {stdout_file.name}]"
                stdout_truncated = False
            else:
                effective_max = self._calculate_effective_max(max_output)
                stdout, stdout_truncated = self._truncate_output(result.stdout or "", effective_max)

            # Get stderr content
            if stderr_file:
                stderr = f"[Errors written to {stderr_file.name}]"
                stderr_truncated = False
            elif redirect_stderr_to_stdout:
                stderr = ""
                stderr_truncated = False
            else:
                effective_max = self._calculate_effective_max(max_output)
                stderr, stderr_truncated = self._truncate_output(result.stderr or "", effective_max)
            
            response = {
                "success": result.returncode == 0,
                "cmd": cmd,
                "args": [str(a) for a in args],
                "stdout": stdout,
                "stderr": stderr,
                "returncode": result.returncode,
            }
            
            # Add file info if redirected
            if stdout_file:
                response["stdout_file"] = stdout_file.name
            if stderr_file:
                response["stderr_file"] = stderr_file.name
            
            if (not stdout_file and stdout_truncated) or (not stderr_file and not redirect_stderr_to_stdout and stderr_truncated):
                response["truncated"] = True
                response["hint"] = "Output was truncated. Use stdout_file= to save full output to a file."
            
            return response
        
        except subprocess.TimeoutExpired:
            raise StorageError(
                "TIMEOUT",
                f"Command timeout after {timeout}s",
                {"command": cmd, "timeout": timeout},
                f"Increase timeout (max: {self.valves.exec_timeout_max}s)"
            )
        except FileNotFoundError:
            raise StorageError(
                "COMMAND_NOT_FOUND",
                f"Command '{cmd}' not found on system",
                {"command": cmd},
                "Use shed_allowed_commands() to see available commands"
            )
        except StorageError:
            # Re-raise StorageError (e.g., from _calculate_effective_max validation)
            raise
        except Exception:
            raise StorageError(
                "EXEC_ERROR",
                "Execution error",
                {"command": cmd}
            )
        finally:
            # Ensure files are closed on error
            for f in files_to_close:
                try:
                    f.close()
                except OSError:
                    pass

    def _ensure_dir(self, path: Path) -> None:
        """Creates a directory and its parents if needed."""
        path.mkdir(parents=True, exist_ok=True)

    def _rm_with_empty_parents(self, filepath: Path, stop_at: Path) -> None:
        """Deletes a file then walks up deleting empty folders."""
        if filepath.exists():
            if filepath.is_dir():
                shutil.rmtree(filepath)
            else:
                filepath.unlink()
        
        # Walk up and delete empty folders
        parent = filepath.parent
        stop_at_resolved = stop_at.resolve()
        
        while parent.resolve() != stop_at_resolved:
            try:
                parent.rmdir()  # Fails if not empty
                parent = parent.parent
            except OSError:
                break

    def _get_lock_path(self, zone_root: Path, relative_path: str) -> Path:
        """Returns the lock file path."""
        return zone_root / "locks" / (relative_path + ".lock")

    def _get_editzone_path(self, zone_root: Path, conv_id: str, relative_path: str) -> Path:
        """Returns the path in editzone."""
        return zone_root / "editzone" / conv_id / relative_path

    def _acquire_lock(self, lock_path: Path, conv_id: str, user_id: str, path: str) -> None:
        """
        Atomically acquires a lock file.
        Uses exclusive file creation to prevent race conditions (TOCTOU).
        Raises FILE_LOCKED if already locked by another conversation.
        """
        self._ensure_dir(lock_path.parent)
        
        lock_data = {
            "conv_id": conv_id,
            "user_id": user_id,
            "locked_at": datetime.now(timezone.utc).isoformat(),
            "path": path,
        }
        
        # Check if lock exists and is from another conversation
        if lock_path.exists():
            try:
                existing_lock = json.loads(lock_path.read_text())
                if existing_lock.get("conv_id") != conv_id:
                    raise StorageError(
                        "FILE_LOCKED",
                        "File locked by another conversation",
                        {"locked_at": existing_lock.get("locked_at")},
                        "Wait or use shed_force_unlock() / shed_maintenance()"
                    )
                # Same conversation - can proceed (re-lock)
                lock_path.write_text(json.dumps(lock_data, indent=2))
                return
            except json.JSONDecodeError:
                # Corrupted lock - overwrite it
                pass
        
        # Try atomic creation with exclusive mode
        try:
            # os.open with O_CREAT | O_EXCL is atomic
            fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
            try:
                lock_content = json.dumps(lock_data, indent=2).encode('utf-8')
                bytes_written = os.write(fd, lock_content)
                # Ensure complete write
                if bytes_written != len(lock_content):
                    raise OSError("Partial write to lock file")
            except Exception:
                # Write failed - remove corrupt lock file
                os.close(fd)
                try:
                    lock_path.unlink(missing_ok=True)
                except OSError:
                    pass
                raise
            else:
                os.close(fd)
        except FileExistsError:
            # Race condition: another process created the lock between our check and create
            # Re-read and check
            try:
                existing_lock = json.loads(lock_path.read_text())
                if existing_lock.get("conv_id") != conv_id:
                    raise StorageError(
                        "FILE_LOCKED",
                        "File locked by another conversation",
                        {
                            "locked_at": existing_lock.get("locked_at"),
                        },
                        "Wait or use shed_force_unlock() / shed_maintenance()"
                    )
            except (json.JSONDecodeError, FileNotFoundError, OSError, PermissionError):
                # Lock was corrupted, removed, or unreadable - try to claim it
                try:
                    lock_path.write_text(json.dumps(lock_data, indent=2))
                except OSError:
                    # Cannot write lock file - propagate as storage error
                    raise StorageError(
                        "LOCK_ERROR",
                        "Cannot acquire lock",
                        hint="Check file permissions"
                    )

    def _check_lock_owner(self, lock_path: Path, user_id: str) -> None:
        """
        Verifies that the current user owns the lock.
        Raises NOT_LOCK_OWNER if not.
        """
        if lock_path.exists():
            try:
                lock_data = json.loads(lock_path.read_text())
                if lock_data.get("user_id") != user_id:
                    raise StorageError(
                        "NOT_LOCK_OWNER",
                        "You don't own this lock",
                        None,
                        "Only the user who opened the file can save/cancel"
                    )
            except (json.JSONDecodeError, OSError, PermissionError):
                pass  # Corrupted or unreadable lock, allow operation

    def _release_lock(self, lock_path: Path) -> None:
        """
        Releases a lock file. Safe to call even if lock doesn't exist.
        This is the counterpart to _acquire_lock().
        """
        try:
            lock_path.unlink(missing_ok=True)
        except OSError:
            pass  # Ignore errors when releasing lock

    def _check_file_not_locked(self, editzone_base: Path, path: str, conv_id: str) -> None:
        """
        Checks if a file is locked by another conversation.
        Raises FILE_LOCKED if the file is locked by a different conversation.
        Used by shed_delete and shed_rename to prevent operations on locked files.
        """
        lock_path = self._get_lock_path(editzone_base, path)
        if lock_path.exists():
            try:
                lock_data = json.loads(lock_path.read_text())
                if lock_data.get("conv_id") != conv_id:
                    raise StorageError(
                        "FILE_LOCKED",
                        "File locked by another conversation",
                        {"locked_at": lock_data.get("locked_at")},
                        "Wait for the other session to release the lock or use shed_force_unlock()"
                    )
            except (json.JSONDecodeError, OSError, PermissionError):
                pass  # Corrupted or unreadable lock, allow operation

    def _validate_content_size(self, content: str) -> None:
        """Checks that content doesn't exceed max size."""
        max_bytes = self.valves.max_file_size_mb * 1024 * 1024
        content_size = len(content.encode('utf-8'))
        if content_size > max_bytes:
            raise StorageError(
                "FILE_TOO_LARGE",
                f"Content too large ({content_size / 1024 / 1024:.2f} MB)",
                {"max_mb": self.valves.max_file_size_mb},
                f"Max size is {self.valves.max_file_size_mb} MB"
            )

    def _get_user_usage(self, user_root: Path) -> int:
        """Calculate total size of user's personal space in bytes."""
        total = 0
        for zone in ["Uploads", "Storage/data", "Documents/data"]:
            zone_path = user_root / zone
            if zone_path.exists():
                for f in zone_path.rglob("*"):
                    if f.is_file():
                        try:
                            total += f.stat().st_size
                        except (OSError, FileNotFoundError):
                            pass
        return total

    def _get_path_size(self, path: Path) -> int:
        """Calculate size of a file or directory in bytes."""
        if not path.exists():
            return 0
        if path.is_file():
            return path.stat().st_size
        # Directory: sum all files recursively
        total = 0
        for f in path.rglob("*"):
            if f.is_file():
                try:
                    total += f.stat().st_size
                except (OSError, FileNotFoundError):
                    pass
        return total

    def _check_quota(self, __user__: dict, additional_bytes: int) -> None:
        """
        Checks if adding additional_bytes would exceed user quota.
        Raises QUOTA_EXCEEDED if quota would be exceeded.
        """
        user_root = self._get_user_root(__user__)
        current_usage = self._get_user_usage(user_root)
        quota_bytes = self.valves.quota_per_user_mb * 1024 * 1024
        
        if current_usage + additional_bytes > quota_bytes:
            raise StorageError(
                "QUOTA_EXCEEDED",
                f"Quota exceeded: {current_usage / 1024 / 1024:.1f} MB used + {additional_bytes / 1024 / 1024:.1f} MB requested > {self.valves.quota_per_user_mb} MB quota",
                {
                    "current_usage_mb": round(current_usage / 1024 / 1024, 2),
                    "requested_mb": round(additional_bytes / 1024 / 1024, 2),
                    "quota_mb": self.valves.quota_per_user_mb,
                },
                "Free up space or contact administrator to increase quota"
            )

    def _check_group_quota(self, group_id: str, additional_bytes: int) -> None:
        """
        Checks if adding additional_bytes would exceed group quota.
        Raises QUOTA_EXCEEDED if quota would be exceeded.
        """
        group_data_path = self._get_groups_root() / group_id / "data"
        current_usage = self._get_path_size(group_data_path)
        quota_bytes = self.valves.quota_per_group_mb * 1024 * 1024
        
        if current_usage + additional_bytes > quota_bytes:
            raise StorageError(
                "QUOTA_EXCEEDED",
                f"Group quota exceeded: {current_usage / 1024 / 1024:.1f} MB used + {additional_bytes / 1024 / 1024:.1f} MB requested > {self.valves.quota_per_group_mb} MB quota",
                {
                    "group_id": group_id,
                    "current_usage_mb": round(current_usage / 1024 / 1024, 2),
                    "requested_mb": round(additional_bytes / 1024 / 1024, 2),
                    "quota_mb": self.valves.quota_per_group_mb,
                },
                "Free up space in group or contact administrator to increase quota"
            )

    def _git_run(self, args: list, cwd: Path, timeout: int = 30) -> subprocess.CompletedProcess:
        """
        Layer 2: Executes a git command.
        All git operations MUST use this method for consistency.
        Includes timeout and error handling.
        """
        try:
            result = subprocess.run(
                ["git"] + args,
                cwd=str(cwd),
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            return result
        except FileNotFoundError:
            raise StorageError(
                "GIT_NOT_AVAILABLE",
                "Git is not installed or not in PATH",
                hint="Install git or contact administrator"
            )
        except PermissionError:
            raise StorageError(
                "PERMISSION_DENIED",
                "Cannot execute git command",
                hint="Check file permissions"
            )
        except OSError:
            raise StorageError(
                "EXECUTION_ERROR",
                "Failed to execute git command",
                hint="Check system configuration"
            )
        except subprocess.TimeoutExpired:
            raise StorageError(
                "TIMEOUT",
                f"Git command timed out after {timeout}s",
                hint="Try a simpler operation or increase timeout"
            )

    def _check_command_available(self, cmd: str) -> bool:
        """
        Layer 2: Checks if a command is available on the system.
        Used for introspection (shed_allowed_commands).
        """
        return shutil.which(cmd) is not None

    def _init_git_repo(self, repo_path: Path) -> None:
        """Initializes a Git repository if needed."""
        git_dir = repo_path / ".git"
        if not git_dir.exists():
            self._ensure_dir(repo_path)
            self._git_run(["init"], repo_path)
            self._git_run(["config", "user.email", "storage@openwebui.local"], repo_path)
            self._git_run(["config", "user.name", "Fileshed"], repo_path)
            # Security: disable hooks to prevent code execution via malicious repos
            self._neutralize_git_hooks(repo_path)

    def _neutralize_git_hooks(self, repo_path: Path) -> None:
        """
        Neutralizes Git hooks to prevent arbitrary code execution.
        This is critical when cloning untrusted repositories.
        """
        hooks_path = repo_path / ".git" / "hooks"
        if hooks_path.exists():
            # Remove all hook files (they could be malicious)
            shutil.rmtree(hooks_path, ignore_errors=True)
            # Recreate empty hooks directory
            hooks_path.mkdir(exist_ok=True)
        # Configure git to use empty hooks path (defense in depth)
        self._git_run(["config", "core.hooksPath", "/dev/null"], repo_path)

    def _git_commit(self, repo_path: Path, message: str) -> None:
        """Performs a Git commit."""
        self._git_run(["add", "-A"], repo_path)
        self._git_run(["commit", "-m", message, "--allow-empty-message"], repo_path)

    def _git_commit_as_user(self, repo_path: Path, message: str, user_id: str) -> None:
        """Performs a Git commit with user as author."""
        self._git_run(["add", "-A"], repo_path)
        author = f"{user_id} <{user_id}@fileshed>"
        self._git_run(["commit", "--author", author, "-m", message, "--allow-empty-message"], repo_path)
    
    # =========================================================================
    # GROUP HELPERS
    # =========================================================================

    def _init_db(self) -> None:
        """Initialize SQLite database if needed."""
        if self._db_initialized:
            return
        
        db_path = self._get_db_path()
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(str(db_path), timeout=10.0)
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS file_ownership (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    group_id TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    owner_id TEXT NOT NULL,
                    write_access TEXT NOT NULL CHECK(write_access IN ('owner', 'group', 'owner_ro')),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(group_id, file_path)
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_ownership_group ON file_ownership(group_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_ownership_owner ON file_ownership(owner_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_ownership_path ON file_ownership(group_id, file_path)")
            conn.commit()
        finally:
            conn.close()
        
        self._db_initialized = True

    def _db_execute(self, query: str, params: tuple = ()) -> tuple:
        """
        Execute a database query.
        Returns (rows, rowcount) tuple:
        - rows: list of Row objects for SELECT, empty list for others
        - rowcount: number of affected rows for INSERT/UPDATE/DELETE
        """
        self._init_db()
        conn = sqlite3.connect(str(self._get_db_path()), timeout=10.0, isolation_level="IMMEDIATE")
        conn.row_factory = sqlite3.Row
        try:
            cursor = conn.execute(query, params)
            result = cursor.fetchall()
            rowcount = cursor.rowcount
            conn.commit()
            return result, rowcount
        finally:
            conn.close()

    def _get_user_groups(self, user_id: str) -> list:
        """Get groups the user belongs to via Open WebUI API."""
        if not GROUPS_AVAILABLE:
            return []
        try:
            return Groups.get_groups_by_member_id(user_id)
        except Exception:
            return []

    def _is_group_member(self, user_id: str, group_id: str) -> bool:
        """Check if user is member of group."""
        user_groups = self._get_user_groups(user_id)
        return any(g.id == group_id for g in user_groups)

    def _check_group_access(self, __user__: dict, group_id: str) -> None:
        """Verify user has access to group. Raises error if not."""
        if not GROUPS_AVAILABLE:
            raise StorageError(
                "GROUP_NOT_AVAILABLE",
                "Group features are not available",
                hint="Open WebUI Groups API not found"
            )

        # Check if group exists first
        group_obj = Groups.get_group_by_id(group_id)
        if group_obj is None:
            raise StorageError(
                "GROUP_NOT_FOUND",
                f"Group not found: '{group_id}'",
                {"group_id": group_id},
                "Check the group name or ID"
            )

        if __user__ is None:
            __user__ = {}
        user_id = __user__.get("id", "")
        if not self._is_group_member(user_id, group_id):
            raise StorageError(
                "GROUP_ACCESS_DENIED",
                f"You are not a member of group '{group_id}'",
                {"group_id": group_id},
                "Request access from a group administrator"
            )

    def _ensure_group_space(self, group_id: str) -> Path:
        """Ensure group space exists. Returns data path."""
        group_path = self._get_groups_root() / group_id
        data_path = group_path / "data"
        
        if not data_path.exists():
            data_path.mkdir(parents=True, exist_ok=True)
            (group_path / "editzone").mkdir(exist_ok=True)
            (group_path / "locks").mkdir(exist_ok=True)
            
            # Initialize Git repository via Layer 2
            self._git_run(["init"], data_path)
            self._git_run(["config", "user.email", "storage@openwebui"], data_path)
            self._git_run(["config", "user.name", "Fileshed"], data_path)
        
        return data_path

    def _get_group_data_path(self, group_id: str) -> Path:
        """Get data path for a group."""
        return self._get_groups_root() / group_id / "data"

    def _get_group_editzone(self, group_id: str, conv_id: str) -> Path:
        """Get editzone path for a group."""
        return self._get_groups_root() / group_id / "editzone" / conv_id

    def _get_group_locks_dir(self, group_id: str) -> Path:
        """Get locks directory for a group."""
        return self._get_groups_root() / group_id / "locks"

    def _get_file_ownership(self, group_id: str, file_path: str) -> Optional[dict]:
        """Get ownership info for a file in group space."""
        rows, _ = self._db_execute(
            "SELECT owner_id, write_access FROM file_ownership WHERE group_id = ? AND file_path = ?",
            (group_id, file_path)
        )
        if rows:
            return {"owner_id": rows[0]["owner_id"], "write_access": rows[0]["write_access"]}
        return None

    def _set_file_ownership(self, group_id: str, file_path: str, owner_id: str, write_access: str) -> None:
        """Set or update ownership for a file."""
        self._db_execute("""
            INSERT INTO file_ownership (group_id, file_path, owner_id, write_access)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(group_id, file_path) DO UPDATE SET
                owner_id = excluded.owner_id,
                write_access = excluded.write_access,
                updated_at = CURRENT_TIMESTAMP
        """, (group_id, file_path, owner_id, write_access))

    def _delete_file_ownership(self, group_id: str, file_path: str) -> None:
        """Delete ownership record for a file."""
        self._db_execute(
            "DELETE FROM file_ownership WHERE group_id = ? AND file_path = ?",
            (group_id, file_path)
        )

    def _delete_file_ownership_recursive(self, group_id: str, dir_path: str) -> int:
        """
        Delete ownership records for a directory and all its contents.
        Returns the number of records deleted.
        """
        # Delete exact match and all paths starting with dir_path/
        if dir_path:
            _, rowcount = self._db_execute(
                "DELETE FROM file_ownership WHERE group_id = ? AND (file_path = ? OR file_path LIKE ?)",
                (group_id, dir_path, dir_path + "/%")
            )
        else:
            # Empty path means root - delete all for this group
            _, rowcount = self._db_execute(
                "DELETE FROM file_ownership WHERE group_id = ?",
                (group_id,)
            )
        return rowcount if rowcount > 0 else 0

    def _update_file_ownership_paths(self, group_id: str, old_path: str, new_path: str) -> None:
        """
        Update ownership records when a directory is renamed.
        Updates the path itself and all paths under it.
        """
        # Update exact match
        self._db_execute(
            "UPDATE file_ownership SET file_path = ?, updated_at = CURRENT_TIMESTAMP WHERE group_id = ? AND file_path = ?",
            (new_path, group_id, old_path)
        )
        
        # Update all paths under old_path/
        # SQLite: replace the prefix old_path/ with new_path/
        old_prefix = old_path + "/"
        new_prefix = new_path + "/"
        self._db_execute("""
            UPDATE file_ownership 
            SET file_path = ? || SUBSTR(file_path, ?),
                updated_at = CURRENT_TIMESTAMP
            WHERE group_id = ? AND file_path LIKE ?
        """, (new_prefix, len(old_prefix) + 1, group_id, old_prefix + "%"))

    def _can_write_group_file(self, group_id: str, file_path: str, user_id: str) -> tuple:
        """
        Check if user can modify file in group space.
        Returns (can_write: bool, error_code: str|None)
        """
        ownership = self._get_file_ownership(group_id, file_path)
        
        if ownership is None:
            return True, None  # New file, anyone can create
        
        mode = ownership["write_access"]
        owner = ownership["owner_id"]
        
        if mode == "group":
            return True, None
        elif mode == "owner":
            if user_id == owner:
                return True, None
            return False, "FILE_OWNER_ONLY"
        elif mode == "owner_ro":
            return False, "FILE_READ_ONLY"
        
        return False, "PERMISSION_DENIED"

    def _can_delete_group_file(self, group_id: str, file_path: str, user_id: str) -> tuple:
        """Check if user can delete file in group space."""
        ownership = self._get_file_ownership(group_id, file_path)
        
        if ownership is None:
            return True, None  # Untracked file
        
        mode = ownership["write_access"]
        owner = ownership["owner_id"]
        
        if mode == "group":
            return True, None  # Everyone can delete
        elif mode == "owner":
            if user_id == owner:
                return True, None  # Owner can delete
            return False, "FILE_OWNER_ONLY"
        elif mode == "owner_ro":
            return False, "FILE_READ_ONLY"  # Nobody can delete, change mode first
        
        return False, "PERMISSION_DENIED"

    def _format_response(self, success: bool, data: Any = None, message: str = None) -> str:
        """Formats a JSON response."""
        response = {"success": success}
        if data is not None:
            response["data"] = data
        if message:
            response["message"] = message
        return json.dumps(response, indent=2, ensure_ascii=False)

    def _format_error(self, e: StorageError, func_name: str = None) -> str:
        """Formats a StorageError with contextual help."""
        function_help = self._get_function_help(func_name) if func_name else None
        return json.dumps(e.to_dict(function_help), indent=2, ensure_ascii=False)

    def _clamp_timeout(self, timeout: int = None) -> int:
        """Clamps timeout to configured values. Uses exec_timeout_default if not specified."""
        # LLM Guardrail: validate type before use
        if timeout is not None and not isinstance(timeout, int):
            raise StorageError(
                "INVALID_PARAMETER",
                f"timeout must be an integer or None, got: {repr(timeout)} ({type(timeout).__name__})",
                hint="Omit timeout or use an integer like timeout=30"
            )
        if timeout is None:
            timeout = self.valves.exec_timeout_default
        return max(1, min(timeout, self.valves.exec_timeout_max))
    
    # =========================================================================
    # UPLOADS (2 functions)
    # =========================================================================

    def _get_howto_description(self, howto: str) -> str:
        """Get short description for a howto topic."""
        descriptions = {
            "download": "Download files with curl (to work with them locally)",
            "csv_to_sqlite": "Import CSV/TSV data into SQLite (fast, no context pollution)",
            "upload": "Handle user-uploaded files",
            "share": "Create download links for files",
            "edit": "Edit existing files safely",
            "commands": "Available commands + workarounds when commands are missing",
            "network": "Network access configuration",
            "paths": "Path rules and examples",
            "large_files": "Process large files WITHOUT loading into context",
            "full": "Complete documentation (long)",
        }
        return descriptions.get(howto, "")

    def _get_full_help(self) -> str:
        """Return the complete documentation."""
        return """
# Fileshed - Documentation

## ⚠️ IMPORTANT: Only call shed_* functions!

```
✅ CORRECT: shed_exec(zone="storage", cmd="ls", args=["-la"])
✅ CORRECT: shed_exec(zone="storage", cmd="mkdir", args=["-p", "dir"])
✅ CORRECT: shed_patch_text(zone="storage", path="notes.txt", content="Hello")
✅ CORRECT: shed_sqlite(zone="storage", path="db.sqlite", query="SELECT * FROM t")
❌ WRONG:   _exec_command(...)  ← INTERNAL, will NOT work!
❌ WRONG:   _validate_path(...) ← INTERNAL, will NOT work!
```

All methods starting with `_` are INTERNAL implementation details.
They are NOT callable. Only `shed_*` functions are available to you.

## IMPORTANT: FILE UPLOAD WORKFLOW
When a file is uploaded, you MUST follow these steps:
  STEP 1: shed_import(import_all=True)           <- Import ALL attached files
          OR shed_import(filename="report.pdf")  <- Import ONE specific file
  STEP 2: shed_move_uploads_to_storage(src="filename", dest="filename")
NEVER skip step 1!

## PATH RULES - VERY IMPORTANT!
Each function works INSIDE its zone. Paths are relative to the zone root.
DO NOT include the zone name in paths!

  CORRECT: shed_exec(zone="storage", cmd="cat", args=["projects/file.txt"])
  WRONG:   shed_exec(zone="storage", cmd="cat", args=["Storage/projects/file.txt"])

## DOWNLOAD LINKS

Three functions to create download links:

| Function | Description |
|----------|-------------|
| shed_link_create() | Create download link |
| shed_link_list() | List your download links |
| shed_link_delete() | Remove a download link |

### shed_link_create - Create a link
  shed_link_create(zone="storage", path="report.pdf")
  shed_link_create(zone="storage", path="data.zip")

Returns: {"download_url": "/api/v1/files/{id}/content", "file_id": "..."}
The user can click the download_url to download the file.

### shed_link_list - List links
  shed_link_list()

Returns list of all download links you've created with file_id, filename, download_url.

### shed_link_delete - Remove a download link
  shed_link_delete(file_id="abc123-...")

Removes file from Open WebUI. Use file_id from create or list.

## HOW TO DO COMMON OPERATIONS

⚠️ **SHELL COMMANDS FIRST!** Use shed_exec() for ALL shell-doable operations.
Only use shed_patch_text() to CREATE or MODIFY file CONTENT.

| Operation          | Method                                                     |
|--------------------|------------------------------------------------------------|
| **Create folder**  | shed_exec(zone="storage", cmd="mkdir", args=["-p", "dir"])|
| Read file          | shed_exec(zone="storage", cmd="cat", args=["file.txt"])   |
| Copy file          | shed_exec(zone="storage", cmd="cp", args=["src", "dest"]) |
| Move/rename        | shed_exec(zone="storage", cmd="mv", args=["old", "new"])  |
| Delete file        | shed_exec(zone="storage", cmd="rm", args=["file.txt"])    |
| Delete folder      | shed_exec(zone="storage", cmd="rm", args=["-rf", "dir"])  |
| List files         | shed_exec(zone="storage", cmd="ls", args=["-la"])         |
| Search in file     | shed_exec(zone="storage", cmd="grep", args=["pat", "f"])  |
| Count lines        | shed_exec(zone="storage", cmd="wc", args=["-l", "file"])  |
| Git operations     | shed_exec(zone="documents", cmd="git", args=["log"])      |

CONTENT OPERATIONS:
| Operation              | Method                                                  |
|------------------------|---------------------------------------------------------|
| Create new file        | shed_create_file(zone, path, content)                   |
| Append to file         | shed_patch_text(zone, path, content, position="end")    |
| Replace pattern        | shed_patch_text(zone, path, content, pattern="...", position="replace") |
| Edit specific line     | shed_patch_text(zone, path, content, line=5, position="replace") |

📌 Line numbers start at 1 (first line = line=1)

❌ WRONG: Using patch_text to create directories (via .keep files)
✓ CORRECT: Using shed_exec(cmd="mkdir", args=["-p", "dir"])

## ZONES
All operations use a zone parameter: "uploads", "storage", "documents", or "group"
- **Uploads**   : Temporary import area (read + delete only)
- **Storage**   : Permanent user space (all operations, no Git)
- **Documents** : Permanent + Git versioned (auto-commit)
- **Groups**    : Shared collaborative spaces (requires group= parameter)

## UNIFIED FUNCTIONS

### Core Operations (all zones)
- shed_exec(zone, cmd, args, group?)           : Execute shell commands
- shed_patch_text(zone, path, content, ..., group?, message?)  : Edit text files
- shed_patch_bytes(zone, path, content, ..., group?, message?) : Edit binary files
- shed_delete(zone, path, group?, message?)    : Delete files/folders
- shed_rename(zone, old_path, new_path, group?, message?) : Rename/move files

### Locked Editing (with locking)
- shed_lockedit_open(zone, path, group?)           : Lock + get content
- shed_lockedit_exec(zone, path, cmd, args, group?): Execute on working copy
- shed_lockedit_overwrite(zone, path, content, group?) : Write to working copy
- shed_lockedit_save(zone, path, group?, message?) : Save + unlock + commit
- shed_lockedit_cancel(zone, path, group?)         : Discard + unlock

### Import (from chat)
- shed_import(import_all=True)              : Import all attached files
- shed_import(filename="file.txt")          : Import one specific file

### Bridges (between zones)
- shed_move_uploads_to_storage(src, dest)
- shed_move_uploads_to_documents(src, dest, message)
- shed_copy_storage_to_documents(src, dest, message)
- shed_move_documents_to_storage(src, dest, message)
- shed_copy_to_group(src_zone, src_path, group, dest_path, message, mode)

## GROUP-SPECIFIC FUNCTIONS

### Discovery
- shed_group_list()                    : List groups you belong to
- shed_group_info(group)               : Show files, ownership, stats

### Ownership Management
- shed_group_set_mode(group, path, mode)  : Change write mode
- shed_group_chown(group, path, new_owner): Transfer ownership

## WRITE MODES (Groups)
- **group**    : Anyone in group can modify (default)
- **owner**    : Only owner can modify
- **owner_ro** : Read-only for everyone (owner can delete)

## DOWNLOAD LINKS (3 functions)
- shed_link_create(zone, path, group?)  : Create download link
- shed_link_list()                      : List links
- shed_link_delete(file_id)             : Remove download link

Examples:
  shed_link_create(zone="storage", path="report.pdf")  # Returns download link
  shed_link_list()                                      # List your download links
  shed_link_delete(file_id="abc123-...")               # Remove a download link

## UTILITIES (6 functions)
- shed_help()
- shed_stats()                         : Show storage usage and quotas
- shed_parameters()                    : Show valve configuration (network_mode, quotas, etc.)
- shed_allowed_commands()
- shed_force_unlock(path, zone)        : Unlock in personal zone (storage/documents)
- shed_force_unlock(path, group=id)    : Unlock in group zone
- shed_maintenance()

## ANSWERING CONFIGURATION QUESTIONS
When user asks about configuration, call shed_parameters() first:
- "Is network enabled?" -> shed_parameters() -> check network_mode
- "Can I use curl?" -> shed_parameters() -> network_mode in ("safe", "all")
- "Can I git push?" -> shed_parameters() -> network_mode == "all"
- "What's my quota?" -> shed_parameters() -> quota_per_user_mb
- "Max file size?" -> shed_parameters() -> max_file_size_mb

## BUILTINS (8 functions - see below)

## BUILTIN FUNCTIONS (always available, no container dependency)

Unlike shed_*_exec() which needs external commands, builtins use Python:

| Function | Description |
|----------|-------------|
| shed_unzip(zone, src, dest) | Extract ZIP (replaces `unzip` command) |
| shed_zip(zone, src, dest, include_empty_dirs) | Create ZIP (replaces `zip` command) |
| shed_tree(zone, path, depth) | Directory tree (replaces `tree` command) |
| shed_zipinfo(zone, path)    | ZIP info (replaces `zipinfo` command) |
| shed_file_type(zone, path)  | File MIME type (replaces `file` command) |
| shed_convert_eol(zone, path, to) | Line endings (replaces `dos2unix`/`unix2dos`) |
| shed_hexdump(zone, path, offset, length) | Hex dump (replaces `xxd`/`hexdump`) |
| shed_sqlite(zone, path, query, params, group) | SQLite queries (replaces `sqlite3` command) |
| shed_sqlite(zone, path, import_csv, table, ...) | CSV import with auto-detection (delimiter, encoding, dates) |

Examples:
  shed_unzip(zone="storage", src="repo.zip", dest="repo")
  shed_zip(zone="storage", src="projects/app", dest="app.zip")
  shed_zip(zone="storage", src="projects", dest="backup.zip", include_empty_dirs=True)  # preserve empty dirs
  shed_tree(zone="storage", path="projects", depth=2)
  shed_zipinfo(zone="storage", path="backup.zip")
  shed_file_type(zone="uploads", path="document.pdf")
  shed_convert_eol(zone="storage", path="script.sh", to="unix")
  shed_hexdump(zone="storage", path="binary.dat", length=128)
  
  # SQLite queries
  shed_sqlite(zone="storage", path="data.db", query="SELECT * FROM users")
  shed_sqlite(zone="storage", path="data.db", query="INSERT INTO users VALUES (?, ?)", params=["Alice", "alice@ex.com"])
  
  # CSV import (auto-detects delimiter and encoding)
  shed_sqlite(zone="storage", path="data.db", import_csv="users.csv", table="users")
  
  # European CSV (semicolon, comma decimal, latin-1)
  shed_sqlite(zone="storage", path="data.db", import_csv="french.csv", table="ventes",
              delimiter=";", decimal=",", encoding="latin-1")
  
  # With date parsing (European DD/MM/YYYY)
  shed_sqlite(zone="storage", path="data.db", import_csv="orders.csv", table="orders",
              date_columns=["order_date"], date_format="dayfirst")

## ALLOWED COMMANDS
Use shed_allowed_commands() to see available commands.

## NETWORK ACCESS
Network is disabled by default. Admin can configure via the network_mode valve:

| network_mode | Effect |
|--------------|--------|
| "disabled" (default) | [X] No network. curl/wget blocked. ffmpeg blocked. URLs blocked in all commands. |
| "safe" | [OK] Downloads only. curl/wget GET, git clone/fetch/pull, ffmpeg (input only), pandoc/convert with URLs. |
| "all" | [!] Full access including upload. curl POST, git push, ffmpeg streaming output. EXFILTRATION RISK! |

Network-capable commands:
- **ffmpeg**: Blocked if disabled. In "safe" mode, output protocols (rtmp, udp, tcp, etc.) are blocked.
- **ffprobe, pandoc, convert, identify**: Local files always ok. URLs require "safe" or "all".
- **curl, wget**: Require "safe" (GET only) or "all" (all methods).
- **git**: clone/fetch/pull require "safe". push requires "all".

## DOWNLOADING FILES - IMPORTANT!
When network_mode is "safe" or "all", ALWAYS use curl via shed_*_exec() instead of fetch_url tool:

  shed_exec(zone="storage", cmd="curl", args=["-L", "-o", "data.csv", "https://example.com/data.csv"])

REQUIRED: The -o flag is MANDATORY for curl/wget. Omitting it returns an error.
This prevents context pollution when downloading large files.

Why curl instead of fetch_url?
1. **Complete download**: curl downloads the FULL file. fetch_url TRUNCATES large content.
2. **No context pollution**: File is saved to disk, not dumped into conversation context.
3. **Post-processing**: You can then unzip, grep, head, tail, awk the file as needed.

Examples:
  # Download a CSV (extension known)
  shed_exec(zone="storage", cmd="curl", args=["-L", "-o", "data.csv", "https://example.com/data.csv"])
  
  # Download and unzip
  shed_exec(zone="storage", cmd="curl", args=["-L", "-o", "repo.zip", "https://github.com/.../archive.zip"])
  shed_unzip(zone="storage", src="repo.zip", dest="repo")
  
  # Download then inspect
  shed_exec(zone="storage", cmd="curl", args=["-L", "-o", "big.json", "https://api.example.com/data"])
  shed_exec(zone="storage", cmd="head", args=["-100", "big.json"])  # First 100 lines
  shed_exec(zone="storage", cmd="jq", args=[".", "big.json"])       # Parse JSON

## DOWNLOAD WITH UNKNOWN EXTENSION
When the URL doesn't reveal the file type (e.g., Google Drive, API endpoints):

  # Step 1: Download with temporary extension
  shed_exec(zone="storage", cmd="curl", args=["-L", "-o", "sample.tmp", "https://drive.google.com/uc?id=...&export=download"])
  
  # Step 2: Detect the actual file type
  shed_file_type(zone="storage", path="sample.tmp")
  # Returns: {"mime_type": "text/csv", "extension": ".csv"}
  
  # Step 3: Rename with correct extension
  shed_rename(zone="storage", old_path="sample.tmp", new_path="sample.csv")

This workflow ensures files get proper extensions even from URLs that hide the file type.

Note: curl runs with -sS automatically (silent + show-error, no progress bar spam).
Note: stdout/stderr are truncated at 50KB to prevent context overflow.

## FORBIDDEN ARGUMENTS
- Shell metacharacters: ; | && & > >> $( ` 
- URLs: blocked unless network_mode is "safe" or "all" for network-capable commands
- find: -exec, -execdir, -ok, -okdir (can execute commands)
- awk: system(), getline pipes (can execute commands)

## REMOVED COMMANDS (security)
- xargs, timeout, env: can execute arbitrary commands
"""



    # =========================================================================
    # INTERNAL IMPLEMENTATION METHODS FOR patch_* FUNCTIONS
    # =========================================================================

    async def _patch_text_impl(
        self,
        zone: str,
        path: str,
        content: str,
        position: str,
        line: int,
        end_line: int,
        pattern: str,
        regex_flags: str,
        match_all: bool,
        overwrite: bool,
        safe: bool,
        group: str,
        message: str,
        mode: str,
        allow_zone_in_path: bool,
        __user__: dict,
        __metadata__: dict,
    ) -> str:
        """Internal implementation for text file patching."""
        if __user__ is None:
            __user__ = {}
        if __metadata__ is None:
            __metadata__ = {}
        user_id = __user__.get("id", "")
        conv_id = self._get_conv_id(__metadata__)

        # Early validation
        if not path or path.strip() == "":
            raise StorageError("MISSING_PARAMETER", "Path parameter is required")

        zone_lower = zone.lower()

        # === ZONE RESOLUTION ===
        user_root = self._get_user_root(__user__)
        git_commit = False
        group_id = None
        zone_name = None  # For zone prefix validation

        if zone_lower == "storage":
            zone_root = user_root / "Storage" / "data"
            editzone_base = user_root / "Storage"
            zone_name = "Storage"
        elif zone_lower == "documents":
            zone_root = user_root / "Documents" / "data"
            editzone_base = user_root / "Documents"
            git_commit = True
            zone_name = "Documents"
            self._init_git_repo(zone_root)
        elif zone_lower == "group":
            if not group:
                raise StorageError("MISSING_PARAMETER", "Group parameter required")
            group_id = self._validate_group_id(group)
            self._check_group_access(__user__, group_id)
            zone_root = self._ensure_group_space(group_id)
            editzone_base = self._get_groups_root() / group_id
            git_commit = True
            zone_name = f"Group:{group_id}"
        elif zone_lower == "uploads":
            raise StorageError("ZONE_READONLY", "Uploads zone is read-only", hint="Use storage or documents zone for writing")
        else:
            raise StorageError("INVALID_ZONE", f"Invalid zone: {zone}", hint="Use one of: uploads, storage, documents, group")

        self._ensure_dir(zone_root)
        path = self._validate_relative_path(path, zone_name, allow_zone_in_path)
        target_path = self._resolve_chroot_path(zone_root, path)

        # === PERMISSION CHECK (groups) ===
        if group_id:
            can_write, error = self._can_write_group_file(group_id, path, user_id)
            if not can_write and target_path.exists():
                raise StorageError(error, f"Cannot write to file: {error}")
        
        # === VALIDATE PARAMETERS ===
        if content is None:
            raise StorageError("MISSING_PARAMETER", "Content parameter is required")

        # Skip position/line/end_line/pattern validation when overwrite=True (these params are ignored)
        valid_positions = ("start", "end", "before", "after", "replace")
        if not overwrite and position not in valid_positions:
            hint = ""
            if position == "overwrite":
                hint = ". To overwrite entire file, use overwrite=True parameter instead"
            elif position == "at":
                hint = ". 'at' is for shed_patch_bytes (binary). For text, use 'before' or 'after' with line=N"
            raise StorageError(
                "INVALID_PARAMETER",
                f"Invalid position: {position}. Valid: {', '.join(valid_positions)}{hint}"
            )
        if not overwrite:
            # LLM Guardrail: validate types before comparison
            if line is not None and not isinstance(line, int):
                raise StorageError(
                    "INVALID_PARAMETER",
                    f"line must be an integer or None, got: {repr(line)} ({type(line).__name__})",
                    hint="Use line=1 for first line, line=2 for second, etc."
                )
            if end_line is not None and not isinstance(end_line, int):
                raise StorageError(
                    "INVALID_PARAMETER",
                    f"end_line must be an integer or None, got: {repr(end_line)} ({type(end_line).__name__})",
                    hint="Use end_line=5 to replace lines up to line 5"
                )

            # Validate line parameter - line=0 is explicitly invalid
            if line is not None and line < 1:
                raise StorageError("INVALID_PARAMETER", "Line must be >= 1 (first line is 1, not 0)")

            if end_line is not None and end_line < 1:
                raise StorageError("INVALID_PARAMETER", "end_line must be >= 1 (first line is 1, not 0)")

            if position in ("before", "after", "replace"):
                if line is None and pattern is None:
                    raise StorageError("MISSING_PARAMETER", f"Position '{position}' requires 'line' or 'pattern'")

            if end_line is not None and position != "replace":
                raise StorageError("INVALID_PARAMETER", "end_line only valid with position='replace'")

            if end_line is not None and end_line < line:
                raise StorageError("INVALID_PARAMETER", "end_line must be >= line")

        # === COMPILE REGEX ===
        compiled_pattern = None
        if pattern is not None and not overwrite:
            if pattern == "":
                raise StorageError("INVALID_PARAMETER", "Pattern cannot be empty")
            # LLM Guardrail: validate regex_flags type
            if not isinstance(regex_flags, str):
                raise StorageError(
                    "INVALID_PARAMETER",
                    f"regex_flags must be a string, got: {repr(regex_flags)} ({type(regex_flags).__name__})",
                    hint="Use regex_flags='i' for case-insensitive, 'im' for multiline, or '' for none"
                )
            flags = 0
            for c in regex_flags.lower():
                if c == 'i': flags |= re.IGNORECASE
                elif c == 'm': flags |= re.MULTILINE
                elif c == 's': flags |= re.DOTALL
            try:
                compiled_pattern = re.compile(pattern, flags)
            except re.error:
                raise StorageError("INVALID_PARAMETER", "Invalid regex pattern", hint="Check regex syntax")
        
        # === CHECK FILE EXISTS ===
        file_exists = target_path.exists()
        file_created = False

        if file_exists and target_path.is_dir():
            raise StorageError("NOT_A_FILE", f"Path is a directory, not a file: {path}")

        if not file_exists:
            if overwrite or position in ("start", "end"):
                file_created = True
            else:
                raise StorageError("FILE_NOT_FOUND", f"File not found: {path}")
        
        # === SIZE AND QUOTA CHECKS ===
        content_bytes = content.encode('utf-8')
        max_size = self.valves.max_file_size_mb * 1024 * 1024
        try:
            current_size = target_path.stat().st_size if file_exists else 0
        except FileNotFoundError:
            current_size = 0
        
        if current_size + len(content_bytes) > max_size:
            raise StorageError("FILE_TOO_LARGE", f"File would exceed {self.valves.max_file_size_mb} MB")
        
        if group_id:
            self._check_group_quota(group_id, len(content_bytes))
        else:
            self._check_quota(__user__, len(content_bytes))
        
        # === SAFE MODE SETUP ===
        lock_path = None
        working_path = target_path

        if safe:
            rel_path = str(target_path.relative_to(zone_root))
            lock_path = editzone_base / "locks" / (rel_path + ".lock")
            edit_path = editzone_base / "editzone" / conv_id / rel_path

            self._acquire_lock(lock_path, conv_id, user_id, rel_path)
            # NOTE: All operations after lock acquisition must be inside try block
            # to ensure lock release on failure
        else:
            if file_created:
                self._ensure_dir(target_path.parent)
                target_path.touch()

        try:
            # === SAFE MODE EDITZONE SETUP (inside try for lock cleanup) ===
            if safe:
                self._ensure_dir(edit_path.parent)
                if file_exists:
                    shutil.copy2(target_path, edit_path)
                else:
                    edit_path.touch()
                working_path = edit_path

            # === READ CONTENT ===
            if overwrite:
                lines = []
            elif file_created and not safe:
                lines = []
            else:
                with open(working_path, 'r', encoding='utf-8', errors='replace') as f:
                    lines = f.readlines()
            
            lines_affected = 0
            match_count = 0
            
            # === PERFORM EDIT ===
            if overwrite:
                lines = [content] if content else []
                lines_affected = 1
            elif position == "start":
                lines.insert(0, content)
                lines_affected = 1
            elif position == "end":
                lines.append(content)
                lines_affected = 1
            elif position == "before":
                if line is not None:
                    if line > len(lines) + 1:
                        raise StorageError("INVALID_PARAMETER", f"Line {line} beyond file ({len(lines)} lines)")
                    lines.insert(line - 1, content)
                    lines_affected = 1
                else:
                    new_lines = []
                    found = False
                    for l in lines:
                        if compiled_pattern.search(l) and (not found or match_all):
                            new_lines.append(content)
                            lines_affected += 1
                            match_count += 1
                            found = True
                        new_lines.append(l)
                    if not found:
                        raise StorageError("PATTERN_NOT_FOUND", f"Pattern not found: {pattern}")
                    lines = new_lines
            elif position == "after":
                if line is not None:
                    if line > len(lines):
                        raise StorageError("INVALID_PARAMETER", f"Line {line} beyond file ({len(lines)} lines)")
                    lines.insert(line, content)
                    lines_affected = 1
                else:
                    new_lines = []
                    found = False
                    for l in lines:
                        new_lines.append(l)
                        if compiled_pattern.search(l) and (not found or match_all):
                            new_lines.append(content)
                            lines_affected += 1
                            match_count += 1
                            found = True
                    if not found:
                        raise StorageError("PATTERN_NOT_FOUND", f"Pattern not found: {pattern}")
                    lines = new_lines
            elif position == "replace":
                if line is not None:
                    if line > len(lines):
                        raise StorageError("INVALID_PARAMETER", f"Line {line} beyond file ({len(lines)} lines)")
                    start_idx = line - 1
                    end_idx = (end_line - 1) if end_line else start_idx
                    end_idx = min(end_idx, len(lines) - 1)
                    lines_affected = end_idx - start_idx + 1
                    lines = lines[:start_idx] + [content] + lines[end_idx + 1:]
                else:
                    # Search and replace in full content (supports multiline patterns)
                    full_content = ''.join(lines)
                    if not compiled_pattern.search(full_content):
                        raise StorageError("PATTERN_NOT_FOUND", f"Pattern not found: {pattern}")

                    # Count replacements and perform substitution
                    if match_all:
                        new_content, match_count = compiled_pattern.subn(content, full_content)
                    else:
                        new_content, match_count = compiled_pattern.subn(content, full_content, count=1)

                    lines_affected = match_count
                    # Split back into lines, preserving line structure
                    if new_content.endswith('\n'):
                        lines = [l + '\n' for l in new_content[:-1].split('\n')]
                    else:
                        parts = new_content.split('\n')
                        lines = [l + '\n' for l in parts[:-1]] + [parts[-1]] if len(parts) > 1 else [new_content]
            
            # === WRITE RESULT ===
            with open(working_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            # === SAFE MODE FINALIZE ===
            if safe:
                self._ensure_dir(target_path.parent)
                shutil.move(str(working_path), str(target_path))

            # === GIT COMMIT ===
            if git_commit:
                commit_msg = message or f"Patch {path}: {position}"
                if group_id:
                    self._git_commit_as_user(zone_root, commit_msg, user_id)
                else:
                    self._git_commit(zone_root, commit_msg)
            
            # === SET GROUP OWNERSHIP ===
            if group_id and file_created:
                effective_mode = mode or self.valves.group_default_mode
                if effective_mode not in ("owner", "group", "owner_ro"):
                    effective_mode = "group"
                self._set_file_ownership(group_id, path, user_id, effective_mode)
            
            # === BUILD RESPONSE ===
            result = {
                "path": path,
                "zone": zone,
                "position": "overwrite" if overwrite else position,
                "lines_affected": lines_affected,
                "created": file_created,
                "file_size": target_path.stat().st_size,
                "safe_mode": safe,
            }
            if match_count > 0:
                result["pattern_matches"] = match_count
            if group_id:
                result["group"] = group_id
            
            action = "created" if file_created else ("overwritten" if overwrite else position)
            return self._format_response(True, data=result, message=f"File {action}: {lines_affected} line(s) affected")
            
        finally:
            # Cleanup on error: release lock and remove editzone if it wasn't moved
            if safe and lock_path:
                self._release_lock(lock_path)
                # Clean up editzone if it still exists (wasn't successfully moved)
                if 'edit_path' in dir() and edit_path.exists():
                    try:
                        edit_path.unlink()
                    except OSError:
                        pass

    async def _patch_bytes_impl(
        self,
        zone: str,
        path: str,
        content: str,
        position: str,
        offset: int,
        length: int,
        content_format: str,
        overwrite: bool,
        safe: bool,
        group: str,
        message: str,
        mode: str,
        allow_zone_in_path: bool,
        __user__: dict,
        __metadata__: dict,
    ) -> str:
        """Internal implementation for binary file patching."""
        import base64 as base64_module

        if __user__ is None:
            __user__ = {}
        if __metadata__ is None:
            __metadata__ = {}
        user_id = __user__.get("id", "")
        conv_id = self._get_conv_id(__metadata__)

        # Early validation
        if content is None:
            raise StorageError("MISSING_PARAMETER", "Content parameter is required")
        if not path or path.strip() == "":
            raise StorageError("MISSING_PARAMETER", "Path parameter is required")

        zone_lower = zone.lower()

        # === PARSE CONTENT ===
        try:
            if content_format == "hex":
                hex_clean = content.replace(" ", "").replace("\n", "")
                if len(hex_clean) % 2 != 0:
                    raise ValueError("Hex string must have even length")
                content_bytes = bytes.fromhex(hex_clean)
            elif content_format == "base64":
                content_bytes = base64_module.b64decode(content)
            elif content_format == "raw":
                content_bytes = content.encode('utf-8')
            else:
                raise StorageError("INVALID_PARAMETER", f"Invalid content_format: {content_format}")
        except ValueError:
            raise StorageError("INVALID_PARAMETER", "Invalid content encoding", hint=f"Content must be valid {content_format}")

        # === ZONE RESOLUTION ===
        user_root = self._get_user_root(__user__)
        git_commit = False
        group_id = None
        zone_name = None  # For zone prefix validation

        if zone_lower == "storage":
            zone_root = user_root / "Storage" / "data"
            editzone_base = user_root / "Storage"
            zone_name = "Storage"
        elif zone_lower == "documents":
            zone_root = user_root / "Documents" / "data"
            editzone_base = user_root / "Documents"
            git_commit = True
            zone_name = "Documents"
            self._init_git_repo(zone_root)
        elif zone_lower == "group":
            if not group:
                raise StorageError("MISSING_PARAMETER", "Group parameter required")
            group_id = self._validate_group_id(group)
            self._check_group_access(__user__, group_id)
            zone_root = self._ensure_group_space(group_id)
            editzone_base = self._get_groups_root() / group_id
            git_commit = True
            zone_name = f"Group:{group_id}"
        elif zone_lower == "uploads":
            raise StorageError("ZONE_READONLY", "Uploads zone is read-only", hint="Use storage or documents zone for writing")
        else:
            raise StorageError("INVALID_ZONE", f"Invalid zone: {zone}", hint="Use one of: uploads, storage, documents, group")

        self._ensure_dir(zone_root)
        path = self._validate_relative_path(path, zone_name, allow_zone_in_path)
        target_path = self._resolve_chroot_path(zone_root, path)

        # === PERMISSION CHECK ===
        if group_id:
            can_write, error = self._can_write_group_file(group_id, path, user_id)
            if not can_write and target_path.exists():
                raise StorageError(error, f"Cannot write to file: {error}")
        
        # === VALIDATE PARAMETERS ===
        # Skip position/offset/length validation when overwrite=True (these params are ignored)
        valid_positions = ("start", "end", "at", "replace")
        if not overwrite and position not in valid_positions:
            hint = ""
            if position == "overwrite":
                hint = ". To overwrite entire file, use overwrite=True parameter instead"
            raise StorageError(
                "INVALID_PARAMETER",
                f"Invalid position: {position}. Valid: {', '.join(valid_positions)}{hint}"
            )

        if not overwrite and position in ("at", "replace") and offset is None:
            raise StorageError("MISSING_PARAMETER", f"Position '{position}' requires 'offset'")

        if not overwrite and position == "replace" and length is None:
            raise StorageError("MISSING_PARAMETER", "Position 'replace' requires 'length'")

        # LLM Guardrail: validate types before comparison
        if offset is not None and not isinstance(offset, int):
            raise StorageError(
                "INVALID_PARAMETER",
                f"offset must be an integer or None, got: {repr(offset)} ({type(offset).__name__})",
                hint="Use offset=0 for start of file, offset=100 for byte 100, etc."
            )
        if length is not None and not isinstance(length, int):
            raise StorageError(
                "INVALID_PARAMETER",
                f"length must be an integer or None, got: {repr(length)} ({type(length).__name__})",
                hint="Use length=10 to replace 10 bytes"
            )

        if offset is not None and offset < 0:
            raise StorageError("INVALID_PARAMETER", "Offset must be >= 0")

        if length is not None and length < 0:
            raise StorageError("INVALID_PARAMETER", "Length must be >= 0")
        
        # === CHECK FILE EXISTS ===
        file_exists = target_path.exists()
        file_created = False
        
        if not file_exists:
            if position in ("start", "end"):
                file_created = True
            else:
                raise StorageError("FILE_NOT_FOUND", f"File not found: {path}")
        
        # === SIZE CHECKS ===
        max_size = self.valves.max_file_size_mb * 1024 * 1024
        try:
            current_size = target_path.stat().st_size if file_exists else 0
        except FileNotFoundError:
            current_size = 0

        # Only validate offset bounds when it will actually be used
        if offset is not None and position in ("at", "replace") and offset > current_size:
            raise StorageError("INVALID_PARAMETER", f"Offset {offset} beyond file size ({current_size})")
        
        bytes_removed = 0
        if position == "replace" and offset < current_size:
            bytes_removed = min(length, current_size - offset)
        
        if current_size + len(content_bytes) - bytes_removed > max_size:
            raise StorageError("FILE_TOO_LARGE", f"File would exceed {self.valves.max_file_size_mb} MB")
        
        if group_id:
            self._check_group_quota(group_id, len(content_bytes))
        else:
            self._check_quota(__user__, len(content_bytes))
        
        # === SAFE MODE SETUP ===
        lock_path = None
        working_path = target_path

        if safe:
            rel_path = str(target_path.relative_to(zone_root))
            lock_path = editzone_base / "locks" / (rel_path + ".lock")
            edit_path = editzone_base / "editzone" / conv_id / rel_path

            self._acquire_lock(lock_path, conv_id, user_id, rel_path)
            # NOTE: All operations after lock acquisition must be inside try block
            # to ensure lock release on failure
        else:
            if file_created:
                self._ensure_dir(target_path.parent)
                target_path.touch()

        try:
            # === SAFE MODE EDITZONE SETUP (inside try for lock cleanup) ===
            if safe:
                self._ensure_dir(edit_path.parent)
                if file_exists:
                    shutil.copy2(target_path, edit_path)
                else:
                    edit_path.touch()
                working_path = edit_path

            # === READ DATA ===
            if file_created and not safe:
                data = bytearray()
            else:
                with open(working_path, 'rb') as f:
                    data = bytearray(f.read())
            
            bytes_affected = len(content_bytes)
            
            # === PERFORM EDIT ===
            if overwrite:
                # Complete file replacement
                data = bytearray(content_bytes)
            elif position == "start":
                data = bytearray(content_bytes) + data
            elif position == "end":
                data.extend(content_bytes)
            elif position == "at":
                data = data[:offset] + bytearray(content_bytes) + data[offset:]
            elif position == "replace":
                end_offset = min(offset + length, len(data))
                bytes_affected = end_offset - offset
                data = data[:offset] + bytearray(content_bytes) + data[end_offset:]
            
            # === WRITE RESULT ===
            with open(working_path, 'wb') as f:
                f.write(data)
            
            # === SAFE MODE FINALIZE ===
            if safe:
                self._ensure_dir(target_path.parent)
                shutil.move(str(working_path), str(target_path))

            # === GIT COMMIT ===
            if git_commit:
                commit_msg = message or f"Patch bytes {path}: {position}"
                if group_id:
                    self._git_commit_as_user(zone_root, commit_msg, user_id)
                else:
                    self._git_commit(zone_root, commit_msg)
            
            # === SET GROUP OWNERSHIP ===
            if group_id and file_created:
                effective_mode = mode or self.valves.group_default_mode
                if effective_mode not in ("owner", "group", "owner_ro"):
                    effective_mode = "group"
                self._set_file_ownership(group_id, path, user_id, effective_mode)
            
            # === BUILD RESPONSE ===
            result = {
                "path": path,
                "zone": zone,
                "position": "overwrite" if overwrite else position,
                "bytes_written": len(content_bytes),
                "bytes_affected": bytes_affected,
                "created": file_created,
                "file_size": target_path.stat().st_size,
                "safe_mode": safe,
                "content_format": content_format,
            }
            if offset is not None and not overwrite:
                result["offset"] = offset
            if group_id:
                result["group"] = group_id

            action = "created" if file_created else ("overwritten" if overwrite else "patched")
            return self._format_response(True, data=result,
                message=f"File {action}: {len(content_bytes)} bytes written")
            
        finally:
            # Cleanup on error: release lock and remove editzone if it wasn't moved
            if safe and lock_path:
                self._release_lock(lock_path)
                # Clean up editzone if it still exists (wasn't successfully moved)
                if 'edit_path' in dir() and edit_path.exists():
                    try:
                        edit_path.unlink()
                    except OSError:
                        pass


    # =========================================================================
    # UNIFIED ZONE FUNCTIONS
    # =========================================================================
    # These 10 functions replace 32 zone-specific functions.
    # All operations now use: shed_xxx(zone="...", ...)
    #
    # ⚠️ IMPORTANT: Use shed_exec() for ALL shell-doable operations!
    #    Only use shed_patch_text() to CREATE or MODIFY file CONTENT.
    #
    #    ✓ Create directory: shed_exec(zone="storage", cmd="mkdir", args=["-p", "dir"])
    #    ✗ WRONG: shed_patch_text(path="dir/.keep", content="")
    # =========================================================================


class Tools:
    """
    Fileshed - Persistent file management with collaboration.
    
    ╔═══════════════════════════════════════════════════════════════════════════╗
    ║  CRITICAL: UPLOADED FILES WORKFLOW                                        ║
    ║  When user uploads files, ALWAYS do this FIRST:                           ║
    ║    1. shed_import(import_all=True)                                       ║
    ║    2. shed_exec(zone="uploads", cmd="ls", args=["-la"])                  ║
    ║  Then move files to Storage or Documents as needed.                       ║
    ╚═══════════════════════════════════════════════════════════════════════════╝
    
    ╔═══════════════════════════════════════════════════════════════════════════╗
    ║  PATH RULES - IMPORTANT!                                                  ║
    ║  Each function already works INSIDE its zone. Use relative paths only.   ║
    ║                                                                           ║
    ║  ✓ CORRECT: shed_exec(zone="storage", cmd="cat", args=["projects/f.txt"])║
    ║  ✗ WRONG:   shed_exec(zone="storage", cmd="cat", args=["Storage/..."])  ║
    ║                                                                           ║
    ║  The zone name is NOT part of the path!                                   ║
    ╚═══════════════════════════════════════════════════════════════════════════╝
    
    ╔═══════════════════════════════════════════════════════════════════════════╗
    ║  ⚠️ SHELL COMMANDS FIRST!                                                 ║
    ║                                                                           ║
    ║  Use shed_exec(zone, cmd, args) for ALL shell-doable operations:         ║
    ║    • mkdir:  shed_exec(zone="storage", cmd="mkdir", args=["-p", "dir"])  ║
    ║    • Copy:   shed_exec(zone="storage", cmd="cp", args=["src", "dst"])    ║
    ║    • Move:   shed_exec(zone="storage", cmd="mv", args=["old", "new"])    ║
    ║    • Read:   shed_exec(zone="storage", cmd="cat", args=["file.txt"])     ║
    ║    • Delete: shed_exec(zone="storage", cmd="rm", args=["file.txt"])      ║
    ║    • Git:    shed_exec(zone="documents", cmd="git", args=["log"])        ║
    ║                                                                           ║
    ║  FILE CONTENT operations:                                                ║
    ║    • Create: shed_create_file(zone, path, content)                       ║
    ║    • Append: shed_patch_text(zone, path, content, position="end")        ║
    ║                                                                           ║
    ║  ❌ WRONG: shed_patch_text(path="dir/.keep") to create directories        ║
    ║  ✓ RIGHT: shed_exec(cmd="mkdir", args=["-p", "dir"])                     ║
    ╚═══════════════════════════════════════════════════════════════════════════╝
    
    ZONES (use zone= parameter):
    • zone="uploads"    -> works in Uploads/    (temporary, per-conversation)
    • zone="storage"    -> works in Storage/    (permanent, no versioning)
    • zone="documents"  -> works in Documents/  (permanent, Git versioned)
    • zone="group"      -> works in Groups/     (requires group= parameter)
    
    CROSS-ZONE TRANSFERS (special functions):
    • shed_move_uploads_to_storage(src, dest)
    • shed_move_uploads_to_documents(src, dest)
    • shed_copy_storage_to_documents(src, dest)
    • shed_move_documents_to_storage(src, dest)
    • shed_copy_to_group(src_zone, src_path, group, dest_path)
    
    GROUP WRITE MODES:
    • "group"    -> Anyone can edit (default)
    • "owner"    -> Only owner can edit
    • "owner_ro" -> Read-only for everyone
    """
    
    class Valves(BaseModel):
        """Tool configuration via Open WebUI interface."""
        storage_base_path: str = Field(
            default="/app/backend/data/user_files",
            description="Storage root path (contains users/ and groups/)"
        )
        quota_per_user_mb: int = Field(
            default=1000,
            description="Quota per user in MB (personal space)"
        )
        quota_per_group_mb: int = Field(
            default=2000,
            description="Quota per group in MB (shared space)"
        )
        max_file_size_mb: int = Field(
            default=300,
            description="Max file size in MB"
        )
        lock_max_age_hours: int = Field(
            default=24,
            description="Max lock duration before expiration"
        )
        exec_timeout_default: int = Field(
            default=30,
            description="Default command timeout (seconds)"
        )
        exec_timeout_max: int = Field(
            default=300,
            description="Maximum allowed timeout (seconds)"
        )
        group_default_mode: str = Field(
            default="group",
            description="Default write mode for new group files: 'owner', 'group', or 'owner_ro'"
        )
        network_mode: str = Field(
            default="disabled",
            description="Network access mode: 'disabled' (default, no network), 'safe' (downloads only, blocks exfiltration), or 'all' ([!] unrestricted, enables data exfiltration)"
        )
        openwebui_api_url: str = Field(
            default="http://localhost:8080",
            description="Open WebUI base URL for shed_link_create(). Use ONLY the base URL without /api path. Examples: http://localhost:8080, https://chat.example.com. The /api/v1/files/ path is added automatically."
        )
        max_output_default: int = Field(
            default=50000,
            description="Default max output size in bytes (~50KB). Use 0 for no limit (up to max_output_absolute)."
        )
        max_output_absolute: int = Field(
            default=5000000,
            description="Absolute max output size in bytes (~5MB). Even max_output=0 cannot exceed this."
        )
        exec_memory_limit_mb: int = Field(
            default=512,
            description="Memory limit for subprocess execution in MB (0 = no limit). Protects against DoS."
        )
        exec_cpu_limit_seconds: int = Field(
            default=60,
            description="CPU time limit for subprocess in seconds (0 = no limit). Protects against CPU exhaustion."
        )
        sqlite_readonly: bool = Field(
            default=False,
            description="If True, SQLite queries are restricted to SELECT only (no INSERT/UPDATE/DELETE/DROP). Safer for untrusted data."
        )
    
    class UserValves(BaseModel):
        """Per-user configuration. Users can set these in Tools > Fileshed > Settings."""
        # Note: shed_link_* functions use internal API, no user configuration needed
        pass
    
    def __init__(self):
        self.valves = self.Valves()
        self._core = _FileshedCore(self)
    
    # =========================================================================
    # INTERNAL IMPLEMENTATION METHODS FOR patch_* FUNCTIONS
    # =========================================================================
    
    async def shed_exec(
        self,
        zone: str,
        cmd: str,
        args: list = None,
        timeout: int = None,
        max_output: int = None,
        stdout_file: str = None,
        stderr_file: str = None,
        redirect_stderr_to_stdout: bool = False,
        group: str = None,
        allow_zone_in_path: bool = False,
        __user__: dict = None,
        __metadata__: dict = None,
    ) -> str:
        """
        Execute a command in the specified zone.

        :param zone: Target zone ("uploads", "storage", "documents", or "group")
        :param cmd: Command to execute (must be in whitelist)
        :param args: Command arguments - file paths go here
        :param timeout: Timeout in seconds (default: 30, max: 300)
        :param max_output: Max output bytes (None=50KB, 0=5MB max)
        :param stdout_file: Save stdout to this file instead of returning it
        :param stderr_file: Save stderr to this file instead of returning it
        :param redirect_stderr_to_stdout: Merge stderr into stdout (like 2>&1)
        :param group: Group name/ID (required if zone="group")
        :param allow_zone_in_path: Allow paths starting with zone name (default: False).
            By default, paths like "Documents/folder" in zone="documents" are rejected
            to prevent accidental duplication. Set True only if you really want a
            subfolder named after the zone.
        :return: Command output as JSON

        Examples:
            shed_exec(zone="uploads", cmd="cat", args=["file.txt"])
            shed_exec(zone="storage", cmd="ls", args=["-la"])
            shed_exec(zone="storage", cmd="mkdir", args=["-p", "projects/2024"])
            shed_exec(zone="storage", cmd="grep", args=["-r", "TODO", "."])
            shed_exec(zone="documents", cmd="git", args=["log", "--oneline"])
            shed_exec(zone="group", group="team", cmd="ls", args=["-la"])

            # Redirect output to file (like shell > redirection)
            shed_exec(zone="storage", cmd="jq", args=["-r", ".[]", "data.json"], stdout_file="output.txt")

        Notes:
        - uploads: read-only commands only
        - documents/group: git commands allowed
        - File paths in args are relative to zone root (don't include zone name!)
        - Use mkdir -p to create directories (NOT patch_text with .keep files!)
        - stdout_file/stderr_file: paths relative to zone root
        """
        try:
            args = args or []  # Handle None default
            ctx = self._core._resolve_zone(zone, group, __user__, __metadata__)

            # Validate command against zone whitelist
            self._core._validate_command(cmd, ctx.whitelist, args)
            
            # Validate arguments (path escapes, network, etc.)
            self._core._validate_args(args, ctx.readonly, cmd)
            validated_args = self._core._validate_path_args(
                args, ctx.zone_root, cmd,
                zone_name=ctx.zone_name,
                allow_zone_in_path=allow_zone_in_path
            )
            
            # Validate and resolve output file paths
            stdout_path = None
            stderr_path = None
            
            if stdout_file:
                if ctx.readonly:
                    raise StorageError(
                        "ZONE_READONLY",
                        "Cannot write stdout_file in read-only zone",
                        {"zone": zone},
                        "Use a writable zone (storage, documents)"
                    )
                # Validate path doesn't escape
                self._core._validate_path_args(
                    [stdout_file], ctx.zone_root, cmd,
                    zone_name=ctx.zone_name,
                    allow_zone_in_path=allow_zone_in_path
                )
                stdout_path = ctx.zone_root / stdout_file

            if stderr_file:
                if ctx.readonly:
                    raise StorageError(
                        "ZONE_READONLY",
                        "Cannot write stderr_file in read-only zone",
                        {"zone": zone},
                        "Use a writable zone (storage, documents)"
                    )
                # Validate path doesn't escape
                self._core._validate_path_args(
                    [stderr_file], ctx.zone_root, cmd,
                    zone_name=ctx.zone_name,
                    allow_zone_in_path=allow_zone_in_path
                )
                stderr_path = ctx.zone_root / stderr_file
            
            # Execute
            result = self._core._exec_command(
                cmd, validated_args,
                cwd=ctx.zone_root,
                timeout=self._core._clamp_timeout(timeout),
                max_output=max_output,
                stdout_file=stdout_path,
                stderr_file=stderr_path,
                redirect_stderr_to_stdout=redirect_stderr_to_stdout,
            )

            # Security: neutralize git hooks after clone to prevent code execution
            # from malicious repositories
            if cmd == "git" and args and args[0] == "clone" and result["returncode"] == 0:
                # Determine the cloned repo directory
                # git clone <url> [target] - target is last non-flag arg, or derived from URL
                clone_target = None
                for arg in reversed(args[1:]):
                    arg_str = str(arg)
                    if not arg_str.startswith("-"):
                        clone_target = arg_str
                        break

                if clone_target:
                    # Check if it's a URL (last arg is URL, so repo dir is derived from URL)
                    if "://" in clone_target or clone_target.endswith(".git"):
                        # Extract repo name from URL
                        repo_name = clone_target.rstrip("/").split("/")[-1]
                        if repo_name.endswith(".git"):
                            repo_name = repo_name[:-4]
                        # Fallback if repo_name is empty (edge case: malformed URL)
                        if not repo_name:
                            repo_name = "repository"
                        clone_path = ctx.zone_root / repo_name
                    else:
                        clone_path = ctx.zone_root / clone_target

                    if clone_path.exists() and (clone_path / ".git").exists():
                        self._core._neutralize_git_hooks(clone_path)

            response_data = {
                "zone": ctx.zone_name,
                "command": cmd,
                "args": args,
                "stdout": result["stdout"],
                "stderr": result["stderr"],
                "returncode": result["returncode"],
                "truncated": result.get("truncated", False),
            }
            
            if stdout_file:
                response_data["stdout_file"] = stdout_file
                if stdout_path and stdout_path.exists():
                    response_data["stdout_file_size"] = stdout_path.stat().st_size
            if stderr_file:
                response_data["stderr_file"] = stderr_file
                if stderr_path and stderr_path.exists():
                    response_data["stderr_file_size"] = stderr_path.stat().st_size
            
            return self._core._format_response(True, data=response_data)
            
        except StorageError as e:
            return self._core._format_error(e, "shed_exec")
        except Exception:
            return self._core._format_response(False, message="Unexpected error during command execution")

    async def shed_create_file(
        self,
        zone: str,
        path: str,
        content: str,
        file_type: str = "text",
        content_format: str = "hex",
        group: str = None,
        message: str = None,
        mode: str = None,
        allow_zone_in_path: bool = False,
        __user__: dict = None,
        __metadata__: dict = None,
    ) -> str:
        """
        Create a new file or overwrite an existing file with the given content.

        This is the simplest way to write a file. For appending or patching, use shed_patch_text/bytes.

        :param zone: Target zone ("storage", "documents", or "group")
        :param path: File path relative to zone (don't include zone name!)
        :param content: File content (text string, or encoded binary if file_type="bytes")
        :param file_type: "text" (default) or "bytes"
        :param content_format: For bytes only: "hex" (default), "base64", or "raw"
        :param group: Group name/ID (required if zone="group")
        :param message: Git commit message (documents/group only)
        :param mode: Ownership mode for new files in group: "owner", "group", "owner_ro"
        :param allow_zone_in_path: Allow path starting with zone name (default: False)
        :return: Creation result as JSON

        Examples:
            shed_create_file(zone="storage", path="hello.txt", content="Hello, world!")
            shed_create_file(zone="documents", path="README.md", content="# My Project", message="Init")
            shed_create_file(zone="storage", path="data.bin", content="48454C4C4F", file_type="bytes")
            shed_create_file(zone="storage", path="img.png", content="iVBORw0K...", file_type="bytes", content_format="base64")
        """
        # Validate file_type
        file_type_lower = file_type.lower() if isinstance(file_type, str) else ""
        if file_type_lower not in ("text", "bytes"):
            return self._core._format_response(
                False,
                error="INVALID_PARAMETER",
                message=f"file_type must be 'text' or 'bytes', got: {repr(file_type)}",
                hint="Use file_type='text' for text files or file_type='bytes' for binary"
            )

        # Delegate to appropriate patch function with overwrite=True
        if file_type_lower == "bytes":
            result = await self.shed_patch_bytes(
                zone=zone, path=path, content=content,
                content_format=content_format, overwrite=True,
                group=group, message=message, mode=mode,
                allow_zone_in_path=allow_zone_in_path,
                __user__=__user__, __metadata__=__metadata__,
            )
        else:
            result = await self.shed_patch_text(
                zone=zone, path=path, content=content,
                overwrite=True, group=group, message=message, mode=mode,
                allow_zone_in_path=allow_zone_in_path,
                __user__=__user__, __metadata__=__metadata__,
            )

        # Add hint explaining this is a wrapper function
        try:
            import json
            parsed = json.loads(result)
            if parsed.get("success"):
                parsed["hint"] = "shed_create_file is a wrapper for shed_patch_text/bytes with overwrite=True. It exists because it's intuitive to find and use."
                return json.dumps(parsed)
        except (json.JSONDecodeError, TypeError):
            pass
        return result

    async def shed_patch_text(
        self,
        zone: str,
        path: str,
        content: str,
        position: str = "end",
        line: int = None,
        end_line: int = None,
        pattern: str = None,
        regex_flags: str = "",
        match_all: bool = False,
        overwrite: bool = False,
        safe: bool = True,
        group: str = None,
        message: str = None,
        mode: str = None,
        allow_zone_in_path: bool = False,
        __user__: dict = None,
        __metadata__: dict = None,
    ) -> str:
        """
        Edit a text file in the specified zone.

        ⚠️ Use this ONLY for file CONTENT operations!
        For creating directories, use: shed_exec(zone, cmd="mkdir", args=["-p", "dir"])

        :param zone: Target zone ("storage", "documents", or "group")
        :param path: File path relative to zone (don't include zone name!)
        :param content: Content to write
        :param position: "start", "end", "before", "after", or "replace" (NOT "overwrite" or "at"!)
        :param line: Line number for "before"/"after"/"replace" (first line is 1, not 0)
        :param end_line: End line for range replacement (only with position="replace")
        :param pattern: Regex pattern for "replace"
        :param regex_flags: Regex flags (i=ignore case, m=multiline, s=dotall)
        :param match_all: Replace all pattern matches (default: first only)
        :param overwrite: True=replace entire file content, False=patch at position (default: False).
                          Note: overwrite=False on existing file APPENDS/PATCHES, does NOT fail!
        :param safe: Lock file during edit
        :param group: Group name/ID (required if zone="group")
        :param message: Git commit message (documents/group only, ignored for storage)
        :param mode: Ownership mode for new files in group: "owner", "group", "owner_ro"
        :param allow_zone_in_path: Allow path starting with zone name (default: False)
        :return: Edit result as JSON

        Examples:
            shed_patch_text(zone="storage", path="notes.txt", content="New line\\n", position="end")
            shed_patch_text(zone="storage", path="file.txt", content="inserted\\n", position="before", line=5)
            shed_patch_text(zone="storage", path="config.py", content="DEBUG=True", pattern="DEBUG=.*", position="replace")
            shed_patch_text(zone="documents", path="README.md", content="# Title", overwrite=True, message="Init")
        """
        try:
            return await self._core._patch_text_impl(
                zone=zone, path=path, content=content,
                position=position, line=line, end_line=end_line,
                pattern=pattern, regex_flags=regex_flags, match_all=match_all,
                overwrite=overwrite, safe=safe, group=group,
                message=message, mode=mode,
                allow_zone_in_path=allow_zone_in_path,
                __user__=__user__, __metadata__=__metadata__,
            )
        except StorageError as e:
            return self._core._format_error(e, "shed_patch_text")
        except Exception:
            return self._core._format_response(False, message="Unexpected error while editing text file")

    async def shed_patch_bytes(
        self,
        zone: str,
        path: str,
        content: str,
        content_format: str = "hex",
        position: str = "end",
        offset: int = None,
        length: int = None,
        overwrite: bool = False,
        safe: bool = True,
        group: str = None,
        message: str = None,
        mode: str = None,
        allow_zone_in_path: bool = False,
        __user__: dict = None,
        __metadata__: dict = None,
    ) -> str:
        """
        Edit a binary file in the specified zone.

        :param zone: Target zone ("storage", "documents", or "group")
        :param path: File path relative to zone (don't include zone name!)
        :param content: Content to write (format depends on content_format)
        :param content_format: "hex" (default), "base64", or "raw"
        :param position: "start", "end", "at", or "replace" (ignored if overwrite=True)
        :param offset: Byte offset for "at"/"replace"
        :param length: Bytes to replace for "replace"
        :param overwrite: True=replace entire file, False=patch at position (default: False)
        :param safe: Lock file during edit
        :param group: Group name/ID (required if zone="group")
        :param message: Git commit message (documents/group only)
        :param mode: Ownership mode for new files in group
        :param allow_zone_in_path: Allow path starting with zone name (default: False)
        :return: Edit result as JSON

        Examples:
            shed_patch_bytes(zone="storage", path="data.bin", content="48454C4C4F")
            shed_patch_bytes(zone="storage", path="img.png", content="89504E47", overwrite=True)
        """
        try:
            return await self._core._patch_bytes_impl(
                zone=zone, path=path, content=content,
                content_format=content_format, position=position,
                offset=offset, length=length, overwrite=overwrite, safe=safe,
                group=group, message=message, mode=mode,
                allow_zone_in_path=allow_zone_in_path,
                __user__=__user__, __metadata__=__metadata__,
            )
        except StorageError as e:
            return self._core._format_error(e, "shed_patch_bytes")
        except Exception:
            return self._core._format_response(False, message="Unexpected error while editing binary file")

    async def shed_delete(
        self,
        zone: str,
        path: str,
        group: str = None,
        message: str = None,
        allow_zone_in_path: bool = False,
        __user__: dict = None,
        __metadata__: dict = None,
    ) -> str:
        """
        Delete a file or folder in the specified zone.

        :param zone: Target zone ("uploads", "storage", "documents", or "group")
        :param path: Path to delete (relative to zone, don't include zone name!)
        :param group: Group name/ID (required if zone="group")
        :param message: Git commit message (documents/group only)
        :param allow_zone_in_path: Allow path starting with zone name (default: False)
        :return: Deletion result as JSON

        Examples:
            shed_delete(zone="uploads", path="temp.txt")
            shed_delete(zone="storage", path="old_project/")
            shed_delete(zone="documents", path="draft.md", message="Remove draft")
            shed_delete(zone="group", group="team", path="obsolete.txt", message="Cleanup")

        Note: uploads allows delete to clean up imported files.
        """
        try:
            if __user__ is None:
                __user__ = {}
            # uploads allows delete even though readonly for other ops
            ctx = self._core._resolve_zone(zone, group, __user__, __metadata__, require_write=False)

            # Check for empty path first
            if not path or path.strip() == "":
                raise StorageError("MISSING_PARAMETER", "Path parameter is required")

            path = self._core._validate_relative_path(path, ctx.zone_name, allow_zone_in_path)
            target = self._core._resolve_chroot_path(ctx.zone_root, path)

            # Prevent deleting the zone root itself
            if target.resolve() == ctx.zone_root.resolve():
                raise StorageError("INVALID_PATH", "Cannot delete zone root", hint="Specify a file or folder within the zone")

            # Protect .git directory in versioned zones (documents, groups)
            if path == ".git" or path.startswith(".git/"):
                raise StorageError("PROTECTED_PATH", "Cannot delete .git directory", hint="The .git directory is required for version control")

            if not target.exists():
                raise StorageError("FILE_NOT_FOUND", f"Path not found: {path}")

            # Check if file is locked by another conversation
            # (skip for uploads which have no editzone_base, and for directories)
            if ctx.editzone_base and not target.is_dir():
                self._core._check_file_not_locked(ctx.editzone_base, path, ctx.conv_id)

            # Group: check delete permission
            user_id = __user__.get("id", "")
            if ctx.group_id:
                can_delete, reason = self._core._can_delete_group_file(ctx.group_id, path, user_id)
                if not can_delete:
                    raise StorageError("PERMISSION_DENIED", reason)
            
            # Delete
            was_dir = target.is_dir()
            if was_dir:
                shutil.rmtree(target)
                if ctx.group_id:
                    self._core._delete_file_ownership_recursive(ctx.group_id, path)
            else:
                target.unlink()
                if ctx.group_id:
                    self._core._delete_file_ownership(ctx.group_id, path)
            
            # Git commit if needed
            if ctx.git_commit:
                self._core._git_run(["add", "-A"], ctx.zone_root)
                commit_msg = message or f"Delete {path}"
                self._core._git_commit_as_user(ctx.zone_root, commit_msg, user_id)
            
            return self._core._format_response(True, data={
                "zone": ctx.zone_name,
                "deleted": path,
                "was_directory": was_dir,
            }, message=f"Deleted: {path}")
            
        except StorageError as e:
            return self._core._format_error(e, "shed_delete")
        except Exception:
            return self._core._format_response(False, message="Unexpected error while deleting file")

    async def shed_rename(
        self,
        zone: str,
        old_path: str,
        new_path: str,
        group: str = None,
        message: str = None,
        allow_zone_in_path: bool = False,
        __user__: dict = None,
        __metadata__: dict = None,
    ) -> str:
        """
        Rename or move a file/folder within the specified zone.

        :param zone: Target zone ("storage", "documents", or "group")
        :param old_path: Current path (relative to zone, don't include zone name!)
        :param new_path: New path (relative to zone, don't include zone name!)
        :param group: Group name/ID (required if zone="group")
        :param message: Git commit message (documents/group only)
        :param allow_zone_in_path: Allow paths starting with zone name (default: False)
        :return: Rename result as JSON

        Examples:
            shed_rename(zone="storage", old_path="draft.txt", new_path="final.txt")
            shed_rename(zone="documents", old_path="old/", new_path="archive/", message="Reorganize")
            shed_rename(zone="group", group="team", old_path="v1.doc", new_path="v2.doc")
        """
        try:
            if __user__ is None:
                __user__ = {}

            # Check for empty paths first
            if not old_path or old_path.strip() == "":
                raise StorageError("MISSING_PARAMETER", "old_path parameter is required")
            if not new_path or new_path.strip() == "":
                raise StorageError("MISSING_PARAMETER", "new_path parameter is required")

            ctx = self._core._resolve_zone(zone, group, __user__, __metadata__, require_write=True)

            old_path = self._core._validate_relative_path(old_path, ctx.zone_name, allow_zone_in_path)
            new_path = self._core._validate_relative_path(new_path, ctx.zone_name, allow_zone_in_path)

            old_target = self._core._resolve_chroot_path(ctx.zone_root, old_path)
            new_target = self._core._resolve_chroot_path(ctx.zone_root, new_path)

            if not old_target.exists():
                raise StorageError("FILE_NOT_FOUND", f"Source not found: {old_path}")

            # Check if file is locked by another conversation (skip for directories)
            if ctx.editzone_base and not old_target.is_dir():
                self._core._check_file_not_locked(ctx.editzone_base, old_path, ctx.conv_id)

            if new_target.exists():
                raise StorageError("FILE_EXISTS", f"Destination exists: {new_path}")
            
            # Group: check write permission
            user_id = __user__.get("id", "")
            if ctx.group_id:
                can_write, reason = self._core._can_write_group_file(ctx.group_id, old_path, user_id)
                if not can_write:
                    raise StorageError("PERMISSION_DENIED", reason)
            
            # Create parent directories
            new_target.parent.mkdir(parents=True, exist_ok=True)
            
            # Rename
            old_target.rename(new_target)
            
            # Update ownership records
            if ctx.group_id:
                self._core._update_file_ownership_paths(ctx.group_id, old_path, new_path)
            
            # Git commit
            if ctx.git_commit:
                self._core._git_run(["add", "-A"], ctx.zone_root)
                commit_msg = message or f"Rename {old_path} -> {new_path}"
                self._core._git_commit_as_user(ctx.zone_root, commit_msg, user_id)
            
            return self._core._format_response(True, data={
                "zone": ctx.zone_name,
                "old_path": old_path,
                "new_path": new_path,
            }, message=f"Renamed: {old_path} -> {new_path}")
            
        except StorageError as e:
            return self._core._format_error(e, "shed_rename")
        except Exception:
            return self._core._format_response(False, message="Unexpected error while renaming file")

    async def shed_lockedit_open(
        self,
        zone: str,
        path: str,
        group: str = None,
        allow_zone_in_path: bool = False,
        __user__: dict = None,
        __metadata__: dict = None,
    ) -> str:
        """
        Open a file for safe editing (locks file, creates working copy).

        ⚠️ COMPLETE WORKFLOW (must follow all steps):
        1. shed_lockedit_open(zone, path)         → Lock file, get content
        2. shed_lockedit_overwrite(zone, path, content)  → Modify (NOT shed_patch_text!)
        3. shed_lockedit_save(zone, path)         → Save + unlock (CLOSES edit mode!)

        OR to cancel: shed_lockedit_cancel(zone, path)  → Discard changes + unlock

        :param zone: Target zone ("storage", "documents", or "group")
        :param path: File path to edit (relative to zone, don't include zone name!)
        :param group: Group name/ID (required if zone="group")
        :param allow_zone_in_path: Allow path starting with zone name (default: False)
        :return: File content and lock info as JSON

        Examples:
            shed_lockedit_open(zone="storage", path="config.json")
            shed_lockedit_open(zone="documents", path="report.md")
            shed_lockedit_open(zone="group", group="team", path="shared.txt")
        """
        try:
            if __user__ is None:
                __user__ = {}

            # Validate path parameter
            if not path or not path.strip():
                raise StorageError(
                    "MISSING_PARAMETER",
                    "File path is required",
                    hint="Specify the file to edit: shed_lockedit_open(zone, path)"
                )

            ctx = self._core._resolve_zone(zone, group, __user__, __metadata__, require_write=True)

            path = self._core._validate_relative_path(path, ctx.zone_name, allow_zone_in_path)
            target = self._core._resolve_chroot_path(ctx.zone_root, path)
            
            if not target.exists():
                raise StorageError("FILE_NOT_FOUND", f"File not found: {path}")
            
            if target.is_dir():
                raise StorageError("NOT_A_FILE", f"Cannot edit a directory: {path}")
            
            # Group: check write permission
            user_id = __user__.get("id", "")
            if ctx.group_id:
                can_write, reason = self._core._can_write_group_file(ctx.group_id, path, user_id)
                if not can_write:
                    raise StorageError("PERMISSION_DENIED", reason)

            # Create lock
            lock_path = self._core._get_lock_path(ctx.editzone_base, path)
            self._core._acquire_lock(lock_path, ctx.conv_id, user_id, path)

            # All operations after lock acquisition must release lock on error
            try:
                # Copy to editzone
                editzone_path = self._core._get_editzone_path(ctx.editzone_base, ctx.conv_id, path)
                editzone_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(target, editzone_path)

                # Read content
                try:
                    with open(editzone_path, 'r', encoding='utf-8', errors='replace') as f:
                        content = f.read()
                    is_binary = False
                except (OSError, UnicodeDecodeError):
                    content = None
                    is_binary = True

                return self._core._format_response(True, data={
                    "zone": ctx.zone_name,
                    "path": path,
                    "content": content,
                    "is_binary": is_binary,
                    "size": target.stat().st_size,
                    "locked_by": user_id,
                }, message=f"File opened for editing: {path}")
            except Exception:
                # Clean up editzone and release lock on any failure after acquisition
                try:
                    if 'editzone_path' in dir() and editzone_path.exists():
                        editzone_path.unlink(missing_ok=True)
                except OSError:
                    pass
                self._core._release_lock(lock_path)
                raise

        except StorageError as e:
            return self._core._format_error(e, "shed_lockedit_open")
        except Exception:
            return self._core._format_response(False, message="Unexpected error while acquiring file lock")

    async def shed_lockedit_exec(
        self,
        zone: str,
        path: str,
        cmd: str,
        args: list = None,
        timeout: int = None,
        group: str = None,
        allow_zone_in_path: bool = False,
        __user__: dict = None,
        __metadata__: dict = None,
    ) -> str:
        """
        Execute a command on file in editzone (working copy).

        :param zone: Target zone ("storage", "documents", or "group")
        :param path: File path (must be opened with shed_lockedit_open, relative to zone)
        :param cmd: Command to execute
        :param args: Command arguments (use "." for the file being edited)
        :param timeout: Timeout in seconds
        :param group: Group name/ID (required if zone="group")
        :param allow_zone_in_path: Allow path starting with zone name (default: False)
        :return: Command output as JSON

        Examples:
            shed_lockedit_exec(zone="storage", path="data.txt", cmd="sed", args=["-i", "s/old/new/g", "."])
            shed_lockedit_exec(zone="storage", path="code.py", cmd="cat", args=["."])
        """
        try:
            if __user__ is None:
                __user__ = {}
            args = args or []  # Handle None default
            ctx = self._core._resolve_zone(zone, group, __user__, __metadata__, require_write=True)

            # Validate path parameter
            if not path or not path.strip():
                raise StorageError(
                    "MISSING_PARAMETER",
                    "File path is required",
                    hint="Specify the file: shed_lockedit_exec(zone, path, cmd)"
                )

            path = self._core._validate_relative_path(path, ctx.zone_name, allow_zone_in_path)
            user_id = __user__.get("id", "")

            # Verify lock ownership
            lock_path = self._core._get_lock_path(ctx.editzone_base, path)
            self._core._check_lock_owner(lock_path, user_id)

            # Get editzone path
            editzone_path = self._core._get_editzone_path(ctx.editzone_base, ctx.conv_id, path)
            
            if not editzone_path.exists():
                raise StorageError("NOT_IN_EDIT_MODE", f"File not open for editing: {path}",
                                   hint="Use shed_lockedit_open() first. Note: shed_lockedit_save() CLOSES edit mode!")
            
            # Validate command
            self._core._validate_command(cmd, ctx.whitelist, args)
            
            # Replace "." with actual filename
            processed_args = [editzone_path.name if a == "." else a for a in args]
            
            # Execute in editzone directory
            result = self._core._exec_command(
                cmd, processed_args,
                cwd=editzone_path.parent,
                timeout=self._core._clamp_timeout(timeout),
            )
            
            return self._core._format_response(True, data={
                "zone": ctx.zone_name,
                "path": path,
                "command": cmd,
                "stdout": result["stdout"],
                "stderr": result["stderr"],
                "returncode": result["returncode"],
            }, message="Command executed in editzone")
            
        except StorageError as e:
            return self._core._format_error(e, "shed_lockedit_exec")
        except Exception:
            return self._core._format_response(False, message="Unexpected error during locked file execution")

    async def shed_lockedit_overwrite(
        self,
        zone: str,
        path: str,
        content: str,
        append: bool = False,
        group: str = None,
        allow_zone_in_path: bool = False,
        __user__: dict = None,
        __metadata__: dict = None,
    ) -> str:
        """
        Write content to file in editzone (working copy).

        ⚠️ REQUIRES: File must be opened first with shed_lockedit_open()
        ⚠️ DO NOT use position, pattern, line, overwrite params - those are for shed_patch_text!

        :param zone: Target zone ("storage", "documents", or "group")
        :param path: File path (must be opened with shed_lockedit_open, relative to zone)
        :param content: Content to write (replaces entire file by default)
        :param append: If True, append instead of replace
        :param group: Group name/ID (required if zone="group")
        :param allow_zone_in_path: Allow path starting with zone name (default: False)
        :return: Write result as JSON

        Examples:
            shed_lockedit_overwrite(zone="storage", path="config.json", content='{"key": "value"}')
            shed_lockedit_overwrite(zone="storage", path="log.txt", content="New entry\\n", append=True)
        """
        try:
            if __user__ is None:
                __user__ = {}
            ctx = self._core._resolve_zone(zone, group, __user__, __metadata__, require_write=True)

            # Validate path parameter
            if not path or not path.strip():
                raise StorageError(
                    "MISSING_PARAMETER",
                    "File path is required",
                    hint="Specify the file: shed_lockedit_overwrite(zone, path, content)"
                )

            path = self._core._validate_relative_path(path, ctx.zone_name, allow_zone_in_path)
            user_id = __user__.get("id", "")

            # Verify lock ownership
            lock_path = self._core._get_lock_path(ctx.editzone_base, path)
            self._core._check_lock_owner(lock_path, user_id)

            # Get editzone path
            editzone_path = self._core._get_editzone_path(ctx.editzone_base, ctx.conv_id, path)
            
            if not editzone_path.exists():
                raise StorageError("NOT_IN_EDIT_MODE", f"File not open for editing: {path}",
                                   hint="Use shed_lockedit_open() first. Note: shed_lockedit_save() CLOSES edit mode!")

            # Validate content parameter
            if content is None:
                raise StorageError("MISSING_PARAMETER", "Content parameter is required")

            # Check content size
            self._core._validate_content_size(content)
            
            # Write
            mode = "a" if append else "w"
            with open(editzone_path, mode, encoding="utf-8") as f:
                f.write(content)
            
            new_size = editzone_path.stat().st_size
            
            return self._core._format_response(True, data={
                "zone": ctx.zone_name,
                "path": path,
                "bytes_written": len(content.encode('utf-8')),
                "new_size": new_size,
                "mode": "append" if append else "overwrite",
            }, message="Content written to editzone")
            
        except StorageError as e:
            return self._core._format_error(e, "shed_lockedit_overwrite")
        except Exception:
            return self._core._format_response(False, message="Unexpected error while overwriting locked file")

    async def shed_lockedit_save(
        self,
        zone: str,
        path: str,
        group: str = None,
        message: str = None,
        allow_zone_in_path: bool = False,
        __user__: dict = None,
        __metadata__: dict = None,
    ) -> str:
        """
        Save edited file back to zone and release lock.

        ⚠️ THIS CLOSES EDIT MODE! After save, the file is unlocked.
        To edit again, you must call shed_lockedit_open() first.

        Workflow: shed_lockedit_open → shed_lockedit_overwrite → shed_lockedit_save (done!)

        :param zone: Target zone ("storage", "documents", or "group")
        :param path: File path (relative to zone, don't include zone name!)
        :param group: Group name/ID (required if zone="group")
        :param message: Git commit message (documents/group only)
        :param allow_zone_in_path: Allow path starting with zone name (default: False)
        :return: Save result as JSON

        Examples:
            shed_lockedit_save(zone="storage", path="config.json")
            shed_lockedit_save(zone="documents", path="report.md", message="Final version")
        """
        try:
            if __user__ is None:
                __user__ = {}
            ctx = self._core._resolve_zone(zone, group, __user__, __metadata__, require_write=True)

            # Validate path parameter
            if not path or not path.strip():
                raise StorageError(
                    "MISSING_PARAMETER",
                    "File path is required",
                    hint="Specify the file to save: shed_lockedit_save(zone, path)"
                )

            path = self._core._validate_relative_path(path, ctx.zone_name, allow_zone_in_path)
            user_id = __user__.get("id", "")

            # Verify lock ownership
            lock_path = self._core._get_lock_path(ctx.editzone_base, path)
            self._core._check_lock_owner(lock_path, user_id)

            # Get paths
            editzone_path = self._core._get_editzone_path(ctx.editzone_base, ctx.conv_id, path)
            target = self._core._resolve_chroot_path(ctx.zone_root, path)
            
            if not editzone_path.exists():
                raise StorageError("NOT_IN_EDIT_MODE", f"File not open for editing: {path}",
                                   hint="Use shed_lockedit_open() first. Note: shed_lockedit_save() CLOSES edit mode!")
            
            # Check quota
            size_diff = editzone_path.stat().st_size - (target.stat().st_size if target.exists() else 0)
            if size_diff > 0:
                if ctx.group_id:
                    self._core._check_group_quota(ctx.group_id, size_diff)
                else:
                    self._core._check_quota(__user__, size_diff)
            
            # Copy back to zone - if this fails, keep lock for retry
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(editzone_path, target)

            # Save succeeded - ensure lock is released even if git/cleanup fails
            try:
                # Git commit if needed
                if ctx.git_commit:
                    self._core._git_run(["add", "-A"], ctx.zone_root)
                    commit_msg = message or f"Edit {path}"
                    self._core._git_commit_as_user(ctx.zone_root, commit_msg, user_id)

                # Cleanup editzone
                self._core._rm_with_empty_parents(editzone_path, ctx.editzone_base / "editzone")
            finally:
                # Always release lock after successful save
                self._core._release_lock(lock_path)

            return self._core._format_response(True, data={
                "zone": ctx.zone_name,
                "path": path,
                "size": target.stat().st_size,
                "committed": ctx.git_commit,
            }, message=f"Saved and unlocked: {path}")
            
        except StorageError as e:
            return self._core._format_error(e, "shed_lockedit_save")
        except Exception:
            return self._core._format_response(False, message="Unexpected error while saving locked file")

    async def shed_lockedit_cancel(
        self,
        zone: str,
        path: str,
        group: str = None,
        allow_zone_in_path: bool = False,
        __user__: dict = None,
        __metadata__: dict = None,
    ) -> str:
        """
        Cancel editing and release lock (discards changes).

        :param zone: Target zone ("storage", "documents", or "group")
        :param path: File path (relative to zone, don't include zone name!)
        :param group: Group name/ID (required if zone="group")
        :param allow_zone_in_path: Allow path starting with zone name (default: False)
        :return: Cancel result as JSON

        Examples:
            shed_lockedit_cancel(zone="storage", path="config.json")
        """
        try:
            if __user__ is None:
                __user__ = {}
            ctx = self._core._resolve_zone(zone, group, __user__, __metadata__, require_write=True)

            # Validate path parameter
            if not path or not path.strip():
                raise StorageError(
                    "MISSING_PARAMETER",
                    "File path is required",
                    hint="Specify the file to cancel: shed_lockedit_cancel(zone, path)"
                )

            path = self._core._validate_relative_path(path, ctx.zone_name, allow_zone_in_path)
            user_id = __user__.get("id", "")

            # Verify lock ownership
            lock_path = self._core._get_lock_path(ctx.editzone_base, path)
            self._core._check_lock_owner(lock_path, user_id)

            # Get editzone path
            editzone_path = self._core._get_editzone_path(ctx.editzone_base, ctx.conv_id, path)

            # Verify file is in edit mode (must have lock or editzone file)
            if not lock_path.exists() and not editzone_path.exists():
                raise StorageError("NOT_IN_EDIT_MODE", f"File not open for editing: {path}",
                                   hint="Use shed_lockedit_open() first")

            # Cleanup - ensure lock is always released even if cleanup fails
            try:
                if editzone_path.exists():
                    self._core._rm_with_empty_parents(editzone_path, ctx.editzone_base / "editzone")
            finally:
                self._core._release_lock(lock_path)

            return self._core._format_response(True, data={
                "zone": ctx.zone_name,
                "path": path,
                "changes_discarded": True,
            }, message=f"Edit cancelled, changes discarded: {path}")
            
        except StorageError as e:
            return self._core._format_error(e, "shed_lockedit_cancel")
        except Exception:
            return self._core._format_response(False, message="Unexpected error while canceling file lock")

    async def shed_move_uploads_to_storage(
        self,
        src: str,
        dest: str,
        overwrite: bool = False,
        allow_zone_in_path: bool = False,
        __user__: dict = None,
        __metadata__: dict = None,
    ) -> str:
        """
        Moves file from Uploads to Storage.
        IMPORTANT: Call shed_import() first to import uploaded files!

        :param src: Source path in Uploads (don't include zone name!)
        :param dest: Destination path in Storage (don't include zone name!)
        :param overwrite: If True, overwrite existing destination file (default: False)
        :param allow_zone_in_path: Allow paths starting with zone name (default: False)
        :return: Confirmation as JSON
        """
        try:
            # Validate required parameters
            if not src or not src.strip():
                raise StorageError(
                    "MISSING_PARAMETER",
                    "Source path is required",
                    hint="Specify the source file: shed_move_uploads_to_storage(src, dest)"
                )
            if not dest or not dest.strip():
                raise StorageError(
                    "MISSING_PARAMETER",
                    "Destination path is required",
                    hint="Specify the destination: shed_move_uploads_to_storage(src, dest)"
                )

            user_root = self._core._get_user_root(__user__)
            conv_id = self._core._get_conv_id(__metadata__)

            # Validate paths with zone name check
            src = self._core._validate_relative_path(src, "Uploads", allow_zone_in_path)
            dest = self._core._validate_relative_path(dest, "Storage", allow_zone_in_path)

            src_chroot = user_root / "Uploads" / conv_id
            dest_chroot = user_root / "Storage" / "data"

            source = self._core._resolve_chroot_path(src_chroot, src)
            target = self._core._resolve_chroot_path(dest_chroot, dest)
            
            if not source.exists():
                raise StorageError(
                    "FILE_NOT_FOUND",
                    f"File not found in Uploads: {src}",
                    {"path": src},
                    "Did you call shed_import() first? Files must be imported before moving."
                )

            if target.exists():
                if overwrite:
                    if target.is_dir():
                        shutil.rmtree(str(target))
                    else:
                        target.unlink()
                else:
                    raise StorageError(
                        "FILE_EXISTS",
                        f"Destination exists: {dest}",
                        hint="Use overwrite=True to replace the existing file"
                    )

            # No quota check needed: move within user space doesn't change total usage

            self._core._ensure_dir(dest_chroot)
            self._core._ensure_dir(target.parent)

            shutil.move(str(source), str(target))
            
            return self._core._format_response(True, message=f"Moved: Uploads/{src} -> Storage/{dest}")
            
        except StorageError as e:
            return self._core._format_error(e, "shed_move_uploads_to_storage")
        except Exception:
            return self._core._format_response(False, message="Unexpected error while moving file from Uploads to Storage")
    
    async def shed_move_uploads_to_documents(
        self,
        src: str,
        dest: str,
        message: str = None,
        overwrite: bool = False,
        allow_zone_in_path: bool = False,
        __user__: dict = None,
        __metadata__: dict = None,
    ) -> str:
        """
        Moves file from Uploads to Documents with Git commit.
        IMPORTANT: Call shed_import() first to import uploaded files!

        :param src: Source path in Uploads (don't include zone name!)
        :param dest: Destination path in Documents (don't include zone name!)
        :param message: Commit message
        :param overwrite: If True, overwrite existing destination file (default: False)
        :param allow_zone_in_path: Allow paths starting with zone name (default: False)
        :return: Confirmation as JSON
        """
        try:
            # Validate required parameters
            if not src or not src.strip():
                raise StorageError(
                    "MISSING_PARAMETER",
                    "Source path is required",
                    hint="Specify the source file: shed_move_uploads_to_documents(src, dest)"
                )
            if not dest or not dest.strip():
                raise StorageError(
                    "MISSING_PARAMETER",
                    "Destination path is required",
                    hint="Specify the destination: shed_move_uploads_to_documents(src, dest)"
                )

            user_root = self._core._get_user_root(__user__)
            conv_id = self._core._get_conv_id(__metadata__)

            # Validate paths with zone name check
            src = self._core._validate_relative_path(src, "Uploads", allow_zone_in_path)
            dest = self._core._validate_relative_path(dest, "Documents", allow_zone_in_path)

            src_chroot = user_root / "Uploads" / conv_id
            dest_chroot = user_root / "Documents" / "data"

            source = self._core._resolve_chroot_path(src_chroot, src)
            target = self._core._resolve_chroot_path(dest_chroot, dest)

            if not source.exists():
                raise StorageError(
                    "FILE_NOT_FOUND",
                    f"File not found in Uploads: {src}",
                    {"path": src},
                    "Did you call shed_import() first? Files must be imported before moving."
                )

            if target.exists():
                if overwrite:
                    if target.is_dir():
                        shutil.rmtree(str(target))
                    else:
                        target.unlink()
                else:
                    raise StorageError(
                        "FILE_EXISTS",
                        f"Destination exists: {dest}",
                        hint="Use overwrite=True to replace the existing file"
                    )

            # No quota check needed: move within user space doesn't change total usage

            # Init Git
            self._core._init_git_repo(dest_chroot)

            self._core._ensure_dir(target.parent)

            shutil.move(str(source), str(target))

            # Commit
            if not message:
                message = f"Import {src}"
            self._core._git_commit(dest_chroot, message)
            
            return self._core._format_response(True, message=f"Moved and committed: Uploads/{src} -> Documents/{dest}")
            
        except StorageError as e:
            return self._core._format_error(e, "shed_move_uploads_to_documents")
        except Exception:
            return self._core._format_response(False, message="Unexpected error while moving file from Uploads to Documents")
    
    async def shed_copy_storage_to_documents(
        self,
        src: str,
        dest: str,
        message: str = None,
        overwrite: bool = False,
        allow_zone_in_path: bool = False,
        __user__: dict = None,
        __metadata__: dict = None,
    ) -> str:
        """
        Copies from Storage to Documents with Git commit.

        :param src: Source path in Storage (don't include zone name!)
        :param dest: Destination path in Documents (don't include zone name!)
        :param message: Commit message
        :param overwrite: If True, overwrite existing destination file (default: False)
        :param allow_zone_in_path: Allow paths starting with zone name (default: False)
        :return: Confirmation as JSON
        """
        try:
            # Validate required parameters
            if not src or not src.strip():
                raise StorageError(
                    "MISSING_PARAMETER",
                    "Source path is required",
                    hint="Specify the source file: shed_copy_storage_to_documents(src, dest)"
                )
            if not dest or not dest.strip():
                raise StorageError(
                    "MISSING_PARAMETER",
                    "Destination path is required",
                    hint="Specify the destination: shed_copy_storage_to_documents(src, dest)"
                )

            user_root = self._core._get_user_root(__user__)

            # Validate paths with zone name check
            src = self._core._validate_relative_path(src, "Storage", allow_zone_in_path)
            dest = self._core._validate_relative_path(dest, "Documents", allow_zone_in_path)

            src_chroot = user_root / "Storage" / "data"
            dest_chroot = user_root / "Documents" / "data"

            source = self._core._resolve_chroot_path(src_chroot, src)
            target = self._core._resolve_chroot_path(dest_chroot, dest)

            if not source.exists():
                raise StorageError("FILE_NOT_FOUND", f"File not found: {src}")

            if target.exists():
                if overwrite:
                    if target.is_dir():
                        shutil.rmtree(str(target))
                    else:
                        target.unlink()
                else:
                    raise StorageError(
                        "FILE_EXISTS",
                        f"Destination exists: {dest}",
                        hint="Use overwrite=True to replace the existing file"
                    )

            # Check quota before copy
            self._core._check_quota(__user__, self._core._get_path_size(source))

            # Init Git
            self._core._init_git_repo(dest_chroot)

            self._core._ensure_dir(target.parent)

            if source.is_dir():
                shutil.copytree(source, target)
            else:
                shutil.copy2(source, target)

            # Commit
            if not message:
                message = f"Import from Storage: {src}"
            self._core._git_commit(dest_chroot, message)

            return self._core._format_response(True, message=f"Copied and committed: Storage/{src} -> Documents/{dest}")
            
        except StorageError as e:
            return self._core._format_error(e, "shed_copy_storage_to_documents")
        except Exception:
            return self._core._format_response(False, message="Unexpected error while copying file from Storage to Documents")
    
    async def shed_move_documents_to_storage(
        self,
        src: str,
        dest: str,
        message: str = None,
        overwrite: bool = False,
        allow_zone_in_path: bool = False,
        __user__: dict = None,
        __metadata__: dict = None,
    ) -> str:
        """
        Moves from Documents to Storage with git rm + commit.

        :param src: Source path in Documents (don't include zone name!)
        :param dest: Destination path in Storage (don't include zone name!)
        :param message: Commit message
        :param overwrite: If True, overwrite existing destination file (default: False)
        :param allow_zone_in_path: Allow paths starting with zone name (default: False)
        :return: Confirmation as JSON
        """
        try:
            # Validate required parameters
            if not src or not src.strip():
                raise StorageError(
                    "MISSING_PARAMETER",
                    "Source path is required",
                    hint="Specify the source file: shed_move_documents_to_storage(src, dest)"
                )
            if not dest or not dest.strip():
                raise StorageError(
                    "MISSING_PARAMETER",
                    "Destination path is required",
                    hint="Specify the destination: shed_move_documents_to_storage(src, dest)"
                )

            user_root = self._core._get_user_root(__user__)

            # Validate paths with zone name check
            src = self._core._validate_relative_path(src, "Documents", allow_zone_in_path)
            dest = self._core._validate_relative_path(dest, "Storage", allow_zone_in_path)

            src_chroot = user_root / "Documents" / "data"
            dest_chroot = user_root / "Storage" / "data"

            source = self._core._resolve_chroot_path(src_chroot, src)
            target = self._core._resolve_chroot_path(dest_chroot, dest)

            if not source.exists():
                raise StorageError("FILE_NOT_FOUND", f"File not found: {src}")

            if target.exists():
                if overwrite:
                    if target.is_dir():
                        shutil.rmtree(str(target))
                    else:
                        target.unlink()
                else:
                    raise StorageError(
                        "FILE_EXISTS",
                        f"Destination exists: {dest}",
                        hint="Use overwrite=True to replace the existing file"
                    )

            # Check quota (move requires temporary duplication)
            self._core._check_quota(__user__, self._core._get_path_size(source))

            self._core._ensure_dir(dest_chroot)
            self._core._ensure_dir(target.parent)

            # Copy to Storage
            if source.is_dir():
                shutil.copytree(source, target)
            else:
                shutil.copy2(source, target)

            # git rm in Documents via Layer 2
            self._core._git_run(["rm", "-rf", src], src_chroot)

            # Commit
            if not message:
                message = f"Move to Storage: {src}"
            self._core._git_commit(src_chroot, message)

            return self._core._format_response(True, message=f"Moved: Documents/{src} -> Storage/{dest}")
            
        except StorageError as e:
            return self._core._format_error(e, "shed_move_documents_to_storage")
        except Exception:
            return self._core._format_response(False, message="Unexpected error while moving file from Documents to Storage")
    
    # =========================================================================
    # UTILITIES (5 functions)
    # =========================================================================
    
    async def shed_import(
        self,
        filename: str = "",
        import_all: bool = False,
        dest_subdir: str = "",
        allow_zone_in_path: bool = False,
        __user__: dict = None,
        __metadata__: dict = None,
        __files__: list = None,
        __event_emitter__=None,
    ) -> str:
        """
        STEP 1: Imports files from chat to Uploads/.
        
        ALWAYS call this function first when user uploads a file!
        
        :param filename: Import only this specific file
        :param import_all: True to import ALL attached files
        :param dest_subdir: Optional subdirectory in Uploads/
        :return: List of imported files
        
        Examples:
          shed_import(import_all=True)           -> import all attached files
          shed_import(filename="report.pdf")     -> import only report.pdf
        """
        try:
            if __user__ is None:
                __user__ = {}
            if __metadata__ is None:
                __metadata__ = {}
            user_root = self._core._get_user_root(__user__)
            conv_id = self._core._get_conv_id(__metadata__)
            uploads_dir = user_root / "Uploads" / conv_id

            if dest_subdir:
                # Validate dest_subdir
                dest_subdir = self._core._validate_relative_path(dest_subdir, "Uploads", allow_zone_in_path)
                if dest_subdir:
                    uploads_dir = uploads_dir / dest_subdir
            
            self._core._ensure_dir(uploads_dir)
            
            # Get files (try multiple sources)
            files = __files__ or []
            
            if not files:
                files = __metadata__.get("files", [])
            
            if not files:
                return self._core._format_response(
                    False, 
                    message="No files attached to conversation"
                )
            
            imported = []
            errors = []
            
            # Possible paths for Open WebUI files
            owui_upload_paths = [
                Path("/app/backend/data/uploads"),
                Path("/app/backend/data/files"),
                Path("/app/backend/data/cache/files"),
                Path("/app/backend/data/cache/uploads"),
            ]
            
            for file_info in files:
                try:
                    file_path = None
                    file_name = None
                    file_id = None
                    user_id_from_file = None
                    
                    if isinstance(file_info, dict):
                        # Open WebUI structure detected
                        file_name = file_info.get("name") or file_info.get("filename")
                        file_id = file_info.get("id")
                        
                        # Search in nested "file" dict
                        nested_file = file_info.get("file")
                        if isinstance(nested_file, dict):
                            file_path = nested_file.get("path") or nested_file.get("file_path")
                            user_id_from_file = nested_file.get("user_id")
                            if not file_name:
                                file_name = nested_file.get("filename") or nested_file.get("name")
                            if not file_id:
                                file_id = nested_file.get("id")
                        
                        # Try direct keys if not found
                        if not file_path:
                            file_path = file_info.get("path") or file_info.get("file_path")
                        
                        # If no direct path, search file by ID
                        if not file_path and file_id:
                            # Search in different possible paths
                            for base_path in owui_upload_paths:
                                if not base_path.exists():
                                    continue
                                
                                # Format Open WebUI: {id}_{name}
                                if file_name:
                                    candidate = base_path / f"{file_id}_{file_name}"
                                    if candidate.exists():
                                        file_path = str(candidate)
                                        break
                                
                                # Try: /base/file_id
                                candidate = base_path / file_id
                                if candidate.exists():
                                    file_path = str(candidate)
                                    break

                                # Try: /base/user_id/file_id
                                if user_id_from_file:
                                    candidate = base_path / user_id_from_file / file_id
                                    if candidate.exists():
                                        file_path = str(candidate)
                                        break

                                # Search by pattern {id}_*
                                for f in base_path.glob(f"{file_id}_*"):
                                    file_path = str(f)
                                    if not file_name:
                                        file_name = f.name.split("_", 1)[1] if "_" in f.name else f.name
                                    break
                                if file_path:
                                    break
                    
                    elif isinstance(file_info, str):
                        file_path = file_info
                        file_name = Path(file_info).name
                    
                    if not file_name:
                        # Generate unique name to prevent collisions
                        file_name = file_id or f"unknown_{uuid.uuid4().hex[:8]}"

                    # Security: clean filename (prevent traversal)
                    file_name = Path(file_name).name  # Keep only the name, not the path
                    if not file_name or file_name in (".", ".."):
                        # Generate unique name to prevent collisions
                        file_name = file_id or f"unknown_{uuid.uuid4().hex[:8]}"
                    
                    # Filter if filename specified
                    if filename and file_name != filename:
                        continue
                    
                    if not import_all and not filename:
                        continue
                    
                    # Copy the file
                    if file_path and isinstance(file_path, str):
                        source = Path(file_path)
                        if source.exists():
                            # Security: reject symlinks
                            if source.is_symlink():
                                errors.append(f"{file_name}: symlinks not allowed")
                                continue
                            
                            # Security: only regular files
                            if not source.is_file():
                                errors.append(f"{file_name}: not a regular file")
                                continue
                            
                            # Check file size
                            file_size = source.stat().st_size
                            max_size = self.valves.max_file_size_mb * 1024 * 1024
                            if file_size > max_size:
                                errors.append(f"{file_name}: too large ({file_size / 1024 / 1024:.1f} MB > {self.valves.max_file_size_mb} MB)")
                                continue
                            
                            # Check quota
                            try:
                                self._core._check_quota(__user__, file_size)
                            except StorageError as quota_error:
                                errors.append(f"{file_name}: {quota_error.message}")
                                continue
                            
                            dest = uploads_dir / file_name
                            shutil.copy2(source, dest)
                            imported.append(file_name)
                        else:
                            errors.append(f"{file_name}: file not found")
                    else:
                        errors.append(f"{file_name}: source file not found")
                
                except Exception:
                    errors.append("An error occurred during import")
            
            if not imported:
                return self._core._format_response(
                    False, 
                    message="No matching files found",
                    data={"errors": errors} if errors else None
                )
            
            result_data = {"imported": imported, "count": len(imported)}
            if errors:
                result_data["errors"] = errors

            return self._core._format_response(
                True,
                data=result_data,
                message=f"Imported {len(imported)} file(s) to Uploads. Use shed_delete(zone='uploads', path='...') to remove."
            )

        except Exception:
            return self._core._format_response(False, message="Unexpected error during file import")
    
    # =========================================================================
    # BUILTIN ZIP/UNZIP (Python zipfile - no external dependency)
    # =========================================================================
    
    async def shed_unzip(
        self,
        zone: str,
        src: str,
        dest: str = "",
        src_zone: str = "",
        allow_zone_in_path: bool = False,
        __user__: dict = None,
        __metadata__: dict = None,
    ) -> str:
        """
        Extracts a ZIP archive using Python zipfile (builtin, no external dependency).
        Works in Storage or Documents zones.

        :param zone: Destination zone for extraction (Storage or Documents)
        :param src: Path to ZIP file (relative to src_zone, or zone if src_zone is empty)
        :param dest: Destination folder (relative to zone). Empty = same folder as ZIP
        :param src_zone: Source zone where ZIP is located (Uploads, Storage, or Documents). Empty = same as zone
        :return: List of extracted files as JSON

        Example:
            shed_unzip(zone="storage", src="downloads/repo.zip", dest="projects/repo")
            shed_unzip(zone="storage", src="archive.zip", dest="extracted", src_zone="uploads")
        """
        # Canonical zone names (with capital)
        ZONE_NAMES = {"uploads": "Uploads", "storage": "Storage", "documents": "Documents"}

        try:
            user_root = self._core._get_user_root(__user__)
            zone_lower = zone.lower()

            # Validate destination zone (must be writable)
            if zone_lower not in ("storage", "documents"):
                raise StorageError(
                    "ZONE_FORBIDDEN",
                    f"Zone '{zone}' not allowed for unzip destination",
                    {"zone": zone},
                    "Use Storage or Documents"
                )
            zone_name = ZONE_NAMES[zone_lower]

            # Get destination zone path
            if zone_lower == "storage":
                zone_root = user_root / "Storage" / "data"
            else:
                zone_root = user_root / "Documents" / "data"

            # Determine source zone (defaults to destination zone if not specified)
            src_zone_lower = src_zone.lower() if src_zone else zone_lower

            # Validate source zone
            if src_zone_lower not in ("uploads", "storage", "documents"):
                raise StorageError(
                    "ZONE_FORBIDDEN",
                    f"Source zone '{src_zone}' not allowed",
                    {"src_zone": src_zone},
                    "Use Uploads, Storage, or Documents"
                )
            src_zone_name = ZONE_NAMES[src_zone_lower]

            # Get source zone path
            if src_zone_lower == "uploads":
                conv_id = self._core._get_conv_id(__metadata__)
                src_zone_root = user_root / "Uploads" / conv_id
            elif src_zone_lower == "storage":
                src_zone_root = user_root / "Storage" / "data"
            else:
                src_zone_root = user_root / "Documents" / "data"

            # Validate source is not empty
            if not src or not src.strip():
                raise StorageError(
                    "MISSING_PARAMETER",
                    "Source path is required",
                    hint="Specify the ZIP file to extract: shed_unzip(zone, src, dest)"
                )

            # Validate and resolve paths
            src = self._core._validate_relative_path(src, src_zone_name, allow_zone_in_path)
            src_path = self._core._resolve_chroot_path(src_zone_root, src)

            if not src_path.exists():
                raise StorageError("FILE_NOT_FOUND", f"ZIP file not found: {src}")
            
            if not src_path.suffix.lower() == ".zip":
                raise StorageError(
                    "INVALID_FORMAT",
                    "File is not a ZIP archive",
                    {"file": src},
                    "Only .zip files are supported"
                )

            # Verify ZIP magic bytes (not just extension)
            with open(src_path, 'rb') as f:
                header = f.read(4)
            if not any(header.startswith(magic) for magic in ZIP_MAGIC_BYTES):
                raise StorageError(
                    "INVALID_FORMAT",
                    "File has .zip extension but is not a valid ZIP archive",
                    {"file": src},
                    "The file header does not match ZIP format"
                )

            # Determine destination
            if dest:
                dest = self._core._validate_relative_path(dest, zone_name, allow_zone_in_path)
                dest_path = self._core._resolve_chroot_path(zone_root, dest)
            else:
                # When dest is empty, extract to same relative location in destination zone
                # (not src_path.parent which would be in the source zone for cross-zone ops)
                src_relative = str(src_path.parent.relative_to(src_zone_root))
                # Validate and resolve the path to prevent any escape
                src_relative = self._core._validate_relative_path(src_relative, zone_name, allow_zone_in_path=True)
                dest_path = self._core._resolve_chroot_path(zone_root, src_relative)
            
            # Check quota before extraction (estimate: 3x zip size)
            zip_size = src_path.stat().st_size
            self._core._check_quota(__user__, zip_size * 3)
            
            # Extract
            self._core._ensure_dir(dest_path)
            extracted_files = []
            
            with zipfile.ZipFile(src_path, 'r') as zf:
                # Security: check for path traversal in zip entries (ZIP Slip prevention)
                dest_resolved = dest_path.resolve()
                for member in zf.namelist():
                    # Block absolute paths
                    if member.startswith('/'):
                        raise StorageError(
                            "PATH_ESCAPE",
                            f"ZIP contains absolute path: {member}",
                            {"member": member},
                            "ZIP file may be malicious (path traversal attempt)"
                        )

                    # Resolve the target path and verify it stays within dest
                    # This catches cases like "foo/../../../etc/passwd"
                    member_path = (dest_path / member).resolve()
                    try:
                        member_path.relative_to(dest_resolved)
                    except ValueError:
                        raise StorageError(
                            "PATH_ESCAPE",
                            f"ZIP contains path traversal: {member}",
                            {"member": member, "resolved": str(member_path)},
                            "ZIP file may be malicious (escapes destination directory)"
                        )

                # ZIP bomb protection: check decompressed size and file count
                infolist = zf.infolist()
                total_size = sum(info.file_size for info in infolist)
                file_count = len(infolist)

                if file_count > ZIP_MAX_FILES:
                    raise StorageError(
                        "ZIP_BOMB",
                        f"ZIP contains too many files ({file_count})",
                        {"file_count": file_count, "max": ZIP_MAX_FILES},
                        "ZIP file may be a decompression bomb"
                    )

                if total_size > ZIP_MAX_DECOMPRESSED_SIZE:
                    raise StorageError(
                        "ZIP_BOMB",
                        f"ZIP decompressed size too large ({total_size // BYTES_PER_MB} MB)",
                        {"decompressed_size": total_size, "max": ZIP_MAX_DECOMPRESSED_SIZE},
                        "ZIP file may be a decompression bomb"
                    )

                if zip_size > 0 and total_size / zip_size > ZIP_MAX_COMPRESSION_RATIO:
                    raise StorageError(
                        "ZIP_BOMB",
                        f"ZIP compression ratio too high ({total_size // zip_size}:1)",
                        {"ratio": total_size / zip_size, "max_ratio": ZIP_MAX_COMPRESSION_RATIO},
                        "ZIP file may be a decompression bomb"
                    )

                # Final symlink check before extraction (TOCTOU protection)
                if dest_path.is_symlink():
                    raise StorageError(
                        "PATH_ESCAPE",
                        "Destination is a symlink",
                        {"dest": str(dest_path)},
                        "Cannot extract to a symlink target"
                    )

                # Extract all files (safe after validation)
                members = zf.namelist()
                try:
                    zf.extractall(dest_path)
                    extracted_files = members
                except Exception:
                    # Clean up any partially extracted files and directories on error
                    # First remove files, then directories (in reverse order for nested dirs)
                    # Remove files first
                    for member in members:
                        member_path = dest_path / member
                        try:
                            if member_path.is_file():
                                member_path.unlink()
                        except OSError:
                            pass
                    # Remove empty directories (reverse sorted for nested cleanup)
                    for member in sorted(members, reverse=True):
                        member_path = dest_path / member
                        try:
                            if member_path.is_dir() and not any(member_path.iterdir()):
                                member_path.rmdir()
                        except OSError:
                            pass
                    raise
            
            # Git commit if Documents
            if zone_lower == "documents":
                docs_data = user_root / "Documents" / "data"
                self._core._git_run(["add", "-A"], cwd=docs_data)
                src_info = f"{src_zone_name}:{src}" if src_zone_lower != zone_lower else src
                self._core._git_run(
                    ["commit", "-m", f"Extracted {src_info} to {dest or 'same folder'}", "--allow-empty"],
                    cwd=docs_data
                )

            return self._core._format_response(
                True,
                data={
                    "source": src,
                    "source_zone": src_zone_name,
                    "destination": str(dest_path.relative_to(zone_root)),
                    "destination_zone": zone_name,
                    "files_count": len(extracted_files),
                    "files": extracted_files[:50],  # Limit to first 50
                    "truncated": len(extracted_files) > 50,
                },
                message=f"Extracted {len(extracted_files)} files from {src_zone_name} to {zone_name}"
            )
            
        except StorageError as e:
            return self._core._format_error(e, "shed_unzip")
        except zipfile.BadZipFile:
            return self._core._format_response(False, message="Invalid or corrupted ZIP file")
        except Exception:
            return self._core._format_response(False, message="Unexpected error during ZIP extraction")
    
    async def shed_zip(
        self,
        zone: str,
        src: str,
        dest: str = "",
        include_empty_dirs: bool = False,
        allow_zone_in_path: bool = False,
        __user__: dict = None,
        __metadata__: dict = None,
    ) -> str:
        """
        Creates a ZIP archive using Python zipfile (builtin, no external dependency).
        Works in Storage or Documents zones.
        
        :param zone: Source zone ("storage" or "documents")
        :param src: File or folder to compress (relative to zone)
        :param dest: Destination ZIP path (relative to zone). Empty = src + ".zip"
        :param include_empty_dirs: Include empty directories in archive (default: False, like standard zip)
        :return: Path to created ZIP as JSON
        
        Example:
            shed_zip(zone="storage", src="projects/myapp", dest="archives/myapp.zip")
            shed_zip(zone="storage", src="projects", dest="backup.zip", include_empty_dirs=True)
        """
        try:
            user_root = self._core._get_user_root(__user__)
            zone_lower = zone.lower()
            
            # Validate zone
            if zone_lower not in ("storage", "documents"):
                raise StorageError(
                    "ZONE_FORBIDDEN",
                    f"Zone '{zone}' not allowed for zip",
                    {"zone": zone},
                    "Use 'storage' or 'documents'"
                )
            
            # Get zone path
            if zone_lower == "storage":
                zone_root = user_root / "Storage" / "data"
                zone_name = "Storage"
            else:
                zone_root = user_root / "Documents" / "data"
                zone_name = "Documents"

            # Validate source is not empty
            if not src or not src.strip():
                raise StorageError(
                    "MISSING_PARAMETER",
                    "Source path is required",
                    hint="Specify the file or folder to compress: shed_zip(zone, src, dest)"
                )

            # Validate and resolve source path
            src = self._core._validate_relative_path(src, zone_name, allow_zone_in_path)
            src_path = self._core._resolve_chroot_path(zone_root, src)

            if not src_path.exists():
                raise StorageError("FILE_NOT_FOUND", f"Source not found: {src}")

            # Determine destination
            if dest:
                dest = self._core._validate_relative_path(dest, zone_name, allow_zone_in_path)
                if not dest.endswith('.zip'):
                    dest += '.zip'
                dest_path = self._core._resolve_chroot_path(zone_root, dest)
            else:
                dest_path = src_path.parent / (src_path.name + ".zip")

            # Check if destination exists
            if dest_path.exists():
                raise StorageError("FILE_EXISTS", f"Destination exists: {dest or dest_path.name}")

            # Check quota (estimate: same size as source)
            src_size = self._core._get_path_size(src_path)
            self._core._check_quota(__user__, src_size)
            
            # Create ZIP
            self._core._ensure_dir(dest_path.parent)
            files_added = 0
            dirs_added = 0
            
            with zipfile.ZipFile(dest_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                if src_path.is_file():
                    zf.write(src_path, src_path.name)
                    files_added = 1
                else:
                    # Add directory recursively
                    for item_path in src_path.rglob('*'):
                        arcname = item_path.relative_to(src_path.parent)
                        if item_path.is_file():
                            zf.write(item_path, arcname)
                            files_added += 1
                        elif item_path.is_dir() and include_empty_dirs:
                            # Check if directory is empty (no files, only subdirs or nothing)
                            has_files = any(p.is_file() for p in item_path.rglob('*'))
                            if not has_files:
                                # Add empty directory entry (path must end with /)
                                zf.writestr(str(arcname) + '/', '')
                                dirs_added += 1
            
            # Git commit if Documents
            if zone_lower == "documents":
                docs_data = user_root / "Documents" / "data"
                self._core._git_run(["add", "-A"], cwd=docs_data)
                self._core._git_run(
                    ["commit", "-m", f"Created ZIP: {dest_path.name}", "--allow-empty"],
                    cwd=docs_data
                )
            
            zip_size = dest_path.stat().st_size
            
            response_data = {
                "source": src,
                "zip_path": str(dest_path.relative_to(zone_root)),
                "files_count": files_added,
                "size_bytes": zip_size,
                "size_human": f"{zip_size / 1024 / 1024:.2f} MB" if zip_size > 1024*1024 else f"{zip_size / 1024:.1f} KB",
            }
            
            if dirs_added > 0:
                response_data["empty_dirs_count"] = dirs_added
            
            message = f"Created ZIP with {files_added} files"
            if dirs_added > 0:
                message += f" and {dirs_added} empty directories"
            
            return self._core._format_response(True, data=response_data, message=message)
            
        except StorageError as e:
            return self._core._format_error(e, "shed_zip")
        except Exception:
            return self._core._format_response(False, message="Unexpected error during ZIP creation")

    # =========================================================================
    # BUILTIN UTILITIES - Replace missing system commands (5 functions)
    # =========================================================================
    
    async def shed_tree(
        self,
        zone: str,
        path: str = ".",
        depth: int = 3,
        group: str = None,
        allow_zone_in_path: bool = False,
        __user__: dict = None,
        __metadata__: dict = None,
    ) -> str:
        """
        Displays directory tree structure (replaces missing 'tree' command).
        
        :param zone: Target zone ("uploads", "storage", "documents", or "group")
        :param path: Starting path (default: root of zone)
        :param depth: Maximum depth to display (default: 3, max: 10)
        :param group: Group name (required if zone="group")
        :return: Tree structure as text
        
        Example:
            shed_tree(zone="storage", path="projects", depth=2)
            shed_tree(zone="group", group="MyTeam", path="docs")
        """
        try:
            # Resolve zone using standard helper
            ctx = self._core._resolve_zone(zone, group, __user__, __metadata__, require_write=False)
            zone_root = ctx.zone_root
            zone_name = ctx.zone_name

            if not zone_root.exists():
                return self._core._format_response(True, data={"tree": "(empty)"}, message="Zone is empty")

            # Validate and resolve path
            path = self._core._validate_relative_path(path, zone_name, allow_zone_in_path) if path and path != "." else ""
            start_path = self._core._resolve_chroot_path(zone_root, path) if path else zone_root
            
            if not start_path.exists():
                raise StorageError("FILE_NOT_FOUND", f"Path not found: {path}")

            # Validate and clamp depth
            if depth < 0:
                raise StorageError(
                    "INVALID_PARAMETER",
                    "Depth must be non-negative",
                    {"depth": depth},
                    "Use depth between 0 and 10"
                )
            depth = max(1, min(depth, 10))
            
            # Build tree
            def build_tree(current: Path, prefix: str = "", current_depth: int = 0) -> list:
                if current_depth >= depth:
                    return []
                
                lines = []
                try:
                    items = sorted(current.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
                except PermissionError:
                    return [f"{prefix}[permission denied]"]
                
                # Filter out hidden files and limit items
                items = [i for i in items if not i.name.startswith('.')]
                total = len(items)
                items_limited = items[:100]  # Limit to 100 items per dir
                items_limited_count = len(items_limited)

                for idx, item in enumerate(items_limited):
                    is_last = (idx == items_limited_count - 1) or (idx == 99 and total > 100)
                    connector = "└── " if is_last else "├── "
                    
                    if item.is_dir():
                        lines.append(f"{prefix}{connector}{item.name}/")
                        if current_depth + 1 < depth:
                            extension = "    " if is_last else "│   "
                            lines.extend(build_tree(item, prefix + extension, current_depth + 1))
                    else:
                        try:
                            size = item.stat().st_size
                            size_str = self._core._format_size(size, short=True)
                        except (OSError, FileNotFoundError):
                            size_str = "?"
                        lines.append(f"{prefix}{connector}{item.name} ({size_str})")
                
                if total > 100:
                    lines.append(f"{prefix}... and {total - 100} more items")
                
                return lines
            
            # Generate tree
            root_name = start_path.name if path else (group if ctx.zone_lower == "group" else ctx.zone_lower.capitalize())
            tree_lines = [f"{root_name}/"]
            tree_lines.extend(build_tree(start_path))
            tree_output = "\n".join(tree_lines)

            zone_display = zone_name
            return self._core._format_response(
                True,
                data={"tree": tree_output, "depth": depth, "path": path or ".", "zone": zone_display},
                message=f"Tree of {zone_display}/{path or '.'} (depth={depth})"
            )
            
        except StorageError as e:
            return self._core._format_error(e, "shed_tree")
        except Exception:
            return self._core._format_response(False, message="Unexpected error while building directory tree")
    
    async def shed_zipinfo(
        self,
        zone: str,
        path: str,
        group: str = None,
        allow_zone_in_path: bool = False,
        __user__: dict = None,
        __metadata__: dict = None,
    ) -> str:
        """
        Shows ZIP archive contents and metadata (replaces missing 'zipinfo' command).

        :param zone: Target zone ("uploads", "storage", "documents", or "group")
        :param path: Path to ZIP file
        :param group: Group name (required if zone="group")
        :return: ZIP contents and metadata as JSON

        Example:
            shed_zipinfo(zone="storage", path="backup.zip")
            shed_zipinfo(zone="group", group="MyTeam", path="archive.zip")
        """
        try:
            # Resolve zone using standard helper
            ctx = self._core._resolve_zone(zone, group, __user__, __metadata__, require_write=False)
            zone_root = ctx.zone_root
            zone_name = ctx.zone_name

            # Validate path is not empty
            if not path or not path.strip():
                raise StorageError(
                    "MISSING_PARAMETER",
                    "Path is required",
                    hint="Specify the ZIP file: shed_zipinfo(zone, path)"
                )

            # Validate and resolve path
            path = self._core._validate_relative_path(path, zone_name, allow_zone_in_path)
            zip_path = self._core._resolve_chroot_path(zone_root, path)
            
            if not zip_path.exists():
                raise StorageError("FILE_NOT_FOUND", f"File not found: {path}")
            
            if not zip_path.suffix.lower() == ".zip":
                raise StorageError(
                    "INVALID_FORMAT",
                    "File is not a ZIP archive",
                    hint="Only .zip files are supported"
                )

            # Verify ZIP magic bytes (not just extension)
            with open(zip_path, 'rb') as f:
                header = f.read(4)
            if not any(header.startswith(magic) for magic in ZIP_MAGIC_BYTES):
                raise StorageError(
                    "INVALID_FORMAT",
                    "File has .zip extension but is not a valid ZIP archive",
                    {"file": path},
                    "The file header does not match ZIP format"
                )

            # Read ZIP info
            with zipfile.ZipFile(zip_path, 'r') as zf:
                files = []
                total_size = 0
                total_compressed = 0
                
                for info in zf.infolist():
                    total_size += info.file_size
                    total_compressed += info.compress_size
                    
                    files.append({
                        "name": info.filename,
                        "size": info.file_size,
                        "compressed": info.compress_size,
                        "ratio": f"{(1 - info.compress_size / info.file_size) * 100:.1f}%" if info.file_size > 0 else "0%",
                        "date": f"{info.date_time[0]:04d}-{info.date_time[1]:02d}-{info.date_time[2]:02d} {info.date_time[3]:02d}:{info.date_time[4]:02d}",
                        "is_dir": info.filename.endswith('/'),
                    })
                
                # Summary
                ratio = (1 - total_compressed / total_size) * 100 if total_size > 0 else 0
                
                return self._core._format_response(
                    True,
                    data={
                        "path": path,
                        "files_count": len(files),
                        "total_size": total_size,
                        "total_size_human": self._core._format_size(total_size),
                        "compressed_size": total_compressed,
                        "compression_ratio": f"{ratio:.1f}%",
                        "files": files[:100],  # Limit to 100
                        "truncated": len(files) > 100,
                    },
                    message=f"ZIP contains {len(files)} files ({ratio:.1f}% compression)"
                )
            
        except StorageError as e:
            return self._core._format_error(e, "shed_zipinfo")
        except zipfile.BadZipFile:
            return self._core._format_response(False, message="Invalid or corrupted ZIP file")
        except Exception:
            return self._core._format_response(False, message="Unexpected error while reading ZIP info")
    
    async def shed_file_type(
        self,
        zone: str,
        path: str,
        group: str = None,
        allow_zone_in_path: bool = False,
        __user__: dict = None,
        __metadata__: dict = None,
    ) -> str:
        """
        Identifies file MIME type (replaces missing 'file' command).

        :param zone: Target zone ("uploads", "storage", "documents", or "group")
        :param path: Path to file
        :param group: Group name (required if zone="group")
        :return: File type information as JSON

        Example:
            shed_file_type(zone="storage", path="document.pdf")
            shed_file_type(zone="group", group="MyTeam", path="data.csv")
        """
        try:
            # Resolve zone using standard helper
            ctx = self._core._resolve_zone(zone, group, __user__, __metadata__, require_write=False)
            zone_root = ctx.zone_root
            zone_name = ctx.zone_name

            # Validate and resolve path
            path = self._core._validate_relative_path(path, zone_name, allow_zone_in_path)
            file_path = self._core._resolve_chroot_path(zone_root, path)

            if not file_path.exists():
                raise StorageError("FILE_NOT_FOUND", f"File not found: {path}")

            if file_path.is_dir():
                return self._core._format_response(
                    True,
                    data={"path": path, "type": "directory", "mime": "inode/directory"},
                    message="Directory"
                )
            
            # Get MIME type from extension
            mime_type, encoding = mimetypes.guess_type(str(file_path))
            
            # Read magic bytes for common formats
            magic_info = None
            try:
                with open(file_path, 'rb') as f:
                    header = f.read(16)
                    
                    # Common magic bytes
                    magic_signatures = {
                        b'\x89PNG\r\n\x1a\n': 'PNG image',
                        b'\xff\xd8\xff': 'JPEG image',
                        b'GIF87a': 'GIF image (87a)',
                        b'GIF89a': 'GIF image (89a)',
                        b'PK\x03\x04': 'ZIP archive (or DOCX/XLSX/PPTX/JAR)',
                        b'PK\x05\x06': 'ZIP archive (empty)',
                        b'%PDF': 'PDF document',
                        b'\x7fELF': 'ELF executable',
                        b'#!': 'Script (shebang)',
                        b'\x1f\x8b': 'Gzip compressed',
                        b'BZ': 'Bzip2 compressed',
                        b'\xfd7zXZ': 'XZ compressed',
                        b'Rar!': 'RAR archive',
                        b'7z\xbc\xaf': '7-Zip archive',
                        b'\x00\x00\x00\x1c\x66\x74\x79\x70': 'MP4/MOV video',
                        b'\x00\x00\x00\x20\x66\x74\x79\x70': 'MP4 video',
                        b'ID3': 'MP3 audio (ID3)',
                        b'\xff\xfb': 'MP3 audio',
                        b'OggS': 'Ogg container',
                        b'RIFF': 'RIFF container (WAV/AVI)',
                        b'SQLite format 3': 'SQLite database',
                    }
                    
                    for sig, desc in magic_signatures.items():
                        if header.startswith(sig):
                            magic_info = desc
                            break
                    
                    # Check for text
                    if not magic_info:
                        try:
                            # Try to decode as UTF-8
                            with open(file_path, 'r', encoding='utf-8') as tf:
                                tf.read(1024)
                            magic_info = "Text file (UTF-8)"
                        except UnicodeDecodeError:
                            magic_info = "Binary file"
            except Exception:
                pass
            
            # Get file stats
            stat = file_path.stat()
            
            return self._core._format_response(
                True,
                data={
                    "path": path,
                    "mime": mime_type or "application/octet-stream",
                    "encoding": encoding,
                    "magic": magic_info,
                    "extension": file_path.suffix,
                    "size": stat.st_size,
                    "size_human": f"{stat.st_size / 1024 / 1024:.2f} MB" if stat.st_size > 1024*1024 else f"{stat.st_size / 1024:.1f} KB" if stat.st_size > 1024 else f"{stat.st_size} B",
                },
                message=f"{magic_info or mime_type or 'Unknown type'}"
            )
            
        except StorageError as e:
            return self._core._format_error(e, "shed_file_type")
        except Exception:
            return self._core._format_response(False, message="Unexpected error while detecting file type")
    
    async def shed_convert_eol(
        self,
        zone: str,
        path: str,
        to: str = "unix",
        group: str = None,
        allow_zone_in_path: bool = False,
        __user__: dict = None,
        __metadata__: dict = None,
    ) -> str:
        """
        Converts line endings (replaces missing 'dos2unix'/'unix2dos' commands).

        :param zone: Target zone ("storage", "documents", or "group")
        :param path: Path to text file
        :param to: Target format: "unix" (LF) or "dos" (CRLF)
        :param group: Group name (required if zone="group")
        :return: Conversion result as JSON

        Example:
            shed_convert_eol(zone="storage", path="script.sh", to="unix")
            shed_convert_eol(zone="group", group="MyTeam", path="readme.txt", to="dos")
        """
        try:
            # Resolve zone using standard helper (require_write=True rejects uploads)
            ctx = self._core._resolve_zone(zone, group, __user__, __metadata__, require_write=True)
            zone_root = ctx.zone_root
            zone_name = ctx.zone_name

            # LLM Guardrail: validate type before use
            if not isinstance(to, str):
                raise StorageError(
                    "INVALID_PARAMETER",
                    f"to must be a string ('unix' or 'dos'), got: {repr(to)} ({type(to).__name__})",
                    hint="Use to='unix' for LF line endings or to='dos' for CRLF (Windows)"
                )

            # Validate target format
            to_lower = to.lower()
            if to_lower not in ("unix", "dos", "lf", "crlf"):
                raise StorageError(
                    "INVALID_MODE",
                    f"Invalid EOL format: {to}",
                    hint="Use 'unix' (LF) or 'dos' (CRLF)"
                )

            # Normalize format name
            to_unix = to_lower in ("unix", "lf")

            # Validate and resolve path
            path = self._core._validate_relative_path(path, zone_name, allow_zone_in_path)
            file_path = self._core._resolve_chroot_path(zone_root, path)
            
            if not file_path.exists():
                raise StorageError("FILE_NOT_FOUND", f"File not found: {path}")
            
            if file_path.is_dir():
                raise StorageError("INVALID_FORMAT", "Cannot convert directory")
            
            # Read file
            try:
                content = file_path.read_bytes()
            except Exception:
                raise StorageError("EXEC_ERROR", "Cannot read file")
            
            # Count existing line endings
            crlf_count = content.count(b'\r\n')
            lf_only_count = content.count(b'\n') - crlf_count
            cr_only_count = content.count(b'\r') - crlf_count
            
            original_format = "mixed"
            if crlf_count > 0 and lf_only_count == 0:
                original_format = "dos"
            elif lf_only_count > 0 and crlf_count == 0:
                original_format = "unix"
            elif cr_only_count > 0 and crlf_count == 0 and lf_only_count == 0:
                original_format = "mac (old)"
            
            # Convert
            if to_unix:
                # To Unix: CRLF -> LF, CR -> LF
                new_content = content.replace(b'\r\n', b'\n').replace(b'\r', b'\n')
                target_format = "unix"
            else:
                # To DOS: First normalize to LF, then convert to CRLF
                normalized = content.replace(b'\r\n', b'\n').replace(b'\r', b'\n')
                new_content = normalized.replace(b'\n', b'\r\n')
                target_format = "dos"
            
            # Check if changed
            if new_content == content:
                return self._core._format_response(
                    True,
                    data={"path": path, "format": original_format, "changed": False},
                    message=f"File already in {target_format} format"
                )
            
            # Write back
            file_path.write_bytes(new_content)

            # Git commit if configured for this zone
            if ctx.git_commit:
                self._core._git_commit(zone_root, f"Convert EOL to {target_format}: {path}")
            
            return self._core._format_response(
                True,
                data={
                    "path": path,
                    "original_format": original_format,
                    "new_format": target_format,
                    "changed": True,
                    "lines_converted": crlf_count if to_unix else lf_only_count,
                },
                message=f"Converted {path} from {original_format} to {target_format}"
            )
            
        except StorageError as e:
            return self._core._format_error(e, "shed_convert_eol")
        except Exception:
            return self._core._format_response(False, message="Unexpected error during line ending conversion")
    
    async def shed_hexdump(
        self,
        zone: str,
        path: str,
        offset: int = 0,
        length: int = 256,
        group: str = None,
        allow_zone_in_path: bool = False,
        __user__: dict = None,
        __metadata__: dict = None,
    ) -> str:
        """
        Shows hexadecimal dump of file (replaces missing 'xxd'/'hexdump' commands).

        :param zone: Target zone ("uploads", "storage", "documents", or "group")
        :param path: Path to file
        :param offset: Starting offset in bytes (default: 0)
        :param length: Number of bytes to display (default: 256, max: 4096)
        :param group: Group name (required if zone="group")
        :return: Hex dump as text

        Example:
            shed_hexdump(zone="storage", path="binary.dat", offset=0, length=128)
            shed_hexdump(zone="group", group="MyTeam", path="data.bin")
        """
        try:
            # Resolve zone using standard helper
            ctx = self._core._resolve_zone(zone, group, __user__, __metadata__, require_write=False)
            zone_root = ctx.zone_root
            zone_name = ctx.zone_name

            # Validate and resolve path
            path = self._core._validate_relative_path(path, zone_name, allow_zone_in_path)
            file_path = self._core._resolve_chroot_path(zone_root, path)

            if not file_path.exists():
                raise StorageError("FILE_NOT_FOUND", f"File not found: {path}")

            if file_path.is_dir():
                raise StorageError("INVALID_FORMAT", "Cannot hexdump directory")

            # LLM Guardrail: convert None to defaults, validate types
            if offset is None:
                offset = 0
            elif not isinstance(offset, int):
                raise StorageError(
                    "INVALID_PARAMETER",
                    f"offset must be an integer or None, got: {repr(offset)} ({type(offset).__name__})",
                    hint="Use offset=0 for start of file, or omit for default"
                )
            if length is None:
                length = DEFAULT_HEXDUMP_BYTES
            elif not isinstance(length, int):
                raise StorageError(
                    "INVALID_PARAMETER",
                    f"length must be an integer or None, got: {repr(length)} ({type(length).__name__})",
                    hint="Use length=256 or omit for default"
                )

            # Clamp values
            offset = max(0, offset)
            length = max(1, min(length, MAX_HEXDUMP_BYTES))
            
            # Read file portion
            file_size = file_path.stat().st_size
            
            if offset >= file_size:
                return self._core._format_response(
                    True,
                    data={"path": path, "offset": offset, "size": file_size, "hexdump": "(offset beyond file)"},
                    message="Offset is beyond end of file"
                )
            
            with open(file_path, 'rb') as f:
                f.seek(offset)
                data = f.read(length)
            
            # Format hex dump (xxd style)
            lines = []
            for i in range(0, len(data), 16):
                chunk = data[i:i+16]
                addr = f"{offset + i:08x}"
                
                # Hex part
                hex_parts = []
                for j in range(0, 16, 2):
                    if j < len(chunk):
                        if j + 1 < len(chunk):
                            hex_parts.append(f"{chunk[j]:02x}{chunk[j+1]:02x}")
                        else:
                            hex_parts.append(f"{chunk[j]:02x}  ")
                    else:
                        hex_parts.append("    ")
                hex_str = " ".join(hex_parts)
                
                # ASCII part
                ascii_str = ""
                for b in chunk:
                    if 32 <= b < 127:
                        ascii_str += chr(b)
                    else:
                        ascii_str += "."
                
                lines.append(f"{addr}: {hex_str}  {ascii_str}")
            
            hexdump_output = "\n".join(lines)
            
            return self._core._format_response(
                True,
                data={
                    "path": path,
                    "offset": offset,
                    "length": len(data),
                    "file_size": file_size,
                    "hexdump": hexdump_output,
                },
                message=f"Hexdump of {path} ({len(data)} bytes from offset {offset})"
            )
            
        except StorageError as e:
            return self._core._format_error(e, "shed_hexdump")
        except Exception:
            return self._core._format_response(False, message="Unexpected error during hexdump")

    async def shed_sqlite(
        self,
        zone: str,
        path: str,
        query: str = None,
        params: list = None,
        limit: int = None,
        output_csv: str = None,
        import_csv: str = None,
        table: str = None,
        if_exists: str = "fail",
        delimiter: str = None,
        encoding: str = None,
        date_columns: list = None,
        date_format: str = None,
        decimal: str = None,
        skip_rows: int = 0,
        has_header: bool = True,
        group: str = None,
        allow_zone_in_path: bool = False,
        __user__: dict = None,
        __metadata__: dict = None,
    ) -> str:
        """
        Executes SQL query on a SQLite database file OR imports a CSV file.
        Python builtin using sqlite3 module, no external dependency.
        
        ⚠️ CONTEXT PROTECTION: SELECT queries without LIMIT return only 10 rows by default!
        Use limit=N for more rows, or output_csv="file.csv" to export all results to file.
        
        :param zone: Target zone ("uploads", "storage", "documents", or "group")
        :param path: Path to .db file (created if not exists for write queries)
        :param query: SQL query to execute (optional if import_csv is provided)
        :param params: Optional list of parameters for parameterized queries (prevents SQL injection)
        :param limit: Max rows to return for SELECT (default: 10 if no LIMIT in query). Use limit=0 for no limit (dangerous!).
        :param output_csv: Export ALL results to this CSV file instead of returning rows (prevents context pollution)
        :param import_csv: Path to CSV file to import (in same zone). If provided, imports CSV instead of running query.
        :param table: Table name for CSV import (required if import_csv is provided)
        :param if_exists: What to do if table exists: "fail" (error), "replace" (drop+recreate), "append" (add rows)
        :param delimiter: CSV delimiter. None=auto-detect, or specify: ",", ";", "\\t", "|"
        :param encoding: File encoding. None=auto-detect (tries utf-8, latin-1, cp1252), or specify: "utf-8", "latin-1", "cp1252", etc.
        :param date_columns: List of column names to parse as dates, e.g. ["created_at", "updated_at"]
        :param date_format: Date format: None=auto, "dayfirst" (DD/MM/YYYY), "monthfirst" (MM/DD/YYYY), or strptime format like "%d/%m/%Y"
        :param decimal: Decimal separator for numbers. None="." (default), or "," for European format (1.234,56)
        :param skip_rows: Number of rows to skip at the beginning (before header). Default: 0
        :param has_header: True if first row (after skip_rows) contains column names, False if data only. Default: True. ⚠️ If False, columns are named col_1, col_2, etc.
        :param group: Group ID or name (required if zone="group")
        :return: Query results or import stats as JSON
        
        Examples:
            # === SQL QUERIES ===
            
            # Basic SELECT (returns max 10 rows by default)
            shed_sqlite(zone="storage", path="data.db", query="SELECT * FROM users")
            # → Returns 10 rows + warning if more exist
            
            # Request more rows explicitly
            shed_sqlite(zone="storage", path="data.db", query="SELECT * FROM users", limit=100)
            # → Returns up to 100 rows
            
            # Use LIMIT in SQL (respected as-is)
            shed_sqlite(zone="storage", path="data.db", query="SELECT * FROM users LIMIT 50")
            # → Returns 50 rows, no warning
            
            # Export ALL results to CSV (no context pollution!)
            shed_sqlite(zone="storage", path="data.db", 
                        query="SELECT * FROM users", output_csv="users_export.csv")
            # → Writes all rows to file, returns stats only
            
            # Create a table
            shed_sqlite(zone="storage", path="data.db", 
                        query="CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, email TEXT)")
            
            # Insert with parameters (safe from SQL injection)
            shed_sqlite(zone="storage", path="data.db",
                        query="INSERT INTO users (name, email) VALUES (?, ?)",
                        params=["Alice", "alice@example.com"])
            
            # === CSV IMPORT (FAST, NO CONTEXT POLLUTION) ===
            
            # Basic import (auto-detects delimiter and encoding)
            shed_sqlite(zone="storage", path="data.db",
                        import_csv="users.csv", table="users")
            
            # French/European CSV (semicolon, comma decimal, latin-1)
            shed_sqlite(zone="storage", path="data.db",
                        import_csv="french_data.csv", table="sales",
                        delimiter=";", decimal=",", encoding="latin-1")
            
            # With date parsing (European format DD/MM/YYYY)
            shed_sqlite(zone="storage", path="data.db",
                        import_csv="orders.csv", table="orders",
                        date_columns=["order_date", "ship_date"], date_format="dayfirst")
            
            # TSV file (tab-separated)
            shed_sqlite(zone="storage", path="data.db",
                        import_csv="data.tsv", table="data", delimiter="\\t")
            
            # Skip header rows (e.g., file has title + empty row before headers)
            shed_sqlite(zone="storage", path="data.db",
                        import_csv="report.csv", table="report", skip_rows=2)
            
            # CSV without header row (data only, columns named col_1, col_2, ...)
            shed_sqlite(zone="storage", path="data.db",
                        import_csv="raw_data.csv", table="raw", has_header=False)
            
            # Replace existing table
            shed_sqlite(zone="storage", path="data.db",
                        import_csv="updated.csv", table="users", if_exists="replace")
        
        Note: Uses pandas if available (best auto-detection), falls back to csv module.
              CSV import keeps data on disk - no context pollution!
        """
        try:
            # Use centralized zone resolution
            ctx = self._core._resolve_zone(zone, group, __user__, __metadata__, require_write=False)
            zone_root = ctx.zone_root
            zone_name = ctx.zone_name
            readonly = ctx.readonly

            # Validate and resolve path
            path = self._core._validate_relative_path(path, zone_name, allow_zone_in_path)
            db_path = self._core._resolve_chroot_path(zone_root, path)
            
            # Ensure parent directory exists
            db_path.parent.mkdir(parents=True, exist_ok=True)

            # Validate mutually exclusive parameters
            if import_csv and query:
                raise StorageError(
                    "INVALID_PARAMETER",
                    "Cannot use both 'import_csv' and 'query' parameters",
                    hint="Use import_csv for CSV import OR query for SQL execution, not both"
                )

            # =====================================================
            # CSV IMPORT MODE
            # =====================================================
            if import_csv:
                # LLM Guardrail: convert skip_rows=None to 0
                if skip_rows is None:
                    skip_rows = 0
                elif not isinstance(skip_rows, int):
                    raise StorageError(
                        "INVALID_PARAMETER",
                        f"skip_rows must be an integer, got: {repr(skip_rows)} ({type(skip_rows).__name__})",
                        hint="Use skip_rows=0 (default) or skip_rows=2 to skip 2 rows"
                    )

                # Validate parameters
                if not table:
                    raise StorageError(
                        "MISSING_PARAMETER",
                        "table parameter required for CSV import",
                        hint="Add table='tablename' parameter"
                    )

                if if_exists not in ("fail", "replace", "append"):
                    raise StorageError(
                        "INVALID_PARAMETER",
                        f"Invalid if_exists value: {if_exists}",
                        hint="Use 'fail', 'replace', or 'append'"
                    )
                
                # Block CSV import in readonly zones
                if readonly:
                    raise StorageError(
                        "ZONE_FORBIDDEN",
                        "CSV import not allowed in Uploads zone",
                        hint="Move the CSV to Storage or Documents first, then import"
                    )
                
                # Validate table name (prevent SQL injection)
                if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', table):
                    raise StorageError(
                        "INVALID_PARAMETER",
                        "Invalid table name",
                        {"table": table},
                        hint="Table name must be alphanumeric with underscores, starting with letter or underscore"
                    )
                
                # Resolve CSV path (in same zone)
                import_csv_path = self._core._validate_relative_path(import_csv, zone_name, allow_zone_in_path)
                csv_path = self._core._resolve_chroot_path(zone_root, import_csv_path)
                
                if not csv_path.exists():
                    raise StorageError(
                        "FILE_NOT_FOUND",
                        f"CSV file not found: {import_csv}",
                        hint="Check the path is correct and relative to the zone"
                    )
                
                # Try to use pandas (best auto-detection), fallback to csv module
                use_pandas = False
                try:
                    import pandas as pd
                    use_pandas = True
                except ImportError:
                    pass
                
                conn = sqlite3.connect(str(db_path), timeout=30.0)
                
                try:
                    cursor = conn.cursor()
                    
                    # Check if table exists
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
                    table_exists = cursor.fetchone() is not None
                    
                    if table_exists:
                        if if_exists == "fail":
                            raise StorageError(
                                "TABLE_EXISTS",
                                f"Table '{table}' already exists",
                                hint="Use if_exists='replace' or if_exists='append'"
                            )
                        elif if_exists == "replace":
                            cursor.execute(f'DROP TABLE IF EXISTS "{table}"')
                            table_exists = False
                    
                    import_info = {"method": "unknown"}
                    
                    if use_pandas:
                        # =====================================================
                        # PANDAS IMPORT (best auto-detection)
                        # =====================================================
                        import_info["method"] = "pandas"
                        
                        # Build pandas read_csv arguments
                        pd_kwargs = {}
                        
                        # Delimiter: auto-detect or specified
                        if delimiter:
                            pd_kwargs['sep'] = delimiter.replace('\\t', '\t')
                        else:
                            pd_kwargs['sep'] = None  # Auto-detect
                            pd_kwargs['engine'] = 'python'  # Required for sep=None
                        
                        # Encoding: auto-detect or specified
                        if encoding:
                            pd_kwargs['encoding'] = encoding
                        else:
                            # Try common encodings
                            detected_encoding = None
                            for enc in ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']:
                                try:
                                    with open(csv_path, 'r', encoding=enc) as test_f:
                                        test_f.read(8192)
                                    detected_encoding = enc
                                    break
                                except (UnicodeDecodeError, UnicodeError):
                                    continue
                            pd_kwargs['encoding'] = detected_encoding or 'utf-8'
                            import_info['detected_encoding'] = pd_kwargs['encoding']
                        
                        # Skip rows
                        if skip_rows > 0:
                            pd_kwargs['skiprows'] = skip_rows
                        
                        # Decimal separator
                        if decimal:
                            pd_kwargs['decimal'] = decimal
                        
                        # Date parsing
                        if date_columns:
                            pd_kwargs['parse_dates'] = date_columns
                            if date_format:
                                if date_format == 'dayfirst':
                                    pd_kwargs['dayfirst'] = True
                                elif date_format == 'monthfirst':
                                    pd_kwargs['dayfirst'] = False
                                elif date_format != 'auto':
                                    pd_kwargs['date_format'] = date_format
                        
                        # Handle NA values
                        pd_kwargs['na_values'] = ['', 'NA', 'N/A', 'NULL', 'null', 'None', 'none', '#N/A', '#NA']
                        pd_kwargs['keep_default_na'] = True
                        
                        # Handle header
                        if not has_header:
                            pd_kwargs['header'] = None  # No header row in file
                        
                        # Read CSV
                        try:
                            df = pd.read_csv(str(csv_path), **pd_kwargs)
                        except Exception:
                            raise StorageError(
                                "CSV_PARSE_ERROR",
                                "Failed to parse CSV with pandas",
                                {"csv": import_csv},
                                hint="Try specifying delimiter, encoding, or skip_rows explicitly"
                            )
                        
                        # Get detected delimiter if auto-detected
                        if 'sep' in pd_kwargs and pd_kwargs['sep'] is None:
                            # pandas doesn't expose detected delimiter easily, so we sniff it
                            import csv as csv_module
                            try:
                                with open(csv_path, 'r', encoding=pd_kwargs.get('encoding', 'utf-8')) as sniff_f:
                                    sample = sniff_f.read(8192)
                                    dialect = csv_module.Sniffer().sniff(sample)
                                    import_info['detected_delimiter'] = repr(dialect.delimiter)
                            except Exception:
                                pass
                        
                        # Generate or sanitize column names
                        if not has_header:
                            # No header: generate col_1, col_2, ...
                            df.columns = [f"col_{i+1}" for i in range(len(df.columns))]
                            import_info['generated_columns'] = True
                        else:
                            # Sanitize column names from header
                            clean_columns = []
                            for col in df.columns:
                                clean = re.sub(r'[^\w]', '_', str(col).strip())
                                if not clean or clean[0].isdigit():
                                    clean = '_' + clean
                                clean_columns.append(clean)
                            df.columns = clean_columns

                        # Check column count limit (DoS protection)
                        if len(df.columns) > CSV_MAX_COLUMNS:
                            raise StorageError(
                                "CSV_TOO_WIDE",
                                f"CSV has too many columns ({len(df.columns)})",
                                {"columns": len(df.columns), "max": CSV_MAX_COLUMNS},
                                f"Maximum {CSV_MAX_COLUMNS} columns allowed"
                            )

                        # Import to SQLite
                        pandas_if_exists = 'append' if if_exists == 'append' and table_exists else 'replace'
                        df.to_sql(table, conn, if_exists=pandas_if_exists, index=False)
                        
                        total_rows = len(df)
                        clean_headers = list(df.columns)
                        
                        # Get column types
                        import_info['column_types'] = {col: str(df[col].dtype) for col in df.columns}
                        
                    else:
                        # =====================================================
                        # CSV MODULE FALLBACK (always available)
                        # =====================================================
                        import csv as csv_module
                        import_info["method"] = "csv_module"
                        
                        # Detect encoding if not specified
                        file_encoding = encoding
                        if not file_encoding:
                            for enc in ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']:
                                try:
                                    with open(csv_path, 'r', encoding=enc) as test_f:
                                        test_f.read(8192)
                                    file_encoding = enc
                                    break
                                except (UnicodeDecodeError, UnicodeError):
                                    continue
                            file_encoding = file_encoding or 'utf-8'
                            import_info['detected_encoding'] = file_encoding
                        
                        # Detect delimiter using Sniffer if not specified
                        csv_delimiter = delimiter.replace('\\t', '\t') if delimiter else None
                        if not csv_delimiter:
                            try:
                                with open(csv_path, 'r', encoding=file_encoding) as sniff_f:
                                    sample = sniff_f.read(8192)
                                    dialect = csv_module.Sniffer().sniff(sample, delimiters=',;\t|')
                                    csv_delimiter = dialect.delimiter
                                    import_info['detected_delimiter'] = repr(csv_delimiter)
                            except csv_module.Error:
                                csv_delimiter = ','  # Default to comma
                        
                        # Read and import CSV
                        with open(csv_path, 'r', newline='', encoding=file_encoding) as f:
                            # Skip rows if needed
                            for _ in range(skip_rows):
                                next(f, None)
                            
                            reader = csv_module.reader(f, delimiter=csv_delimiter)
                            
                            # Handle header row
                            if has_header:
                                headers = next(reader)  # First row = column names
                                # Sanitize column names
                                clean_headers = []
                                for h in headers:
                                    clean = re.sub(r'[^\w]', '_', h.strip())
                                    if not clean or clean[0].isdigit():
                                        clean = '_' + clean
                                    clean_headers.append(clean)
                                first_data_row = None
                            else:
                                # No header: first row is data, generate column names
                                first_data_row = next(reader, None)
                                if first_data_row is None:
                                    raise StorageError(
                                        "CSV_EMPTY",
                                        "CSV file is empty (no data rows)",
                                        {"csv": import_csv}
                                    )
                                clean_headers = [f"col_{i+1}" for i in range(len(first_data_row))]
                                import_info['generated_columns'] = True

                            # Check column count limit (DoS protection)
                            if len(clean_headers) > CSV_MAX_COLUMNS:
                                raise StorageError(
                                    "CSV_TOO_WIDE",
                                    f"CSV has too many columns ({len(clean_headers)})",
                                    {"columns": len(clean_headers), "max": CSV_MAX_COLUMNS},
                                    f"Maximum {CSV_MAX_COLUMNS} columns allowed"
                                )

                            # Create table if needed
                            if not table_exists or if_exists == "replace":
                                columns_def = ", ".join(f'"{col}" TEXT' for col in clean_headers)
                                cursor.execute(f'CREATE TABLE "{table}" ({columns_def})')

                            # Prepare INSERT statement
                            placeholders = ", ".join("?" * len(clean_headers))
                            insert_sql = f'INSERT INTO "{table}" VALUES ({placeholders})'
                            
                            # Date parsing setup
                            date_col_indices = []
                            if date_columns:
                                for dc in date_columns:
                                    # Find column index (case-insensitive, sanitized)
                                    dc_clean = re.sub(r'[^\w]', '_', dc.strip())
                                    if not dc_clean or dc_clean[0].isdigit():
                                        dc_clean = '_' + dc_clean
                                    try:
                                        idx = clean_headers.index(dc_clean)
                                        date_col_indices.append(idx)
                                    except ValueError:
                                        # Try original name
                                        for i, h in enumerate(clean_headers):
                                            if h.lower() == dc.lower() or h.lower() == dc_clean.lower():
                                                date_col_indices.append(i)
                                                break
                            
                            # Batch insert for performance
                            batch_size = 1000
                            batch = []
                            total_rows = 0
                            
                            # If has_header=False, we already read the first data row
                            # Create an iterator that includes it
                            if first_data_row is not None:
                                import itertools
                                all_rows = itertools.chain([first_data_row], reader)
                            else:
                                all_rows = reader
                            
                            for row in all_rows:
                                # Pad or truncate row to match headers
                                if len(row) < len(clean_headers):
                                    row = list(row) + [''] * (len(clean_headers) - len(row))
                                elif len(row) > len(clean_headers):
                                    row = list(row[:len(clean_headers)])
                                else:
                                    row = list(row)
                                
                                # Process decimal separator if specified
                                if decimal and decimal != '.':
                                    for i, val in enumerate(row):
                                        if val and i not in date_col_indices:
                                            # Try to convert European decimal format
                                            try:
                                                # Remove thousand separators (spaces or dots) and replace decimal
                                                cleaned = val.replace(' ', '').replace('.', '')
                                                cleaned = cleaned.replace(decimal, '.')
                                                float(cleaned)  # Test if it's a number
                                                row[i] = cleaned
                                            except (ValueError, AttributeError):
                                                pass  # Not a number, keep original
                                
                                # Process date columns
                                if date_col_indices and date_format:
                                    from datetime import datetime
                                    for idx in date_col_indices:
                                        if idx < len(row) and row[idx]:
                                            try:
                                                if date_format == 'dayfirst':
                                                    # Try common European formats
                                                    for fmt in ['%d/%m/%Y', '%d-%m-%Y', '%d.%m.%Y', '%d/%m/%y', '%d-%m-%y']:
                                                        try:
                                                            dt = datetime.strptime(row[idx], fmt)
                                                            row[idx] = dt.strftime('%Y-%m-%d')
                                                            break
                                                        except ValueError:
                                                            continue
                                                elif date_format == 'monthfirst':
                                                    # Try common US formats
                                                    for fmt in ['%m/%d/%Y', '%m-%d-%Y', '%m/%d/%y', '%m-%d-%y']:
                                                        try:
                                                            dt = datetime.strptime(row[idx], fmt)
                                                            row[idx] = dt.strftime('%Y-%m-%d')
                                                            break
                                                        except ValueError:
                                                            continue
                                                elif date_format != 'auto':
                                                    dt = datetime.strptime(row[idx], date_format)
                                                    row[idx] = dt.strftime('%Y-%m-%d')
                                            except (ValueError, TypeError):
                                                pass  # Keep original value
                                
                                batch.append(tuple(row))
                                
                                if len(batch) >= batch_size:
                                    cursor.executemany(insert_sql, batch)
                                    total_rows += len(batch)
                                    batch = []
                            
                            # Insert remaining rows
                            if batch:
                                cursor.executemany(insert_sql, batch)
                                total_rows += len(batch)
                    
                    conn.commit()

                    response_data = {
                        "db_path": path,
                        "csv_path": import_csv,
                        "table": table,
                        "columns": clean_headers,
                        "rows_imported": total_rows,
                        "if_exists": if_exists,
                        "import_info": import_info,
                    }
                    
                    if delimiter:
                        response_data["delimiter"] = delimiter
                    if encoding:
                        response_data["encoding"] = encoding
                    if date_columns:
                        response_data["date_columns"] = date_columns
                    if decimal:
                        response_data["decimal"] = decimal
                    
                    return self._core._format_response(
                        True,
                        data=response_data,
                        message=f"Imported {total_rows} rows from '{import_csv}' into table '{table}' (using {import_info['method']})"
                    )
                    
                except StorageError:
                    conn.rollback()  # Explicit rollback on error
                    raise
                except sqlite3.Error:
                    conn.rollback()  # Explicit rollback on error
                    raise StorageError(
                        "EXEC_ERROR",
                        "SQLite error during CSV import",
                        {"csv": import_csv, "table": table}
                    )
                except Exception:
                    conn.rollback()  # Explicit rollback on error
                    raise StorageError(
                        "EXEC_ERROR",
                        "CSV import failed",
                        {"csv": import_csv, "table": table},
                        hint="Try specifying delimiter, encoding, or check CSV format"
                    )
                finally:
                    conn.close()
            
            # =====================================================
            # SQL QUERY MODE
            # =====================================================
            if not query:
                raise StorageError(
                    "MISSING_PARAMETER",
                    "Either 'query' or 'import_csv' parameter is required",
                    hint="Provide a SQL query or a CSV file to import"
                )
            
            # Check if this is a read or write query
            query_stripped = query.strip().upper()
            is_read_query = query_stripped.startswith(("SELECT", "PRAGMA", "EXPLAIN"))

            # Block write operations if sqlite_readonly valve is enabled
            if self.valves.sqlite_readonly and not is_read_query:
                raise StorageError(
                    "COMMAND_FORBIDDEN",
                    "Write operations are disabled (sqlite_readonly=True)",
                    {"query_type": query_stripped.split()[0] if query_stripped else "unknown"},
                    hint="Only SELECT, PRAGMA, and EXPLAIN queries are allowed. Ask admin to disable sqlite_readonly."
                )

            # Block write operations in readonly zones
            if readonly and not is_read_query:
                raise StorageError(
                    "ZONE_FORBIDDEN",
                    "Write operations not allowed in Uploads zone",
                    hint="Move the database to Storage or Documents first"
                )
            
            # Block dangerous operations
            # Strip comments first to prevent bypass attacks like AT/**/TACH
            # Convert to uppercase to prevent case-based bypass (e.g., "attach" instead of "ATTACH")
            query_no_comments = self._core._strip_sql_comments(query_stripped).upper()
            dangerous_patterns = [
                "ATTACH", "DETACH",  # Could access other databases
                "LOAD_EXTENSION",    # Could load malicious code
            ]
            for pattern in dangerous_patterns:
                if pattern in query_no_comments:
                    raise StorageError(
                        "COMMAND_FORBIDDEN",
                        f"SQL operation '{pattern}' is not allowed for security reasons"
                    )
            
            # Execute the query
            params = params or []
            conn = sqlite3.connect(str(db_path), timeout=10.0)
            conn.row_factory = sqlite3.Row
            
            try:
                cursor = conn.cursor()
                cursor.execute(query, params)
                
                if is_read_query:
                    # Get column names first
                    columns = [description[0] for description in cursor.description] if cursor.description else []
                    
                    # Check if user wants CSV export (all results, no context pollution)
                    if output_csv:
                        # Block CSV export in readonly zones
                        if readonly:
                            raise StorageError(
                                "ZONE_READONLY",
                                "Cannot export CSV to read-only zone",
                                {"zone": zone_name, "output_csv": output_csv},
                                hint="Use 'storage' or 'documents' zone for CSV export"
                            )
                        # Export all results to CSV file
                        import csv as csv_module
                        
                        output_csv_path = self._core._validate_relative_path(output_csv, zone_name, allow_zone_in_path)
                        csv_path = self._core._resolve_chroot_path(zone_root, output_csv_path)
                        self._core._ensure_dir(csv_path.parent)
                        
                        row_count = 0
                        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                            writer = csv_module.writer(f)
                            writer.writerow(columns)  # Header
                            
                            # Fetch and write in batches to handle large results
                            while True:
                                batch = cursor.fetchmany(1000)
                                if not batch:
                                    break
                                for row in batch:
                                    writer.writerow(list(row))
                                    row_count += 1
                        
                        return self._core._format_response(
                            True,
                            data={
                                "path": path,
                                "query": query,
                                "output_csv": output_csv,
                                "rows_exported": row_count,
                                "columns": columns,
                            },
                            message=f"Exported {row_count} row(s) to {output_csv}"
                        )
                    
                    # Check if query already has LIMIT
                    has_limit = bool(re.search(r'\bLIMIT\s+\d+', query_stripped))
                    
                    # Determine effective limit
                    DEFAULT_LIMIT = 10
                    if has_limit:
                        # User specified LIMIT in SQL - respect it
                        rows = cursor.fetchall()
                        total_rows = len(rows)
                        results = [dict(zip(columns, row)) for row in rows] if rows else []
                        truncated = False
                        effective_limit = None
                    else:
                        # No LIMIT in query - apply protection
                        if limit is None:
                            effective_limit = DEFAULT_LIMIT
                        elif limit == 0:
                            effective_limit = None  # No limit (dangerous but explicit)
                        else:
                            effective_limit = limit
                        
                        if effective_limit:
                            # First count total rows (for user info)
                            rows = cursor.fetchall()
                            total_rows = len(rows)
                            
                            # Truncate if needed
                            if total_rows > effective_limit:
                                results = [dict(zip(columns, row)) for row in rows[:effective_limit]]
                                truncated = True
                            else:
                                results = [dict(zip(columns, row)) for row in rows]
                                truncated = False
                        else:
                            # limit=0: user explicitly requested all, but protect against memory exhaustion
                            # Use fetchmany with batching up to MAX_SQL_ROWS
                            results = []
                            batch_size = 1000
                            while True:
                                batch = cursor.fetchmany(batch_size)
                                if not batch:
                                    break
                                for row in batch:
                                    results.append(dict(zip(columns, row)))
                                    if len(results) >= MAX_SQL_ROWS:
                                        break
                                if len(results) >= MAX_SQL_ROWS:
                                    break
                            total_rows = len(results)
                            truncated = len(results) >= MAX_SQL_ROWS
                    
                    # Build response
                    response_data = {
                        "path": path,
                        "query": query,
                        "row_count": len(results),
                        "columns": columns,
                        "rows": results,
                    }
                    
                    if truncated:
                        response_data["total_rows"] = total_rows
                        response_data["truncated"] = True
                        response_data["limit_applied"] = effective_limit
                        message = (
                            f"⚠️ No LIMIT in query. Showing {len(results)}/{total_rows} rows to protect context. "
                            f"Options: (1) Add LIMIT to SQL, (2) Use limit=N parameter for more rows, "
                            f"(3) Use output_csv='results.csv' to export ALL {total_rows} rows to file."
                        )
                    else:
                        message = f"Query returned {len(results)} row(s)"
                    
                    return self._core._format_response(True, data=response_data, message=message)
                else:
                    # For INSERT/UPDATE/DELETE/CREATE/etc.
                    conn.commit()
                    rowcount = cursor.rowcount
                    lastrowid = cursor.lastrowid

                    return self._core._format_response(
                        True,
                        data={
                            "path": path,
                            "query": query,
                            "rows_affected": rowcount,
                            "last_row_id": lastrowid,
                        },
                        message=f"Query executed successfully ({rowcount} row(s) affected)"
                    )
                    
            except sqlite3.Error:
                conn.rollback()  # Explicit rollback on error
                raise StorageError(
                    "EXEC_ERROR",
                    "SQLite query failed",
                    {"query": query},
                    hint="Check your SQL syntax"
                )
            finally:
                conn.close()

        except StorageError as e:
            return self._core._format_error(e, "shed_sqlite")
        except Exception:
            return self._core._format_response(False, message="Unexpected error during SQLite operation")

    # =========================================================================
    # DOWNLOAD LINKS (3 functions)
    # =========================================================================
    
    
    async def shed_link_create(
        self,
        zone: str,
        path: str,
        group: str = None,
        __user__: dict = None,
        __metadata__: dict = None,
    ) -> str:
        """
        Create a download link for a file.
        
        Uploads the file to Open WebUI's file system and returns a download URL.
        The link works while the user is logged in (uses session cookie).
        Works with any file type: PDF, images, ZIP, CSV, etc.
        
        :param zone: Zone to read from ("uploads", "storage", "documents", "group")
        :param path: Relative path to the file
        :param group: Group name (required if zone="group")
        :return: JSON with download_url and file_id
        
        Related functions:
            shed_link_list()   - List all download links
            shed_link_delete() - Remove a download link
        
        Examples:
            shed_link_create(zone="storage", path="exports/report.pdf")
            shed_link_create(zone="storage", path="archives/data.zip")
            shed_link_create(zone="group", group="team", path="shared/presentation.pptx")
        """
        try:
            if __user__ is None:
                __user__ = {}

            # Resolve zone using standard helper
            ctx = self._core._resolve_zone(zone, group, __user__, __metadata__, require_write=False)
            zone_root = ctx.zone_root
            zone_name = ctx.zone_name

            # Validate path (check for zone prefix duplication)
            path = self._core._validate_relative_path(path, zone_name, allow_zone_in_path=False)

            # Resolve and validate path
            filepath = self._core._resolve_chroot_path(zone_root, path)
            
            if not filepath.exists():
                raise StorageError(
                    "FILE_NOT_FOUND",
                    f"File not found: {path}",
                    {"zone": zone, "path": path}
                )
            
            if not filepath.is_file():
                raise StorageError(
                    "NOT_A_FILE",
                    f"Path is not a file: {path}",
                    {"zone": zone, "path": path}
                )
            
            # Use Open WebUI internal Python API via Bridge (no HTTP request = no deadlock)
            
            # Get user ID
            user_id = __user__.get("id")
            if not user_id:
                raise StorageError(
                    "NO_USER_ID",
                    "User ID not available",
                    {},
                    "This should not happen - contact administrator"
                )
            
            # Generate unique file ID
            file_id = str(uuid.uuid4())
            filename = filepath.name
            file_size = filepath.stat().st_size
            
            # Detect content type
            content_type, _ = mimetypes.guess_type(filename)
            if not content_type:
                content_type = "application/octet-stream"
            
            # Copy file to Open WebUI uploads directory
            uploads_dir = Path("/app/backend/data/uploads")
            uploads_dir.mkdir(parents=True, exist_ok=True)
            dest_path = uploads_dir / f"{file_id}_{filename}"
            shutil.copy2(filepath, dest_path)
            
            try:
                # Create database entry using Bridge (isolates Open WebUI API changes)
                bridge = _OpenWebUIBridge()
                file_item = bridge.insert_file(
                    user_id=user_id,
                    file_id=file_id,
                    filename=filename,
                    file_path=str(dest_path),
                    content_type=content_type,
                    file_size=file_size,
                    metadata={"fileshed_link": True, "source_zone": zone, "source_path": path}
                )
                
                if not file_item:
                    # Clean up copied file on failure
                    dest_path.unlink(missing_ok=True)
                    raise StorageError(
                        "DB_ERROR",
                        "Failed to create file entry in database",
                        {"file_id": file_id}
                    )
                
                # Build download URL (full URL with base from valve)
                base_url = self.valves.openwebui_api_url.rstrip('/')
                download_url = f"{base_url}/api/v1/files/{file_id}/content"
                
                # Markdown clickable link for easy copy-paste by LLM
                clickable_link = f"[📥 Download {filename}]({download_url})"
                
                return self._core._format_response(True, {
                    "file_id": file_id,
                    "download_url": download_url,
                    "clickable_link": clickable_link,
                    "filename": filename,
                    "size_bytes": file_size,
                    "zone": zone,
                    "path": path,
                }, message=f"Link ready: {clickable_link}")
                
            except StorageError:
                # Clean up on failure
                dest_path.unlink(missing_ok=True)
                raise
            except Exception:
                dest_path.unlink(missing_ok=True)
                raise StorageError(
                    "INTERNAL_API_ERROR",
                    "Error calling Open WebUI API",
                    None,
                    "Check Open WebUI version compatibility"
                )
                
        except StorageError as e:
            return self._core._format_error(e, "shed_link_create")
        except Exception:
            return self._core._format_response(False, message="Unexpected error while creating download link")

    async def shed_link_list(
        self,
        __user__: dict = None,
    ) -> str:
        """
        List all download links created by the current user.
        
        :return: JSON with list of links (file_id, filename, download_url, size)
        
        Related functions:
            shed_link_create() - Create a new download link
            shed_link_delete() - Remove a download link
        
        Examples:
            shed_link_list()
        """
        try:
            if __user__ is None:
                __user__ = {}
            user_id = __user__.get("id")
            if not user_id:
                raise StorageError(
                    "NO_USER_ID",
                    "User ID not available",
                    {},
                    "This should not happen - contact administrator"
                )
            
            # Use Bridge to get user's files
            bridge = _OpenWebUIBridge()
            bridge._ensure_initialized()
            
            # Get files using the internal API
            all_files = bridge._files_class.get_files_by_user_id(user_id)
            
            # Filter only files created by Fileshed (have fileshed_link marker)
            files = []
            if all_files:
                for f in all_files:
                    if hasattr(f, 'meta') and f.meta and isinstance(f.meta, dict):
                        meta_data = f.meta.get('data', {})
                        if isinstance(meta_data, dict) and meta_data.get('fileshed_link') == True:
                            files.append(f)
            
            if not files:
                return self._core._format_response(True, {
                    "files": [],
                    "count": 0
                }, message="No download links found")
            
            # Format file list
            base_url = self.valves.openwebui_api_url.rstrip('/')
            file_list = []
            for f in files:
                download_url = f"{base_url}/api/v1/files/{f.id}/content"
                file_info = {
                    "file_id": f.id,
                    "filename": f.filename,
                    "download_url": download_url,
                    "clickable_link": f"[📥 {f.filename}]({download_url})",
                    "created_at": f.created_at,
                }
                # Add size and source info if available in meta
                if hasattr(f, 'meta') and f.meta and isinstance(f.meta, dict):
                    file_info["size_bytes"] = f.meta.get("size")
                    file_info["content_type"] = f.meta.get("content_type")
                    meta_data = f.meta.get('data', {})
                    if isinstance(meta_data, dict):
                        file_info["source_zone"] = meta_data.get("source_zone")
                        file_info["source_path"] = meta_data.get("source_path")
                file_list.append(file_info)
            
            return self._core._format_response(True, {
                "files": file_list,
                "count": len(file_list)
            }, message=f"Found {len(file_list)} download link(s)")
            
        except StorageError as e:
            return self._core._format_error(e, "shed_link_list")
        except Exception:
            return self._core._format_response(False, message="Unexpected error while listing download links")

    async def shed_link_delete(
        self,
        file_id: str,
        __user__: dict = None,
    ) -> str:
        """
        Remove a download link from Open WebUI.
        
        This deletes both the database entry and the physical file.
        
        :param file_id: The file ID returned by shed_link_create() or shed_link_list()
        :return: JSON with success status
        
        Related functions:
            shed_link_create() - Create a new download link
            shed_link_list()   - List all download links
        
        Examples:
            shed_link_delete(file_id="317ef925-c87a-44fd-8d29-acdccb8e6070")
        """
        try:
            if __user__ is None:
                __user__ = {}
            user_id = __user__.get("id")
            if not user_id:
                raise StorageError(
                    "NO_USER_ID",
                    "User ID not available",
                    {},
                    "This should not happen - contact administrator"
                )
            
            if not file_id:
                raise StorageError(
                    "MISSING_FILE_ID",
                    "file_id parameter is required",
                    {},
                    "Use shed_link_list() to get file IDs"
                )
            
            # Use Bridge to get and verify file ownership
            bridge = _OpenWebUIBridge()
            file_item = bridge.get_file_by_id(file_id)
            
            if not file_item:
                raise StorageError(
                    "FILE_NOT_FOUND",
                    f"File not found: {file_id}",
                    {"file_id": file_id},
                    "Use shed_link_list() to see your download links"
                )
            
            # Verify ownership
            if file_item.user_id != user_id:
                raise StorageError(
                    "ACCESS_DENIED",
                    "You can only delete your own download links",
                    {"file_id": file_id}
                )
            
            # Verify this is a Fileshed-created link (not a user upload)
            is_fileshed_link = False
            if hasattr(file_item, 'meta') and file_item.meta and isinstance(file_item.meta, dict):
                meta_data = file_item.meta.get('data', {})
                if isinstance(meta_data, dict) and meta_data.get('fileshed_link') == True:
                    is_fileshed_link = True
            
            if not is_fileshed_link:
                raise StorageError(
                    "NOT_A_FILESHED_LINK",
                    f"This file was not created by Fileshed: {file_id}",
                    {"file_id": file_id, "filename": file_item.filename},
                    "shed_link_delete only removes links created by shed_link_create. Use Open WebUI UI to manage other files."
                )
            
            # Get file path before deletion
            file_path = file_item.path if hasattr(file_item, 'path') else None
            filename = file_item.filename
            
            # Delete from database
            bridge.delete_file_by_id(file_id)
            
            # Delete physical file if it exists
            if file_path:
                try:
                    Path(file_path).unlink(missing_ok=True)
                except Exception:
                    pass  # File might already be gone
            
            return self._core._format_response(True, {
                "file_id": file_id,
                "filename": filename,
                "deleted": True
            }, message=f"Link deleted: {filename}")
            
        except StorageError as e:
            return self._core._format_error(e, "shed_link_delete")
        except Exception:
            return self._core._format_response(False, message="Unexpected error while deleting download link")

    # =========================================================================
    # HOWTO GUIDES (targeted help to avoid context pollution)
    # =========================================================================
    


    async def shed_help(
        self,
        howto: str = None,
        __user__: dict = None,
        __metadata__: dict = None,
    ) -> str:
        """
        Get help for Fileshed. Call without arguments for quick reference,
        or with a howto topic for detailed guides.
        
        :param howto: Optional topic. Available: download, csv_to_sqlite, upload, share, edit, commands, network, paths, large_files, full
        :return: Help text
        
        Examples:
            shed_help()                        # Quick reference + list of howtos
            shed_help(howto="download")        # How to download files (use curl, not fetch_url)
            shed_help(howto="csv_to_sqlite")   # How to import CSV into SQLite (fast)
            shed_help(howto="large_files")     # Process large files without context pollution
            shed_help(howto="commands")        # Available commands + workarounds
            shed_help(howto="full")            # Complete documentation
        """
        
        # List of available howtos
        available_howtos = list(self._core.HOWTO_GUIDES.keys()) + ["full"]
        
        # No argument (or empty string): return quick help + howto list
        if not howto:
            help_text = """# 🛖 Fileshed - Quick Reference

## 🔥 WORKFLOWS (choose one!)

### Workflow 1: Direct Write (simple, no locking)
```
shed_patch_text(zone="storage", path="file.txt", content="Hello", overwrite=True)
```
One function, done. Use `overwrite=True` to replace entire file.

### Workflow 2: Locked Edit (with locking, for concurrent access)
```
1. shed_lockedit_open(zone="storage", path="file.txt")      # Lock + copy to editzone
2. shed_lockedit_overwrite(zone="storage", path="file.txt", content="New content")  # Edit copy
3. shed_lockedit_save(zone="storage", path="file.txt")      # Save + unlock (CLOSES edit mode!)
```
⚠️ After shed_lockedit_save, the file is CLOSED. To edit again, start from step 1.

### Workflow 3: Shell Commands
```
shed_exec(zone="storage", cmd="ls", args=["-la"])           # List files
shed_exec(zone="storage", cmd="cat", args=["file.txt"])     # Read file
shed_exec(zone="storage", cmd="grep", args=["pattern", "file.txt"])  # Search
```

## 📁 ZONES

| Zone | Purpose | Git versioned? |
|------|---------|----------------|
| `storage` | General files, scripts, data | No |
| `documents` | Important docs, versioned | Yes (auto-commit) |
| `uploads` | User uploaded files (read-only) | No |
| `group` | Shared with team (requires group=) | Yes |

## ⚡ QUICK OPERATIONS

| Task | Command |
|------|---------|
| List files | `shed_exec(zone="storage", cmd="ls", args=["-la"])` |
| Read file | `shed_exec(zone="storage", cmd="cat", args=["file.txt"])` |
| Create folder | `shed_exec(zone="storage", cmd="mkdir", args=["-p", "folder"])` |
| Create/overwrite file | `shed_patch_text(zone="storage", path="f.txt", content="...", overwrite=True)` |
| Append to file | `shed_patch_text(zone="storage", path="f.txt", content="...", position="end")` |
| Delete file | `shed_delete(zone="storage", path="file.txt")` |
| Copy file | `shed_exec(zone="storage", cmd="cp", args=["src.txt", "dst.txt"])` |
| Move/rename | `shed_rename(zone="storage", old_path="a.txt", new_path="b.txt")` |

## 🔗 SHARE FILES

```
shed_link_create(zone="storage", path="report.pdf")  # Get download link
shed_link_list()                                      # List your links
shed_link_delete(file_id="...")                       # Remove link
```

## 📊 STATS & INFO

```
shed_stats()              # Storage usage
shed_parameters()         # Configuration limits
shed_allowed_commands()   # Available shell commands
shed_tree(zone="storage") # Directory tree
```

## 📚 HOWTO GUIDES (for complex tasks)

""" + "\n".join(f"- `shed_help(howto=\"{h}\")` — {self._core._get_howto_description(h)}" for h in available_howtos) + """

## ⚠️ COMMON MISTAKES

```
❌ position="overwrite"           → Use overwrite=True instead!
❌ position="at" in patch_text    → "at" is for patch_bytes. Use "before"/"after" with line=N
❌ shed_lockedit_save twice           → save CLOSES edit mode, reopen with shed_lockedit_open
❌ shed_patch_text for folders    → Use shed_exec(cmd="mkdir", args=["-p", "folder"])
❌ paths with zone name           → Paths are RELATIVE: "file.txt" not "Storage/file.txt"
```
"""
            # Build howtos dict for structured access
            howtos_dict = {h: self._core._get_howto_description(h) for h in available_howtos}
            
            return self._core._format_response(
                True, 
                data={
                    "help": help_text,
                    "howtos": howtos_dict
                }, 
                message="Help in data.help, howtos comprehensive list in data.howtos"
            )
        
        # Specific howto requested
        howto_lower = howto.lower().strip()
        
        if howto_lower == "full":
            return self._core._format_response(True, data={"help": self._core._get_full_help()}, message="Full documentation in data.help")
        
        if howto_lower in self._core.HOWTO_GUIDES:
            return self._core._format_response(True, data={"help": self._core.HOWTO_GUIDES[howto_lower], "topic": howto_lower}, message=f"Guide '{howto_lower}' in data.help")
        
        # Unknown howto
        howtos_dict = {h: self._core._get_howto_description(h) for h in available_howtos}
        return self._core._format_response(False, data={"howtos": howtos_dict}, message=f"Unknown howto '{howto}'. Available howtos in data.howtos")
    


    async def shed_stats(
        self,
        __user__: dict = None,
        __metadata__: dict = None,
    ) -> str:
        """
        Returns usage statistics.
        
        :return: Statistics as JSON
        """
        try:
            user_root = self._core._get_user_root(__user__)
            
            def get_dir_size(path: Path) -> int:
                if not path.exists():
                    return 0
                total = 0
                for f in path.rglob("*"):
                    if f.is_file():
                        total += f.stat().st_size
                return total
            
            def count_files(path: Path) -> int:
                if not path.exists():
                    return 0
                return sum(1 for f in path.rglob("*") if f.is_file())
            
            uploads_size = get_dir_size(user_root / "Uploads")
            storage_size = get_dir_size(user_root / "Storage" / "data")
            documents_size = get_dir_size(user_root / "Documents" / "data")
            
            total_size = uploads_size + storage_size + documents_size
            quota = self.valves.quota_per_user_mb * 1024 * 1024
            
            stats = {
                "uploads": {
                    "size_bytes": uploads_size,
                    "size_human": f"{uploads_size / 1024 / 1024:.2f} MB",
                    "files": count_files(user_root / "Uploads"),
                },
                "storage": {
                    "size_bytes": storage_size,
                    "size_human": f"{storage_size / 1024 / 1024:.2f} MB",
                    "files": count_files(user_root / "Storage" / "data"),
                },
                "documents": {
                    "size_bytes": documents_size,
                    "size_human": f"{documents_size / 1024 / 1024:.2f} MB",
                    "files": count_files(user_root / "Documents" / "data"),
                },
                "total": {
                    "size_bytes": total_size,
                    "size_human": f"{total_size / 1024 / 1024:.2f} MB",
                    "quota_mb": self.valves.quota_per_user_mb,
                    "usage_percent": f"{(total_size / quota) * 100:.1f}%",
                },
            }
            
            return self._core._format_response(True, data=stats)

        except Exception:
            return self._core._format_response(False, message="Unexpected error while calculating storage stats")

    async def shed_parameters(
        self,
        __user__: dict = None,
        __metadata__: dict = None,
    ) -> str:
        """
        Returns current valve configuration (read-only).
        
        Call this function to answer user questions about:
        - "Is network access enabled?" -> check network_mode
        - "Can I use curl/wget?" -> check network_mode != "disabled"
        - "Can I git push?" -> check network_mode == "all"
        - "What's my storage quota?" -> check quota_per_user_mb
        - "What's the max file size?" -> check max_file_size_mb
        - "What's the default timeout?" -> check exec_timeout_default
        
        Values can only be changed by admins in Open WebUI (Workspace > Tools > Valves).
        
        :return: All valve values as JSON (read-only)
        
        Example:
            shed_parameters()
        
        Key fields:
          - network_mode: "disabled" | "safe" | "all"
            - "disabled": No network (curl/wget/git clone blocked)
            - "safe": Downloads only (curl GET, git clone/pull, no push)
            - "all": Full network access (uploads/push allowed)
          - quota_per_user_mb: Storage limit per user
          - quota_per_group_mb: Storage limit per group
          - max_file_size_mb: Maximum single file size
          - exec_timeout_default: Default command timeout (seconds)
        """
        try:
            params = {
                "storage_base_path": self.valves.storage_base_path,
                "quota_per_user_mb": self.valves.quota_per_user_mb,
                "quota_per_group_mb": self.valves.quota_per_group_mb,
                "max_file_size_mb": self.valves.max_file_size_mb,
                "lock_max_age_hours": self.valves.lock_max_age_hours,
                "exec_timeout_default": self.valves.exec_timeout_default,
                "exec_timeout_max": self.valves.exec_timeout_max,
                "group_default_mode": self.valves.group_default_mode,
                "network_mode": self.valves.network_mode,
                "openwebui_api_url": self.valves.openwebui_api_url,
            }
            
            # Add helpful derived info
            params["_info"] = {
                "network_enabled": self.valves.network_mode != "disabled",
                "network_upload_allowed": self.valves.network_mode == "all",
                "groups_available": GROUPS_AVAILABLE,
            }
            
            return self._core._format_response(True, data=params, message="Current valve configuration")

        except Exception:
            return self._core._format_response(False, message="Unexpected error while getting parameters")

    async def shed_allowed_commands(
        self,
        __user__: dict = None,
        __metadata__: dict = None,
    ) -> str:
        """
        Tests available commands in container.
        
        :return: List of available/missing commands by zone
        """
        try:
            # Cache the result
            if self._core._commands_cache is not None:
                return self._core._format_response(True, data=self._core._commands_cache)
            
            # Check all commands via Layer 2
            all_commands = WHITELIST_READWRITE
            available = []
            missing = []
            
            for cmd in sorted(all_commands):
                if self._core._check_command_available(cmd):
                    available.append(cmd)
                else:
                    missing.append(cmd)
            
            # Check network commands status (curl/wget + git network ops + media tools)
            network_status = {
                "mode": self.valves.network_mode,
                "curl": {
                    "installed": self._core._check_command_available("curl"),
                    "enabled": self.valves.network_mode in ("safe", "all"),
                },
                "wget": {
                    "installed": self._core._check_command_available("wget"),
                    "enabled": self.valves.network_mode in ("safe", "all"),
                },
                "git_clone": self.valves.network_mode in ("safe", "all"),
                "git_fetch": self.valves.network_mode in ("safe", "all"),
                "git_pull": self.valves.network_mode in ("safe", "all"),
                "git_push": self.valves.network_mode == "all",
                "ffmpeg": {
                    "installed": self._core._check_command_available("ffmpeg"),
                    "enabled": self.valves.network_mode in ("safe", "all"),
                    "output_protocols_blocked": self.valves.network_mode == "safe",
                },
                "pandoc": {
                    "installed": self._core._check_command_available("pandoc"),
                    "urls_enabled": self.valves.network_mode in ("safe", "all"),
                },
            }
            
            result = {
                "uploads": {
                    "available": [c for c in available if c in WHITELIST_READONLY],
                    "missing": [c for c in missing if c in WHITELIST_READONLY],
                },
                "storage": {
                    "available": [c for c in available if c in WHITELIST_READWRITE],
                    "missing": [c for c in missing if c in WHITELIST_READWRITE],
                },
                "documents": {
                    "available": [c for c in available if c in WHITELIST_READWRITE],
                    "missing": [c for c in missing if c in WHITELIST_READWRITE],
                },
                "network": network_status,
                "summary": {
                    "total_whitelist": len(all_commands),
                    "available": len(available),
                    "missing": len(missing),
                    "coverage": f"{(len(available) / len(all_commands)) * 100:.1f}%",
                },
            }
            
            self._core._commands_cache = result
            return self._core._format_response(True, data=result)

        except Exception:
            return self._core._format_response(False, message="Unexpected error while listing allowed commands")

    async def shed_force_unlock(
        self,
        zone: str = "",
        path: str = "",
        group: str = "",
        allow_zone_in_path: bool = False,
        __user__: dict = None,
        __metadata__: dict = None,
    ) -> str:
        """
        Forces file unlock (crash recovery).

        Use this if a file is stuck in edit mode after a crash.

        :param zone: "storage" or "documents" (for personal zones)
        :param path: File path relative to zone
        :param group: Group ID (for group zones - use instead of zone)
        :return: Confirmation as JSON

        Examples:
            shed_force_unlock(zone="storage", path="stuck_file.txt")
            shed_force_unlock(group="team", path="locked_doc.md")
        """
        try:
            # Validate path is provided
            if not path:
                raise StorageError("MISSING_PARAMETER", "path is required")

            # Determine if group or personal zone
            if group:
                # Group mode
                group = self._core._validate_group_id(group)
                self._core._check_group_access(__user__, group)
                zone_name = f"Group:{group}"

                # Validate path with zone_name
                path = self._core._validate_relative_path(path, zone_name, allow_zone_in_path)

                group_path = self._core._get_groups_root() / group
                lock_path = group_path / "locks" / (path + ".lock")
                editzone_base = group_path / "editzone"
                zone_display = zone_name
            else:
                # Personal zone mode
                if not zone:
                    raise StorageError(
                        "MISSING_PARAMETER",
                        "Must specify either 'zone' or 'group'",
                        hint="Use zone='storage' or zone='documents', or group='group_id'"
                    )

                if zone.lower() not in ("storage", "documents"):
                    raise StorageError(
                        "ZONE_FORBIDDEN",
                        f"Invalid zone: {zone}",
                        {},
                        "Use 'storage' or 'documents'"
                    )

                user_root = self._core._get_user_root(__user__)
                zone_name = "Storage" if zone.lower() == "storage" else "Documents"

                # Validate path with zone_name
                path = self._core._validate_relative_path(path, zone_name, allow_zone_in_path)

                zone_root = user_root / zone_name
                lock_path = self._core._get_lock_path(zone_root, path)
                editzone_base = zone_root / "editzone"
                zone_display = zone_name
            
            # Find and delete all editzones for this path
            if editzone_base.exists():
                for conv_dir in editzone_base.iterdir():
                    if conv_dir.is_dir():
                        edit_path = conv_dir / path
                        if edit_path.exists():
                            self._core._rm_with_empty_parents(edit_path, editzone_base)
            
            # Delete lock
            if lock_path.exists():
                self._core._rm_with_empty_parents(lock_path, lock_path.parent.parent / "locks")
            
            return self._core._format_response(True, message=f"Unlocked: {path} in {zone_display}")
            
        except StorageError as e:
            return self._core._format_error(e, "shed_force_unlock")
        except Exception:
            return self._core._format_response(False, message="Unexpected error while forcing unlock")
    
    async def shed_maintenance(
        self,
        __user__: dict = None,
        __metadata__: dict = None,
    ) -> str:
        """
        Cleans expired locks and orphan editzones (personal and group spaces).
        
        :return: Cleanup report as JSON
        """
        try:
            if __user__ is None:
                __user__ = {}
            user_root = self._core._get_user_root(__user__)
            max_age_hours = self.valves.lock_max_age_hours
            now = datetime.now(timezone.utc)
            
            cleaned = {
                "expired_locks": [],
                "corrupted_locks": [],
                "orphan_editzones": [],
            }
            
            def clean_zone(zone_root: Path, zone_name: str):
                """Helper to clean locks and editzones in a zone."""
                locks_dir = zone_root / "locks"
                editzone_dir = zone_root / "editzone"
                
                # 1. Clean expired and corrupted locks
                if locks_dir.exists():
                    for lock_file in locks_dir.rglob("*.lock"):
                        try:
                            lock_data = json.loads(lock_file.read_text())
                            locked_at_str = lock_data.get("locked_at", "")
                            
                            if locked_at_str:
                                locked_at = datetime.fromisoformat(
                                    locked_at_str.replace("Z", "+00:00")
                                )
                                age_hours = (now - locked_at).total_seconds() / 3600
                                
                                if age_hours > max_age_hours:
                                    # Expired lock
                                    rel_path = lock_file.relative_to(locks_dir)
                                    path_str = str(rel_path)[:-5]  # Remove .lock
                                    
                                    # Delete associated editzone
                                    conv_id = lock_data.get("conv_id", "")
                                    if conv_id:
                                        edit_path = editzone_dir / conv_id / path_str
                                        if edit_path.exists():
                                            self._core._rm_with_empty_parents(edit_path, editzone_dir)
                                    
                                    # Delete lock
                                    self._core._rm_with_empty_parents(lock_file, locks_dir)
                                    cleaned["expired_locks"].append(f"{zone_name}/{path_str}")
                            
                        except json.JSONDecodeError:
                            # Corrupted lock
                            rel_path = lock_file.relative_to(locks_dir)
                            self._core._rm_with_empty_parents(lock_file, locks_dir)
                            cleaned["corrupted_locks"].append(f"{zone_name}/{rel_path}")
                        except (ValueError, TypeError):
                            pass  # Invalid date, ignore
                
                # 2. Clean orphan editzones (without corresponding lock)
                if editzone_dir.exists():
                    for conv_dir in editzone_dir.iterdir():
                        if conv_dir.is_dir():
                            for item in conv_dir.rglob("*"):
                                if item.is_file():
                                    rel_path = item.relative_to(conv_dir)
                                    lock_path = locks_dir / (str(rel_path) + ".lock")
                                    
                                    if not lock_path.exists():
                                        # Orphan editzone
                                        self._core._rm_with_empty_parents(item, editzone_dir)
                                        cleaned["orphan_editzones"].append(
                                            f"{zone_name}/editzone/{conv_dir.name}/{rel_path}"
                                        )
            
            # Clean personal zones
            for zone_name in ("Storage", "Documents"):
                zone_root = user_root / zone_name
                clean_zone(zone_root, zone_name)
            
            # Clean group zones (for groups the user belongs to)
            user_id = __user__.get("id", "")
            user_groups = self._core._get_user_groups(user_id)
            groups_root = self._core._get_groups_root()
            
            for group in user_groups:
                group_path = groups_root / group.id
                if group_path.exists():
                    clean_zone(group_path, f"Group:{group.id}")
            
            total = (len(cleaned["expired_locks"]) + 
                    len(cleaned["corrupted_locks"]) + 
                    len(cleaned["orphan_editzones"]))
            
            return self._core._format_response(
                True,
                data=cleaned,
                message=f"Maintenance complete: {total} element(s) cleaned"
            )

        except Exception:
            return self._core._format_response(False, message="Unexpected error during maintenance cleanup")

    # =========================================================================
    # GROUP FUNCTIONS (14 functions)
    # =========================================================================
    
    # --- Discovery (2) ---
    
    async def shed_group_list(
        self,
        __user__: dict = None,
    ) -> str:
        """
        Lists groups the user belongs to.
        
        :return: List of groups with id, name, and member count
        """
        try:
            if __user__ is None:
                __user__ = {}
            if not GROUPS_AVAILABLE:
                return self._core._format_response(
                    False,
                    message="Group features are not available (Open WebUI Groups API not found)"
                )

            user_id = __user__.get("id", "")
            groups = self._core._get_user_groups(user_id)
            
            result = []
            for g in groups:
                # Use dedicated API method to get member count
                member_count = 0
                try:
                    member_count = Groups.get_group_member_count_by_id(g.id) or 0
                except Exception:
                    pass
                
                result.append({
                    "id": g.id,
                    "name": g.name,
                    "description": g.description or "",
                    "member_count": member_count,
                })
            
            return self._core._format_response(
                True,
                data={"groups": result, "count": len(result)},
                message=f"Found {len(result)} group(s)"
            )
            
        except StorageError as e:
            return self._core._format_error(e, "shed_group_list")
        except Exception:
            return self._core._format_response(False, message="Unexpected error while listing groups")
    
    async def shed_group_info(
        self,
        group: str,
        __user__: dict = None,
    ) -> str:
        """
        Shows group files, ownership information, and statistics.
        
        :param group: Group ID or group name
        :return: Group information including files and their ownership
        """
        try:
            # Validate group_id
            group = self._core._validate_group_id(group)
            self._core._check_group_access(__user__, group)
            
            # Get group info and member list using dedicated API methods
            group_obj = Groups.get_group_by_id(group)
            try:
                member_ids = Groups.get_group_user_ids_by_id(group) or []
            except Exception:
                member_ids = []
            
            data_path = self._core._get_group_data_path(group)
            
            if not data_path.exists():
                return self._core._format_response(
                    True,
                    data={
                        "group_id": group,
                        "name": group_obj.name if group_obj else group,
                        "members": member_ids,
                        "member_count": len(member_ids),
                        "files": [],
                        "total_files": 0,
                        "total_size": 0
                    },
                    message="Group space is empty"
                )
            
            # Get all ownership records for this group in a single query
            all_ownership, _ = self._core._db_execute(
                "SELECT file_path, owner_id, write_access FROM file_ownership WHERE group_id = ?",
                (group,)
            )
            ownership_map = {row["file_path"]: {"owner_id": row["owner_id"], "write_access": row["write_access"]} for row in all_ownership}
            
            # List files with ownership
            files = []
            total_size = 0
            
            for item in data_path.rglob("*"):
                if item.is_file() and ".git" not in item.parts:
                    rel_path = str(item.relative_to(data_path))
                    try:
                        size = item.stat().st_size
                    except (OSError, FileNotFoundError):
                        continue  # Skip files that disappeared
                    total_size += size
                    
                    ownership = ownership_map.get(rel_path)
                    files.append({
                        "path": rel_path,
                        "size": size,
                        "owner": ownership["owner_id"] if ownership else "unknown",
                        "mode": ownership["write_access"] if ownership else "unknown",
                    })
            
            return self._core._format_response(
                True,
                data={
                    "group_id": group,
                    "name": group_obj.name if group_obj else group,
                    "members": member_ids,
                    "member_count": len(member_ids),
                    "files": files,
                    "total_files": len(files),
                    "total_size": total_size,
                    "total_size_human": f"{total_size / 1024 / 1024:.2f} MB",
                },
                message=f"Group has {len(files)} file(s) and {len(member_ids)} member(s)"
            )
            
        except StorageError as e:
            return self._core._format_error(e, "shed_group_info")
        except Exception:
            return self._core._format_response(False, message="Unexpected error while getting group info")
    
    # --- Operations (4) ---
    
    async def shed_group_set_mode(
        self,
        group: str,
        path: str,
        mode: str,
        allow_zone_in_path: bool = False,
        __user__: dict = None,
    ) -> str:
        """
        Changes the write mode of a file (owner only).

        :param group: Group ID or group name
        :param path: File path
        :param mode: New mode: 'owner', 'group', or 'owner_ro'
        :return: Operation result as JSON
        """
        try:
            if __user__ is None:
                __user__ = {}
            # Validate group_id
            group = self._core._validate_group_id(group)
            self._core._check_group_access(__user__, group)
            user_id = __user__.get("id", "")
            zone_name = f"Group:{group}"

            # Validate path
            path = self._core._validate_relative_path(path, zone_name, allow_zone_in_path)
            
            # Validate mode
            if mode not in ("owner", "group", "owner_ro"):
                raise StorageError(
                    "INVALID_MODE",
                    f"Invalid mode: {mode}",
                    hint="Use 'owner', 'group', or 'owner_ro'"
                )
            
            # Check ownership
            ownership = self._core._get_file_ownership(group, path)
            if ownership is None:
                raise StorageError("FILE_NOT_FOUND", f"No ownership record for: {path}")
            
            if ownership["owner_id"] != user_id:
                raise StorageError(
                    "NOT_FILE_OWNER",
                    "Only the file owner can change the write mode",
                    {"path": path}
                )

            # Update mode
            old_mode = ownership["write_access"]
            self._core._set_file_ownership(group, path, user_id, mode)
            
            return self._core._format_response(
                True,
                data={"path": path, "old_mode": old_mode, "new_mode": mode},
                message=f"File mode changed from '{old_mode}' to '{mode}'"
            )
            
        except StorageError as e:
            return self._core._format_error(e, "shed_group_set_mode")
        except Exception:
            return self._core._format_response(False, message="Unexpected error while setting group mode")
    
    async def shed_group_chown(
        self,
        group: str,
        path: str,
        new_owner: str,
        allow_zone_in_path: bool = False,
        __user__: dict = None,
    ) -> str:
        """
        Transfers file ownership to another user (owner only).

        :param group: Group ID or group name
        :param path: File path
        :param new_owner: User ID of new owner
        :return: Operation result as JSON
        """
        try:
            if __user__ is None:
                __user__ = {}
            # Validate group_id
            group = self._core._validate_group_id(group)
            self._core._check_group_access(__user__, group)
            user_id = __user__.get("id", "")
            zone_name = f"Group:{group}"

            # Validate path
            path = self._core._validate_relative_path(path, zone_name, allow_zone_in_path)
            
            # Validate new_owner (sanitize)
            if not new_owner or not isinstance(new_owner, str):
                raise StorageError("INVALID_OWNER", "new_owner is required")
            new_owner = new_owner.strip()
            if not new_owner or len(new_owner) > 255:
                raise StorageError("INVALID_OWNER", "Invalid new_owner format")
            # Block dangerous characters for SQL and filesystem
            if any(c in new_owner for c in [";", "'", '"', "\\", "/", "\n", "\r", "\0"]):
                raise StorageError("INVALID_OWNER", "new_owner contains invalid characters")
            
            # Check ownership
            ownership = self._core._get_file_ownership(group, path)
            if ownership is None:
                raise StorageError("FILE_NOT_FOUND", f"No ownership record for: {path}")
            
            if ownership["owner_id"] != user_id:
                raise StorageError(
                    "NOT_FILE_OWNER",
                    "Only the file owner can transfer ownership",
                    {"path": path}
                )

            # Check new owner is group member
            if not self._core._is_group_member(new_owner, group):
                raise StorageError(
                    "INVALID_OWNER",
                    f"User '{new_owner}' is not a member of this group"
                )
            
            # Update ownership
            self._core._db_execute(
                "UPDATE file_ownership SET owner_id = ?, updated_at = CURRENT_TIMESTAMP WHERE group_id = ? AND file_path = ?",
                (new_owner, group, path)
            )
            
            return self._core._format_response(
                True,
                data={"path": path, "old_owner": user_id, "new_owner": new_owner},
                message=f"Ownership transferred to '{new_owner}'"
            )
            
        except StorageError as e:
            return self._core._format_error(e, "shed_group_chown")
        except Exception:
            return self._core._format_response(False, message="Unexpected error while changing file ownership")
    
    # --- Bridge (1) ---
    
    async def shed_copy_to_group(
        self,
        src_zone: str,
        src_path: str,
        group: str,
        dest_path: str,
        message: str = "Add file to group",
        mode: str = None,
        overwrite: bool = False,
        allow_zone_in_path: bool = False,
        __user__: dict = None,
        __metadata__: dict = None,
    ) -> str:
        """
        Copies a file from personal space to group.

        :param src_zone: Source zone ('uploads', 'storage', or 'documents')
        :param src_path: Source file path (relative to src_zone, don't include zone name!)
        :param group: Target group ID
        :param dest_path: Destination path in group (don't include zone name!)
        :param message: Git commit message
        :param mode: Write mode: 'owner', 'group', or 'owner_ro' (default from config)
        :param overwrite: If True, overwrite existing destination file (default: False)
        :param allow_zone_in_path: Allow paths starting with zone name (default: False)
        :return: Operation result as JSON
        """
        try:
            if __user__ is None:
                __user__ = {}
            if __metadata__ is None:
                __metadata__ = {}
            # Validate group_id
            group = self._core._validate_group_id(group)
            self._core._check_group_access(__user__, group)
            user_id = __user__.get("id", "")
            conv_id = self._core._get_conv_id(__metadata__)

            # Resolve source zone first to get zone_name for validation
            user_root = self._core._get_user_root(__user__)
            src_zone_lower = src_zone.lower()

            if src_zone_lower == "uploads":
                src_base = user_root / "Uploads" / conv_id
                src_zone_name = "Uploads"
            elif src_zone_lower == "storage":
                src_base = user_root / "Storage" / "data"
                src_zone_name = "Storage"
            elif src_zone_lower == "documents":
                src_base = user_root / "Documents" / "data"
                src_zone_name = "Documents"
            else:
                raise StorageError(
                    "ZONE_FORBIDDEN",
                    f"Invalid source zone: {src_zone}",
                    hint="Use 'uploads', 'storage', or 'documents'"
                )

            # Validate paths with zone name check
            src_path = self._core._validate_relative_path(src_path, src_zone_name, allow_zone_in_path)
            dest_path = self._core._validate_relative_path(dest_path, f"Group:{group}", allow_zone_in_path)
            
            source = self._core._resolve_chroot_path(src_base, src_path)
            
            if not source.exists():
                raise StorageError("FILE_NOT_FOUND", f"File not found: {src_path}")
            
            # Check file size
            if source.is_file():
                file_size = source.stat().st_size
                max_size = self.valves.max_file_size_mb * 1024 * 1024
                if file_size > max_size:
                    raise StorageError(
                        "FILE_TOO_LARGE",
                        f"File exceeds max size ({self.valves.max_file_size_mb} MB)",
                        {"size_mb": round(file_size / 1024 / 1024, 2), "max_mb": self.valves.max_file_size_mb}
                    )
            
            # Check group quota
            self._core._check_group_quota(group, self._core._get_path_size(source))
            
            # Resolve destination
            data_path = self._core._ensure_group_space(group)
            dest = self._core._resolve_chroot_path(data_path, dest_path)

            # Check if destination exists
            if dest.exists():
                if overwrite:
                    if dest.is_dir():
                        shutil.rmtree(str(dest))
                    else:
                        dest.unlink()
                else:
                    raise StorageError(
                        "FILE_EXISTS",
                        f"Destination exists: {dest_path}",
                        hint="Use overwrite=True to replace the existing file"
                    )

            existing = self._core._get_file_ownership(group, dest_path)
            if existing:
                can_write, error = self._core._can_write_group_file(group, dest_path, user_id)
                if not can_write:
                    raise StorageError(error, f"Cannot overwrite file: {error}")
            
            # Copy (handle both files and directories)
            dest.parent.mkdir(parents=True, exist_ok=True)
            if source.is_dir():
                shutil.copytree(source, dest)
            else:
                shutil.copy2(source, dest)
            
            # Set ownership
            effective_mode = mode or self.valves.group_default_mode
            if effective_mode not in ("owner", "group", "owner_ro"):
                effective_mode = "group"
            self._core._set_file_ownership(group, dest_path, user_id, effective_mode)
            
            # Git commit
            self._core._git_commit_as_user(data_path, message, user_id)
            
            return self._core._format_response(
                True,
                data={
                    "src_zone": src_zone,
                    "src_path": src_path,
                    "group": group,
                    "dest_path": dest_path,
                    "mode": effective_mode,
                },
                message=f"File copied to group '{group}' with mode '{effective_mode}'"
            )
            
        except StorageError as e:
            return self._core._format_error(e, "shed_copy_to_group")
        except Exception:
            return self._core._format_response(False, message="Unexpected error while copying to group")
