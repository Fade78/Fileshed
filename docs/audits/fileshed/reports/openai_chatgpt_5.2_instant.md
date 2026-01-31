## Deep Security, Architecture, and LLM-Safety Audit

**Audited file:** `Fileshed.py`
**Tool version:** **1.0.4** (as declared in file header) 
**Specification reviewed:** `SPEC.md` (design, constraints, threat model) 

This audit evaluates the implementation **in the context of OpenWebUI tool execution**, LLM-driven invocation, admin-only valve configuration, and multi-user/group operation. The report focuses on alignment with the specification and on non-obvious, design-relevant risks.

---

## Axis 1 — Architecture & Separation of Concerns

**Intent & behavior**
The tool enforces a strict two-layer architecture: a public `Tools` surface exposing only `shed_*` methods to the LLM, and a private `_FileshedCore` containing all sensitive logic (filesystem, subprocess, Git, DB). This directly addresses OpenWebUI’s reflection model where all `Tools` methods are LLM-callable.

**Strengths**

* Clean, explicit separation that materially reduces accidental LLM access to dangerous primitives.
* `_OpenWebUIBridge` isolates volatile internal APIs, reducing blast radius of OpenWebUI version drift.
* Centralized `ZoneContext` resolution aligns precisely with the spec’s architecture and avoids scattered zone logic.

**Weaknesses / residual risks**

* The pattern relies on developer discipline: a future contributor could accidentally add non-`shed_` methods to `Tools`.
* No automated guard (e.g., assertion at init time) that only `shed_` methods exist on `Tools`.

**Rating:** ★★★★★

---

## Axis 2 — Trust Boundaries & Execution Model (LLM vs User vs Admin)

**Intent & behavior**
The design assumes:

* The LLM is **untrusted but constrained**.
* End users cannot configure valves.
* Administrators control quotas, network mode, and execution limits.

**Strengths**

* Clear demarcation between admin-only valves and LLM-accessible parameters.
* Security-sensitive features (network, curl, git push) are valve-gated, not prompt-gated.
* Uploads zone is enforced read-only, reducing user-supplied payload execution risks.

**Weaknesses / residual risks**

* The LLM remains a confused-deputy risk: it can be socially engineered to perform destructive but *authorized* actions (e.g., `rm -rf` within zone).
* No concept of “intent confirmation” for high-impact operations; this is an explicit design choice but remains a residual risk.

**Rating:** ★★★★☆

---

## Axis 3 — Filesystem Isolation & Path Safety

**Intent & behavior**
All filesystem access is intended to be chroot-like, confined to zone roots with path normalization and explicit traversal prevention.

**Strengths**

* Central `_resolve_chroot_path` model (per spec) prevents `..` escape and symlink abuse.
* `.git` and internal directories are protected from modification.
* Uploads zone is both read-only and conversation-scoped.

**Weaknesses / residual risks**

* Reliance on correct and consistent use of `_resolve_chroot_path`; any missed call is a latent escape risk.
* Hard-link and symlink creation is removed from whitelists, but existing symlinks inside zones could still be abused if not fully resolved (implementation-dependent).

**Rating:** ★★★★☆

---

## Axis 4 — Command Execution & Argument-Level Safety

**Intent & behavior**
The tool exposes a controlled shell via `shed_exec`, with:

* Explicit command whitelists per zone.
* Global blacklists for interpreters, shells, and privilege escalation.
* Regex-based argument sanitization to block metacharacters and dangerous flags.

**Strengths**

* `subprocess.run` with argument lists (no shell) is a strong baseline.
* Fine-grained handling of edge cases (`jq`, `awk`, pipes) shows deep threat modeling.
* Removal of historically dangerous utilities (`xargs`, `env`, `timeout`) is well-justified.

**Weaknesses / residual risks**

* Regex-based argument filtering is complex and brittle; novel tool behaviors or obscure flags could bypass intent.
* Some whitelisted tools (`sed`, `awk`) are inherently powerful and rely on partial pattern blocking rather than full semantic restriction.

**Rating:** ★★★★☆

---

## Axis 5 — Network Access & Data Exfiltration Controls

**Intent & behavior**
Network access is explicitly tiered (`disabled` / `safe` / `all`) and enforced at the command-argument level for `curl`, `git`, `ffmpeg`, and media tools.

**Strengths**

* Clear distinction between *download-only* and *exfiltration-capable* operations.
* Granular blocking of curl/wget upload flags and ffmpeg output protocols.
* Sensible default: network fully disabled.

**Weaknesses / residual risks**

* Once `network_mode=all` is enabled by an admin, the tool becomes a high-bandwidth exfiltration vector by design.
* URL detection relies on regex matching; protocol smuggling or indirect fetches via allowed tools remain theoretical risks.

**Rating:** ★★★★☆

---

## Axis 6 — Multi-User & Group Permission Model

**Intent & behavior**
Group spaces are Git-versioned, document-only zones with explicit ownership and mode semantics enforced via SQLite.

**Strengths**

* Ownership and mode model (`owner`, `group`, `owner_ro`) is simple, auditable, and well-scoped.
* Permissions are enforced server-side, not via LLM instruction.
* Group membership is verified against OpenWebUI’s Groups API.

**Weaknesses / residual risks**

* SQLite is a single point of integrity; corruption or concurrent write issues could desync permissions.
* No explicit transactional coupling between filesystem operations and permission DB updates.

**Rating:** ★★★★☆

---

## Axis 7 — Concurrency, Locking & Crash Recovery

**Intent & behavior**
The locked-edit workflow introduces explicit file locks, editzones, and recovery tooling.

**Strengths**

* Clear three-phase workflow prevents silent overwrites.
* Lock expiration and `shed_force_unlock` address crash scenarios.
* Editzones are conversation-scoped, reducing cross-chat interference.

**Weaknesses / residual risks**

* Locks are advisory and filesystem-based; unexpected process termination could still leave inconsistent state until maintenance runs.
* No OS-level file locking primitives are used.

**Rating:** ★★★★☆

---

## Axis 8 — SQLite & Structured Data Handling

**Intent & behavior**
SQLite is used both as a user-facing data tool and as an internal permission store.

**Strengths**

* CSV import limits (columns, batch sizes) reduce DoS risk.
* SELECT output limits protect LLM context.
* Optional read-only mode is valve-controlled.

**Weaknesses / residual risks**

* Complex CSV auto-detection increases parsing attack surface.
* User-controlled SQL (even SELECT) can still be computationally expensive.

**Rating:** ★★★★☆

---

## Axis 9 — LLM Misuse Resistance & Prompt Adversariality

**Intent & behavior**
The tool assumes the LLM may behave adversarially or be prompt-injected, and constrains it structurally rather than by instruction.

**Strengths**

* No reliance on “don’t do X” prompting; enforcement is code-level.
* Public API surface is intentionally narrow and explicit.
* Extensive inline warnings and help steer the LLM toward safe workflows.

**Weaknesses / residual risks**

* The LLM can still intentionally perform destructive actions that are *allowed* (e.g., deleting all user files).
* No rate-limiting or anomaly detection on repeated destructive calls.

**Rating:** ★★★★☆

---

## Final Overall Assessment

**Overall rating:** **★★★★☆ (4.5 / 5)**

Weighted toward security and isolation, Fileshed demonstrates **exceptionally strong architectural discipline** for an LLM-invoked tool. The design aligns closely with the specification and shows mature threat modeling, particularly around shell execution and network exfiltration.

Residual risks are largely **intentional and documented trade-offs**, not oversights.

---

## Concrete, Actionable Improvement Recommendations

1. **Add an automated guard on `Tools` initialization** to assert that only `shed_*` methods are publicly exposed.
2. **Harden argument validation** by supplementing regex checks with per-command semantic validation for the riskiest tools (`sed`, `awk`, `ffmpeg`).
3. **Introduce optional admin-level destructive-action confirmation** (e.g., valve-controlled soft-confirmation for recursive deletes).
4. **Improve coupling between permission DB and filesystem operations** (transaction-like rollback on partial failures).
5. **Add lightweight audit logging hooks** for high-impact operations (delete, chmod, group chown) to aid incident review.

This tool is suitable for production deployment in OpenWebUI environments with a strong security posture, provided administrators understand and intentionally configure network and quota valves.

