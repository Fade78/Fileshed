
# Fileshed Tool Audit Report

## File Name and Version
- File: Fileshed.py
- Version: 1.0.3

## Architecture and Separation of Concerns
**Intent and Behavior**: The tool implements a strict separation between public API (`Tools` class) and internal implementation (`_FileshedCore` class), exposing only `shed_*` functions to the LLM while hiding all internal methods. This follows the SPEC.md's explicit design requirement to prevent LLMs from accessing internal methods.

**Strengths**: 
- Clear separation of concerns with well-defined boundaries.
- Internal methods are completely hidden from the LLM.
- Zone resolution and path validation are centralized in `_resolve_zone` and `_resolve_chroot_path`.
- The SPEC explicitly states this is a security requirement to prevent LLMs from attempting to call internal methods.

**Weaknesses**:
- The single-file architecture (as required by OpenWebUI tool deployment) creates a large monolithic file that could become difficult to maintain.
- While the separation is well-implemented, the SPEC notes that "this use case is not supported in the current version" for multi-instance deployments with distributed locks.

**Rating**: ★★★★☆ (4/5)

## Public vs Internal API Exposure
**Intent and Behavior**: The SPEC explicitly states that "only `shed_*` functions are visible to the LLM" and "internal methods are NOT exposed." The implementation strictly enforces this by only defining `shed_*` methods in the `Tools` class.

**Strengths**:
- Complete elimination of internal method exposure to the LLM.
- All internal methods are prefixed with `_` and documented as internal.
- The SPEC states: "LLMs sometimes attempted to call these internal methods directly" - this implementation prevents that.
- The SPEC also notes that "this separation relies on OpenWebUI's architecture which only exposes `Tools` class methods."

**Weaknesses**:
- The tool relies on OpenWebUI's internal API behavior, which could change between versions without warning.
- The `_OpenWebUIBridge` class is a necessary abstraction layer for OpenWebUI integration, but its existence is a potential point of failure if OpenWebUI changes its internal API.

**Rating**: ★★★★★ (5/5)

## Filesystem Access and Isolation
**Intent and Behavior**: The tool implements chroot-like isolation using `_resolve_chroot_path` to prevent path traversal attacks. The SPEC states: "All paths use `_resolve_chroot_path()` — Prevents path traversal attacks."

**Strengths**:
- Comprehensive path validation with multiple layers:
  - `_validate_relative_path` checks for path traversal and zone prefix
  - `_resolve_chroot_path` verifies paths stay within the zone
  - Symlink checks before extraction
- The SPEC explicitly states: "This prevents path traversal attacks."
- The tool enforces the critical rule: "Paths are always relative to the zone root: 'Storage/file.txt' not 'Storage/Storage/file.txt'."

**Weaknesses**:
- The implementation relies on path normalization (Unicode NFC), which could potentially be bypassed in rare cases.
- The SPEC notes that "the LLM sometimes attempted to call these internal methods directly" - while this is prevented by the API separation, it could still lead to misconfiguration if users are unaware of the path rules.

**Rating**: ★★★★☆ (4/5)

## Command Execution and Argument Safety
**Intent and Behavior**: The tool implements a strict command whitelist with separate read-only and read-write lists, and validates all command arguments to prevent command injection and dangerous operations.

**Strengths**:
- Comprehensive command whitelisting with separate lists for different zones.
- Argument validation blocks dangerous patterns with regex: `; | && & > >> << $( ${`.
- The SPEC explicitly states: "This is defense-in-depth, not absolute protection."
- The tool blocks dangerous options like `find -exec` and `awk system()`.
- The SPEC notes: "Block dangerous options: `find -exec`, `awk system()`, `xargs`."

**Weaknesses**:
- The regex-based validation could be bypassed by carefully crafted inputs (e.g., `;` encoded as Unicode characters).
- The SPEC acknowledges this limitation: "This is defense-in-depth, not absolute protection."
- The tool does not implement sandboxing for command execution, relying solely on argument validation.

**Rating**: ★★★★☆ (4/5)

## Network Access and Data Exfiltration Risks
**Intent and Behavior**: The tool implements a configurable network mode (`network_mode`) with three levels: `disabled`, `safe`, and `all`, controlling network access to prevent data exfiltration.

**Strengths**:
- Clear network mode configuration with appropriate restrictions:
  - `disabled`: No network access
  - `safe`: Downloads only (blocks exfiltration)
  - `all`: Full access (risky, with warning)
- The SPEC explicitly states: "Network-capable commands: ffmpeg, ffprobe, pandoc, convert, identify, curl, wget, git."
- The tool blocks dangerous options in `safe` mode (e.g., `ffmpeg` output protocols like `rtmp://`).
- The SPEC notes: "In 'safe' mode, output protocols that can send data to remote servers are blocked."

**Weaknesses**:
- The `all` mode is available by default (though disabled by default), creating a potential risk if administrators don't properly configure it.
- The SPEC acknowledges the risk: "Use with caution" for `all` mode.
- The implementation relies on valve configuration to control risk, which is an admin-only setting.

**Rating**: ★★★★☆ (4/5)

## Concurrency, Locking, and Crash Recovery
**Intent and Behavior**: The tool implements a file locking mechanism for concurrent access, with a specific workflow for locked editing.

**Strengths**:
- Atomic file-based locking using `os.open()` with `O_CREAT | O_EXCL`.
- The SPEC states: "Locks use `os.open()` with `O_CREAT | O_EXCL` for atomic acquisition."
- The tool implements a clear workflow: `shed_lockedit_open` → `shed_lockedit_overwrite` → `shed_lockedit_save`.
- The SPEC notes: "Locks are reliable for a single OpenWebUI instance."
- The `shed_maintenance` function cleans up expired locks and orphaned editzones.

**Weaknesses**:
- The locking mechanism is not distributed and would fail in multi-instance deployments (e.g., multiple OpenWebUI containers sharing NFS storage).
- The SPEC acknowledges this limitation: "For multi-instance deployments, an external locking mechanism (Redis, database) would be needed. This use case is not supported in the current version."

**Rating**: ★★★★☆ (4/5)

## Group Permission Model
**Intent and Behavior**: The tool implements a group permission model with three modes (`owner`, `group`, `owner_ro`) for collaborative file access.

**Strengths**:
- The SPEC explicitly describes the permission model with clear use cases.
- The implementation uses a dedicated SQLite database (`access_auth.sqlite`) to track file ownership and permissions.
- The SPEC states: "Group ownership model is implemented with three modes."
- The tool provides functions to manage permissions: `shed_group_set_mode`, `shed_group_chown`.

**Weaknesses**:
- The implementation relies on OpenWebUI's Groups API, which might not be available in all deployments.
- The SPEC notes: "Group features are not available (Open WebUI Groups API not found)" as a potential error.
- The tool requires OpenWebUI Groups API to be available, which may not be the case in all environments.

**Rating**: ★★★★☆ (4/5)

## Interaction with OpenWebUI Internals
**Intent and Behavior**: The tool uses OpenWebUI's internal API for file management, download links, and group management.

**Strengths**:
- The `_OpenWebUIBridge` class isolates OpenWebUI API dependencies.
- The SPEC states: "This isolates all direct interactions with Open WebUI's internal modules."
- The implementation handles multiple OpenWebUI API versions gracefully.
- The SPEC notes: "If Open WebUI's internal API changes between versions, only this class needs updating."

**Weaknesses**:
- The tool is vulnerable to breaking if OpenWebUI changes its internal API structure.
- The SPEC acknowledges this risk: "This class isolates all direct interactions with Open WebUI's internal modules. If Open WebUI's internal API changes between versions, only this class needs updating."

**Rating**: ★★★★☆ (4/5)

## LLM Misuse Resistance
**Intent and Behavior**: The tool implements multiple guardrails to prevent LLM misuse, including input validation, command whitelisting, and network restrictions.

**Strengths**:
- Comprehensive input validation for all user-provided paths and arguments.
- The SPEC explicitly states: "No logging. Errors are raised to the calling LLM, not logged to files."
- The tool provides helpful error messages with contextual hints.
- The SPEC notes: "Error messages never expose internal identifiers, UUIDs, or absolute disk paths."

**Weaknesses**:
- The tool relies on the LLM understanding the path rules and workflow patterns.
- The SPEC acknowledges: "The LLM sometimes attempted to call these internal methods directly" - this is prevented by the API separation, but users still need to understand the correct workflow.
- The tool has a learning curve for users unfamiliar with Unix-like file operations.

**Rating**: ★★★★☆ (4/5)

## Final Overall Assessment
**Rating**: ★★★★☆ (4.2/5)

**Justification**: The Fileshed tool demonstrates strong security practices with well-implemented defenses against common attack vectors. The separation of public and internal APIs is particularly well-executed. The primary weaknesses are related to the inherent limitations of the OpenWebUI environment and the single-file architecture, which create some maintenance challenges. The tool is well-designed for its intended use case but has limitations in multi-instance deployments and relies on external API stability.

## Actionable Recommendations
1. Add explicit documentation in `shed_help` about the need for `shed_import` before moving files from Uploads to Storage/Documents.
2. Implement a warning in `shed_parameters` when `network_mode` is set to `all` to emphasize the data exfiltration risk.
3. Add a check in `_OpenWebUIBridge` to detect if OpenWebUI Groups API is unavailable and provide a more helpful error message.
4. Consider adding a configuration option to enable distributed locking for multi-instance deployments (though this would require significant architectural changes).
5. Add a note in the SPEC.md about the reliance on OpenWebUI Groups API availability for group features.
