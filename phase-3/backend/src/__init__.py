"""Phase III Backend - AI Chatbot for conversational todo management.

Import strategy: Phase II shared code (database, auth, models) is imported via
package aliasing. The phase-2/backend/src directory is added to sys.path as
'phase2_backend', allowing imports like:

    from phase2_backend.database import engine, get_session
    from phase2_backend.api.dependencies import ValidatedUser
    from phase2_backend.models.task import Task, TaskCreate

Phase II internal imports (e.g. `from src.utils.logging import ...`) are handled
by a custom import hook that falls back to Phase II's src/ for submodules not
found in Phase III's src/.
"""

import os
import sys
import importlib
import importlib.util
from pathlib import Path

# Resolve Phase II backend source directory
_phase2_backend_src = Path(__file__).resolve().parent.parent.parent.parent / "phase-2" / "backend" / "src"
_phase3_backend_src = Path(__file__).resolve().parent

if _phase2_backend_src.exists():
    _phase2_str = str(_phase2_backend_src)
    if _phase2_str not in sys.path:
        sys.path.insert(0, _phase2_str)


class _Phase2FallbackFinder:
    """Meta path finder (PEP 451) that resolves `src.*` imports from Phase II
    when the submodule doesn't exist in Phase III's src/ directory.

    This handles Phase II code that does `from src.utils.logging import ...`
    when running inside Phase III's process where `src` is Phase III's package.
    """

    def __init__(self, phase2_src: Path, phase3_src: Path):
        self._phase2_src = phase2_src
        self._phase3_src = phase3_src

    def find_spec(self, fullname: str, path=None, target=None):
        if not fullname.startswith("src."):
            return None
        # Only intercept if the submodule doesn't exist in Phase III
        rel = fullname.replace("src.", "", 1).replace(".", os.sep)
        phase3_pkg = self._phase3_src / rel
        phase3_mod = self._phase3_src / (rel + ".py")
        if phase3_pkg.is_dir() or phase3_mod.is_file():
            return None  # Let normal import handle Phase III modules

        # Check if it exists in Phase II
        phase2_pkg = self._phase2_src / rel
        phase2_mod = self._phase2_src / (rel + ".py")

        if phase2_pkg.is_dir():
            init_file = phase2_pkg / "__init__.py"
            if init_file.exists():
                return importlib.util.spec_from_file_location(
                    fullname, init_file,
                    submodule_search_locations=[str(phase2_pkg)],
                )
            else:
                return importlib.util.spec_from_file_location(
                    fullname, None,
                    submodule_search_locations=[str(phase2_pkg)],
                )
        elif phase2_mod.is_file():
            return importlib.util.spec_from_file_location(fullname, phase2_mod)

        return None


if _phase2_backend_src.exists():
    # Install the fallback finder (only once)
    if not any(isinstance(f, _Phase2FallbackFinder) for f in sys.meta_path):
        sys.meta_path.insert(0, _Phase2FallbackFinder(_phase2_backend_src, _phase3_backend_src))

    # Register phase2_backend as a package pointing to phase-2/backend/src
    _phase2_init = _phase2_backend_src / "__init__.py"
    if "phase2_backend" not in sys.modules:
        spec = importlib.util.spec_from_file_location(
            "phase2_backend",
            _phase2_backend_src / "__init__.py" if _phase2_init.exists() else None,
            submodule_search_locations=[_phase2_str],
        )
        if spec:
            phase2_mod = importlib.util.module_from_spec(spec)
            sys.modules["phase2_backend"] = phase2_mod
            phase2_mod.__path__ = [_phase2_str]

# Also register phase3_backend alias for Phase III imports within tests
_phase3_str = str(_phase3_backend_src)
if _phase3_str not in sys.path:
    sys.path.insert(0, _phase3_str)

if "phase3_backend" not in sys.modules:
    spec = importlib.util.spec_from_file_location(
        "phase3_backend",
        _phase3_backend_src / "__init__.py",
        submodule_search_locations=[_phase3_str],
    )
    if spec:
        phase3_mod = importlib.util.module_from_spec(spec)
        sys.modules["phase3_backend"] = phase3_mod
        phase3_mod.__path__ = [_phase3_str]
