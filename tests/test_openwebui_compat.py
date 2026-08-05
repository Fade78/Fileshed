#!/usr/bin/env python3
"""
Detects incompatibilities between Fileshed and Open WebUI's internal models API.

Open WebUI 0.9.0 turned its models layer (Files, Groups, ...) into coroutine
functions. Calling one of them without awaiting returns a coroutine object: the
database operation silently never happens, and the coroutine is truthy, so
`if not result:` guards do not catch it. That is what broke download links with
a misleading "We could not find what you're looking for :/" at download time
(issue #8) -- the bug is invisible at creation time, which is exactly why it
needs a test.

This file is a self-contained runner. No test framework, no network:

    python3 tests/test_openwebui_compat.py

It runs four independent checks:

  A. STATIC    Every Files/Groups call in Fileshed.py goes through _owui_call().
               This is the guard for code written later: a direct call added in
               a future patch fails here even if no runtime path exercises it.

  B. ASYNC     Fileshed driven against a fake Open WebUI 0.9+ API. Every
               coroutine the fake hands out is tracked, and the check fails if
               any was left un-awaited. Also asserts the database side effects
               actually happened, which is what issue #8 got wrong.

  C. SYNC      The same scenario against a fake pre-0.9 synchronous API, so the
               fix cannot regress older deployments.

  D. LIVE      When `open_webui` is importable (i.e. run inside a real install),
               checks that every symbol Fileshed depends on still exists, and
               that the fakes used by checks B and C match the real signatures.
               Skipped otherwise -- that is the normal case outside Open WebUI.

Exit code is 0 when everything passes, 1 otherwise.
"""

import ast
import asyncio
import importlib.util
import inspect
import json
import shutil
import sys
import tempfile
import time
import types
from pathlib import Path

FILESHED_PATH = Path(__file__).resolve().parent.parent / "Fileshed.py"
if len(sys.argv) > 1:  # allow checking a candidate file: ... compat.py path/to/Fileshed.py
    FILESHED_PATH = Path(sys.argv[1]).resolve()

# Fileshed relies on these Open WebUI symbols. Check D verifies they still exist.
REQUIRED_FILES_METHODS = (
    "insert_new_file",
    "get_file_by_id",
    "get_files_by_user_id",
    "delete_file_by_id",
)
REQUIRED_GROUPS_METHODS = (
    "get_all_groups",
    "get_groups_by_member_id",
    "get_group_by_id",
    "get_group_user_ids_by_id",
    "get_group_member_count_by_id",
)
REQUIRED_FILEFORM_FIELDS = ("id", "filename", "path", "data", "meta")

USER = {"id": "aaaaaaaa-1111-2222-3333-444444444444", "role": "user", "name": "tester"}
STRANGER = {"id": "bbbbbbbb-1111-2222-3333-444444444444", "role": "user", "name": "stranger"}
META = {"chat_id": "cccccccc-1111-2222-3333-444444444444"}
GROUP_ID = "11111111-2222-3333-4444-555555555555"
GROUP_NAME = "team"


# =============================================================================
# Reporting
# =============================================================================

class Report:
    def __init__(self):
        self.failures = []
        self.skipped = []

    def section(self, title):
        print(f"\n--- {title} ---")

    def check(self, label, ok, detail=""):
        print(f"  {'ok  ' if ok else 'FAIL'}  {label}")
        if not ok:
            if detail:
                for line in str(detail).splitlines():
                    print(f"          {line}")
            self.failures.append(label)

    def skip(self, label, reason):
        print(f"  skip  {label} ({reason})")
        self.skipped.append(label)


# =============================================================================
# Optional dependency: pydantic
# =============================================================================

def ensure_pydantic():
    """
    Fileshed imports pydantic, which Open WebUI always provides. When running
    these checks outside an Open WebUI environment it may be missing, so fall
    back to a stand-in covering the little Fileshed uses: BaseModel subclasses
    whose annotated attributes are declared with Field(default=...).
    """
    try:
        import pydantic  # noqa: F401
        return "real"
    except ImportError:
        pass

    stub = types.ModuleType("pydantic")

    class _FieldInfo:
        def __init__(self, default=None, description=None, **kw):
            self.default = default
            self.description = description

    def Field(default=None, description=None, **kw):  # noqa: N802
        return _FieldInfo(default=default, description=description, **kw)

    class BaseModel:
        def __init__(self, **kwargs):
            for name in getattr(type(self), "__annotations__", {}):
                value = getattr(type(self), name, None)
                if isinstance(value, _FieldInfo):
                    value = value.default
                setattr(self, name, value)
            for key, value in kwargs.items():
                setattr(self, key, value)

        def model_dump(self):
            return {n: getattr(self, n) for n in getattr(type(self), "__annotations__", {})}

    stub.BaseModel = BaseModel
    stub.Field = Field
    sys.modules["pydantic"] = stub
    return "stub"


def ensure_cryptography_usable():
    """
    Fileshed already degrades gracefully when cryptography is absent, but a
    broken build can fail at import time with something other than ImportError
    (a panic from the Rust bindings, for instance), which Fileshed's
    `except ImportError` does not catch. Probe it once and hide it if unusable:
    encryption is out of scope for this compatibility check.
    """
    try:
        import cryptography.hazmat.primitives.ciphers.aead  # noqa: F401
        return "available"
    except BaseException:
        for name in list(sys.modules):
            if name == "cryptography" or name.startswith("cryptography."):
                del sys.modules[name]
        sys.modules["cryptography"] = types.ModuleType("cryptography")
        return "unusable, masked for this run"


# =============================================================================
# Fake Open WebUI
# =============================================================================

class AwaitTracker:
    """
    Records every coroutine the fake async API hands out and whether it was
    awaited. An un-awaited coroutine is the exact failure mode of issue #8: no
    exception, no database write, and a truthy return value.
    """

    def __init__(self):
        self.records = []

    def wrap(self, name, coro):
        record = {"name": name, "awaited": False}
        self.records.append(record)

        async def watcher():
            record["awaited"] = True
            return await coro

        return watcher()

    def never_awaited(self):
        return sorted({r["name"] for r in self.records if not r["awaited"]})


class FileForm:
    """
    Mirrors open_webui.models.files.FileForm: required fields are rejected when
    missing and unknown fields are rejected outright, so a Fileshed change that
    stops matching the real form fails here.
    """

    _REQUIRED = ("id", "filename", "path")
    _OPTIONAL = ("hash", "data", "meta")
    # Mirrors pydantic's introspection surface, so verify_api_symbols() can
    # examine this class the same way it examines the real one.
    model_fields = {name: None for name in _REQUIRED + _OPTIONAL}

    def __init__(self, **kwargs):
        unknown = set(kwargs) - set(self._REQUIRED) - set(self._OPTIONAL)
        if unknown:
            raise TypeError(f"FileForm got unexpected field(s): {sorted(unknown)}")
        missing = [f for f in self._REQUIRED if kwargs.get(f) is None]
        if missing:
            raise TypeError(f"FileForm missing required field(s): {missing}")
        self.id = kwargs["id"]
        self.filename = kwargs["filename"]
        self.path = kwargs["path"]
        self.hash = kwargs.get("hash")
        self.data = kwargs.get("data") or {}
        self.meta = kwargs.get("meta") or {}


class FileModel:
    def __init__(self, user_id, form):
        now = int(time.time())
        self.id = form.id
        self.user_id = user_id
        self.hash = form.hash
        self.filename = form.filename
        self.path = form.path
        self.data = form.data
        self.meta = form.meta
        self.created_at = now
        self.updated_at = now


class GroupModel:
    def __init__(self, id, user_id, name, description="", member_ids=()):
        now = int(time.time())
        self.id = id
        self.user_id = user_id
        self.name = name
        self.description = description
        self.data = None
        self.meta = None
        self.permissions = None
        self.created_at = now
        self.updated_at = now
        # Membership lives in a separate table upstream; kept here only to
        # answer get_group_user_ids_by_id().
        self._member_ids = list(member_ids)


class FakeStore:
    """Backing state shared by the sync and async facades."""

    def __init__(self):
        self.files = {}
        self.groups = {}

    # -- files --
    def insert_new_file(self, user_id, form_data):
        row = FileModel(user_id, form_data)
        self.files[row.id] = row
        return row

    def get_file_by_id(self, id):
        return self.files.get(id)

    def get_files_by_user_id(self, user_id):
        return [f for f in self.files.values() if f.user_id == user_id]

    def delete_file_by_id(self, id):
        return self.files.pop(id, None) is not None

    # -- groups --
    def get_all_groups(self):
        return list(self.groups.values())

    def get_groups_by_member_id(self, user_id):
        return [g for g in self.groups.values() if user_id in g._member_ids]

    def get_group_by_id(self, id):
        return self.groups.get(id)

    def get_group_user_ids_by_id(self, id):
        group = self.groups.get(id)
        return list(group._member_ids) if group else []

    def get_group_member_count_by_id(self, id):
        return len(self.get_group_user_ids_by_id(id))


class SyncFiles:
    """Pre-0.9 Open WebUI: plain methods, real signatures."""

    def __init__(self, store):
        self._store = store

    def insert_new_file(self, user_id, form_data, db=None):
        return self._store.insert_new_file(user_id, form_data)

    def get_file_by_id(self, id, db=None):
        return self._store.get_file_by_id(id)

    def get_files_by_user_id(self, user_id, db=None):
        return self._store.get_files_by_user_id(user_id)

    def delete_file_by_id(self, id, db=None):
        return self._store.delete_file_by_id(id)


class SyncGroups:
    def __init__(self, store):
        self._store = store

    def get_all_groups(self, db=None):
        return self._store.get_all_groups()

    def get_groups_by_member_id(self, user_id, db=None):
        return self._store.get_groups_by_member_id(user_id)

    def get_group_by_id(self, id, db=None):
        return self._store.get_group_by_id(id)

    def get_group_user_ids_by_id(self, id, db=None):
        return self._store.get_group_user_ids_by_id(id)

    def get_group_member_count_by_id(self, id, db=None):
        return self._store.get_group_member_count_by_id(id)


def _async_facade(cls_name, sync_obj, method_names, tracker):
    """
    Build a 0.9+ style facade: same method names and signatures, but each one
    returns a tracked coroutine instead of a value.
    """
    namespace = {}
    for method_name in method_names:
        def make(method_name):
            target = getattr(sync_obj, method_name)

            def call(*args, **kwargs):
                async def body():
                    return target(*args, **kwargs)
                return tracker.wrap(f"{cls_name}.{method_name}", body())

            call.__name__ = method_name
            call.__signature__ = inspect.signature(target)
            # `call` must stay a plain function: it has to register the
            # coroutine at call time, before anyone decides to await it.
            # inspect.iscoroutinefunction() therefore says no, so flag it.
            call.__fileshed_returns_coroutine__ = True
            return call
        namespace[method_name] = staticmethod(make(method_name))
    return type(cls_name, (), namespace)()


def install_fake_open_webui(mode, data_dir, tracker):
    """
    Put a fake `open_webui` package in sys.modules.

    :param mode: "async" (0.9+) or "sync" (<= 0.8.x)
    :return: (store, upload_dir)
    """
    for name in list(sys.modules):
        if name == "open_webui" or name.startswith("open_webui."):
            del sys.modules[name]

    store = FakeStore()
    sync_files = SyncFiles(store)
    sync_groups = SyncGroups(store)

    if mode == "async":
        files_obj = _async_facade("Files", sync_files, REQUIRED_FILES_METHODS, tracker)
        groups_obj = _async_facade("Groups", sync_groups, REQUIRED_GROUPS_METHODS, tracker)
        version = "0.11.0"
    else:
        files_obj, groups_obj = sync_files, sync_groups
        version = "0.8.12"

    upload_dir = Path(data_dir) / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)

    pkg = types.ModuleType("open_webui")
    pkg.__path__ = []
    pkg.__version__ = version

    models = types.ModuleType("open_webui.models")
    models.__path__ = []

    files_mod = types.ModuleType("open_webui.models.files")
    files_mod.Files = files_obj
    files_mod.FileForm = FileForm

    groups_mod = types.ModuleType("open_webui.models.groups")
    groups_mod.Groups = groups_obj

    config_mod = types.ModuleType("open_webui.config")
    config_mod.UPLOAD_DIR = upload_dir

    sys.modules.update({
        "open_webui": pkg,
        "open_webui.models": models,
        "open_webui.models.files": files_mod,
        "open_webui.models.groups": groups_mod,
        "open_webui.config": config_mod,
    })
    return store, upload_dir


def load_fileshed():
    """Import Fileshed.py fresh, so it binds to the fake currently installed."""
    sys.modules.pop("fileshed_under_test", None)
    spec = importlib.util.spec_from_file_location("fileshed_under_test", FILESHED_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules["fileshed_under_test"] = module
    spec.loader.exec_module(module)
    return module


# =============================================================================
# CHECK A -- static: no Open WebUI models call escapes _owui_call()
# =============================================================================

def check_static(report):
    report.section("A. Static: every Open WebUI models call goes through _owui_call()")

    tree = ast.parse(FILESHED_PATH.read_text())

    # Calls passed as an argument to _owui_call(...) are the compliant ones.
    wrapped = set()
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id == "_owui_call"):
            for arg in node.args:
                if isinstance(arg, ast.Call):
                    wrapped.add(id(arg))

    def is_models_call(node):
        """`Groups.xxx(...)` or `<something>._files_class.xxx(...)`."""
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)):
            return False
        owner = node.func.value
        if isinstance(owner, ast.Name) and owner.id in ("Groups", "Files"):
            return True
        return isinstance(owner, ast.Attribute) and owner.attr == "_files_class"

    offenders = [
        f"line {node.lineno}: {ast.unparse(node.func)}(...)"
        for node in ast.walk(tree)
        if is_models_call(node) and id(node) not in wrapped
    ]
    report.check(
        "no direct Files/Groups call bypasses _owui_call()",
        not offenders,
        "\n".join(offenders) + "\n"
        "Wrap it: await _owui_call(Groups.get_group_by_id(gid))" if offenders else "",
    )

    # _owui_call must actually await; a helper that just returns its argument
    # would make check A pass while reintroducing the bug.
    helper = next(
        (n for n in ast.walk(tree)
         if isinstance(n, ast.AsyncFunctionDef) and n.name == "_owui_call"),
        None,
    )
    report.check("_owui_call() exists and is a coroutine function", helper is not None)
    if helper is not None:
        report.check(
            "_owui_call() awaits awaitable results",
            any(isinstance(n, ast.Await) for n in ast.walk(helper)),
            "_owui_call() must await its argument when it is awaitable",
        )

    # Every call to a coroutine method defined in Fileshed must be awaited.
    async_methods = {
        n.name for n in ast.walk(tree) if isinstance(n, ast.AsyncFunctionDef)
    }
    awaited = {
        id(n.value) for n in ast.walk(tree)
        if isinstance(n, ast.Await) and isinstance(n.value, ast.Call)
    }
    unawaited = [
        f"line {node.lineno}: {ast.unparse(node.func)}(...)"
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
        and node.func.attr in async_methods
        and id(node) not in awaited
        and id(node) not in wrapped
    ]
    report.check(
        "no un-awaited call to a Fileshed coroutine method",
        not unawaited,
        "\n".join(unawaited),
    )


# =============================================================================
# CHECKS B / C -- runtime, against each API generation
# =============================================================================

async def run_scenario(report, mode, base_dir, data_dir, tracker):
    store, upload_dir = install_fake_open_webui(mode, data_dir, tracker)
    store.groups[GROUP_ID] = GroupModel(
        GROUP_ID, user_id=USER["id"], name=GROUP_NAME,
        description="Test group", member_ids=[USER["id"]],
    )

    fileshed = load_fileshed()
    report.check("Groups API detected", fileshed.GROUPS_AVAILABLE)

    tools = fileshed.Tools()
    tools.valves.storage_base_path = str(base_dir)
    ctx = dict(__user__=USER, __metadata__=META)

    async def call(coro):
        return json.loads(await coro)

    # -- download links, i.e. the path reported in issue #8 -----------------
    result = await call(tools.shed_patch_text(
        zone="storage", path="report.txt", content="hello", **ctx))
    report.check("seed a file in Storage", result.get("success"), result.get("message"))

    result = await call(tools.shed_link_create(zone="storage", path="report.txt", **ctx))
    report.check("shed_link_create() reports success", result.get("success"), result.get("message"))
    file_id = (result.get("data") or {}).get("file_id")

    # The heart of issue #8: creation claimed success while the row was never
    # written, so the link 404ed later with ERROR_MESSAGES.NOT_FOUND.
    report.check(
        "shed_link_create() actually wrote the database row",
        file_id in store.files,
        f"reported file_id={file_id}, rows in database={list(store.files)}\n"
        "A link was handed out for a row that does not exist: downloading it "
        'returns {"detail":"We could not find what you\'re looking for :/"}',
    )

    if file_id in store.files:
        row = store.files[file_id]
        report.check("stored path exists on disk", Path(row.path).is_file(), row.path)
        report.check(
            "file written under Open WebUI's resolved UPLOAD_DIR",
            Path(row.path).parent == upload_dir,
            f"{Path(row.path).parent} != {upload_dir}",
        )
        report.check("row is owned by the calling user", row.user_id == USER["id"], row.user_id)
        report.check(
            "row is marked as a Fileshed link",
            (row.meta or {}).get("data", {}).get("fileshed_link") is True,
            json.dumps(row.meta),
        )

    result = await call(tools.shed_link_list(__user__=USER))
    report.check("shed_link_list() succeeds", result.get("success"), result.get("message"))
    report.check(
        "shed_link_list() returns the link",
        (result.get("data") or {}).get("count") == 1,
        json.dumps(result.get("data")),
    )

    existed_before_delete = file_id in store.files
    result = await call(tools.shed_link_delete(file_id=file_id, __user__=USER))
    report.check("shed_link_delete() succeeds", result.get("success"), result.get("message"))
    # Requires the row to have existed first, so this cannot pass just because
    # creation never wrote anything.
    report.check(
        "shed_link_delete() removed the database row",
        existed_before_delete and file_id not in store.files,
        "row still present after delete" if existed_before_delete
        else "no row existed to delete (see the create check above)",
    )

    # -- groups -------------------------------------------------------------
    result = await call(tools.shed_group_list(__user__=USER))
    report.check("shed_group_list() succeeds", result.get("success"), result.get("message"))
    groups = (result.get("data") or {}).get("groups") or []
    report.check("shed_group_list() finds the group", len(groups) == 1, json.dumps(groups))
    report.check(
        "shed_group_list() resolves the member count",
        bool(groups) and groups[0].get("member_count") == 1,
        json.dumps(groups),
    )

    result = await call(tools.shed_patch_text(
        zone="group", group=GROUP_NAME, path="shared.txt", content="group content", **ctx))
    report.check("write into the group zone by name", result.get("success"), result.get("message"))

    result = await call(tools.shed_read(
        zone="group", group=GROUP_NAME, path="shared.txt", **ctx))
    report.check("read back from the group zone", result.get("success"), result.get("message"))

    result = await call(tools.shed_group_info(group=GROUP_NAME, __user__=USER))
    report.check("shed_group_info() succeeds", result.get("success"), result.get("message"))
    report.check(
        "shed_group_info() lists the members",
        (result.get("data") or {}).get("member_count") == 1,
        json.dumps((result.get("data") or {}).get("members")),
    )

    # Access control must still deny; a coroutine treated as a value made
    # _check_group_access() accept every group, so these two matter.
    result = await call(tools.shed_read(
        zone="group", group=GROUP_NAME, path="shared.txt",
        __user__=STRANGER, __metadata__=META))
    report.check("a non-member is denied", not result.get("success"), result.get("message"))

    result = await call(tools.shed_read(
        zone="group", group="does-not-exist", path="shared.txt", **ctx))
    report.check("an unknown group is rejected", not result.get("success"), result.get("message"))

    # -- diagnostics --------------------------------------------------------
    result = await call(tools.shed_parameters(__user__=USER))
    info = (result.get("data") or {}).get("_info", {})
    report.check(
        "shed_parameters() reports the Open WebUI version",
        info.get("openwebui_version") == ("0.11.0" if mode == "async" else "0.8.12"),
        json.dumps(info),
    )


async def check_runtime(report, mode, title):
    report.section(title)
    tracker = AwaitTracker()
    tmp = Path(tempfile.mkdtemp(prefix=f"fileshed-{mode}-"))
    try:
        await run_scenario(report, mode, tmp / "fileshed", tmp / "openwebui", tracker)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    if mode == "async":
        report.check(
            "at least one models call was made",
            bool(tracker.records),
            "The fake API was never called; the scenario is not exercising it.",
        )
        never_awaited = tracker.never_awaited()
        report.check(
            "every Open WebUI models call was awaited",
            not never_awaited,
            "un-awaited: " + ", ".join(never_awaited) + "\n"
            "These calls returned a coroutine that was dropped: the database "
            "operation never ran and the truthy coroutine slipped past any "
            "`if not result:` guard. Route them through await _owui_call(...)."
            if never_awaited else "",
        )


# =============================================================================
# CHECK D -- live: the installed Open WebUI still provides what Fileshed uses
# =============================================================================

def verify_api_symbols(report, files_obj, groups_obj, file_form_cls):
    """
    Check an Open WebUI models API -- real or fake -- against what Fileshed
    needs: every method present, and a signature the fakes used by checks B
    and C can stand in for. Reports whether each method is sync or async;
    Fileshed handles both, so neither is a failure on its own.
    """
    for real_owner, owner_name, methods, fake_owner in (
        (files_obj, "Files", REQUIRED_FILES_METHODS, SyncFiles(FakeStore())),
        (groups_obj, "Groups", REQUIRED_GROUPS_METHODS, SyncGroups(FakeStore())),
    ):
        for method_name in methods:
            real = getattr(real_owner, method_name, None)
            report.check(f"{owner_name}.{method_name}() exists", real is not None)
            if real is None:
                continue

            is_async = (inspect.iscoroutinefunction(real)
                        or getattr(real, "__fileshed_returns_coroutine__", False))
            print(f"  info  {owner_name}.{method_name}() is {'async' if is_async else 'sync'}")

            # The fakes driving checks B and C must accept everything the real
            # API accepts, otherwise those checks prove nothing.
            try:
                real_params = set(inspect.signature(real).parameters)
                fake_params = set(inspect.signature(getattr(fake_owner, method_name)).parameters)
            except (TypeError, ValueError) as exc:
                report.skip(f"fake {owner_name}.{method_name}() signature", str(exc))
                continue

            report.check(
                f"fake {owner_name}.{method_name}() covers the real signature",
                real_params <= fake_params,
                f"real accepts {sorted(real_params)}, fake accepts {sorted(fake_params)}\n"
                "Update the fakes in this file to match Open WebUI.",
            )

    fields = set(getattr(file_form_cls, "model_fields", None)
                 or getattr(file_form_cls, "__annotations__", None)
                 or ())
    if fields:
        missing = [f for f in REQUIRED_FILEFORM_FIELDS if f not in fields]
        report.check(
            "FileForm still accepts the fields Fileshed sets",
            not missing,
            f"missing from FileForm: {missing} (it has {sorted(fields)})",
        )
    else:
        report.skip("FileForm field check", "fields not introspectable")


def check_live(report):
    report.section("D. Live: symbols in the installed Open WebUI")

    for name in list(sys.modules):
        if name == "open_webui" or name.startswith("open_webui."):
            del sys.modules[name]

    try:
        from open_webui.models.files import FileForm as RealFileForm, Files as RealFiles
        from open_webui.models.groups import Groups as RealGroups
    except ImportError as exc:
        report.skip("live Open WebUI symbol check", f"open_webui not importable: {exc}")
        # Outside a real install there is nothing to introspect, so exercise the
        # same logic against the 0.9+ fake. That keeps this code from rotting
        # unnoticed until someone finally runs it inside Open WebUI.
        print("  info  self-checking the symbol logic against the 0.9+ fake instead")
        tracker = AwaitTracker()
        store = FakeStore()
        verify_api_symbols(
            report,
            _async_facade("Files", SyncFiles(store), REQUIRED_FILES_METHODS, tracker),
            _async_facade("Groups", SyncGroups(store), REQUIRED_GROUPS_METHODS, tracker),
            FileForm,
        )
        return

    try:
        from open_webui import __version__ as version
    except ImportError:
        version = "unknown"
    print(f"  info  Open WebUI version: {version}")

    try:
        from open_webui.config import UPLOAD_DIR  # noqa: F401
        report.check("open_webui.config.UPLOAD_DIR is available", True)
    except ImportError as exc:
        report.check("open_webui.config.UPLOAD_DIR is available", False, str(exc))

    verify_api_symbols(report, RealFiles, RealGroups, RealFileForm)


# =============================================================================

async def main():
    print(f"Fileshed under test: {FILESHED_PATH}")
    print(f"pydantic: {ensure_pydantic()}")
    print(f"cryptography: {ensure_cryptography_usable()}")

    report = Report()
    check_static(report)
    await check_runtime(report, "async", "B. Runtime against Open WebUI 0.9+ (async models API)")
    await check_runtime(report, "sync", "C. Runtime against Open WebUI <= 0.8.x (sync models API)")
    check_live(report)

    print()
    if report.failures:
        print(f"{len(report.failures)} FAILED:")
        for failure in report.failures:
            print(f"  - {failure}")
        return 1
    suffix = f" ({len(report.skipped)} skipped)" if report.skipped else ""
    print(f"All checks passed{suffix}.")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
