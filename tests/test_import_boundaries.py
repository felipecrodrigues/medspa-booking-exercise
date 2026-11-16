import ast
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]
PACKAGE = ROOT / "src" / "medspa_booking"


def imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            prefix = "." * node.level
            modules.add(prefix + (node.module or ""))
    return modules


def test_appointment_rules_and_status_do_not_import_web_or_persistence() -> None:
    for relative_path in ("appointments/rules.py", "appointments/status.py"):
        modules = imported_modules(PACKAGE / relative_path)

        assert not {"fastapi", "sqlalchemy"}.intersection(
            module.split(".", maxsplit=1)[0].lstrip(".") for module in modules
        )


def test_feature_schemas_do_not_import_orm_models() -> None:
    for relative_path in ("services/schemas.py", "appointments/schemas.py"):
        modules = imported_modules(PACKAGE / relative_path)

        assert not any(
            module.rstrip(".").endswith("models") or ".models." in module
            for module in modules
        )


def test_feature_operations_do_not_import_pydantic_schemas() -> None:
    for relative_path in (
        "services/operations.py",
        "appointments/operations.py",
    ):
        modules = imported_modules(PACKAGE / relative_path)

        assert not any(module.endswith(".schemas") for module in modules)


def test_database_modules_do_not_import_fastapi() -> None:
    for path in (PACKAGE / "db").glob("*.py"):
        modules = imported_modules(path)

        assert not any(
            module.split(".", maxsplit=1)[0].lstrip(".") == "fastapi"
            for module in modules
        )


@pytest.mark.parametrize(
    "module_name",
    [
        "medspa_booking.db.seed",
        "medspa_booking.main",
        "medspa_booking.db.schema_ddl",
    ],
)
def test_entrypoint_imports_register_all_orm_mappers_in_fresh_process(
    module_name: str,
) -> None:
    script = (
        "import importlib, sys\n"
        "from sqlalchemy.orm import configure_mappers\n"
        "importlib.import_module(sys.argv[1])\n"
        "configure_mappers()\n"
    )
    environment = os.environ.copy()
    source_path = str(ROOT / "src")
    environment["PYTHONPATH"] = os.pathsep.join(
        path for path in (source_path, environment.get("PYTHONPATH")) if path
    )

    result = subprocess.run(
        [sys.executable, "-c", script, module_name],
        cwd=ROOT,
        env=environment,
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert result.returncode == 0, result.stderr
