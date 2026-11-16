#!/usr/bin/env python3
"""Parse the ontology kit and validate example data against its SHACL shapes."""

import os
import subprocess
import sys
from pathlib import Path
from typing import Any

ONTOLOGY_DIR = Path(__file__).resolve().parent.parent
VENV = ONTOLOGY_DIR / ".venv"
OWL_EXPORT = ONTOLOGY_DIR / "medspa-booking.owl"
DEPENDENCIES = ("rdflib==7.6.0", "pyshacl==0.40.2")


def venv_python() -> Path:
    """Return the platform-specific Python executable inside the local venv."""
    executable_dir = "Scripts" if os.name == "nt" else "bin"
    executable_name = "python.exe" if os.name == "nt" else "python3"
    return VENV / executable_dir / executable_name


def in_venv() -> bool:
    """Check whether this process is running in the ontology's isolated venv."""
    return Path(sys.prefix).resolve() == VENV.resolve()


def enter_venv() -> None:
    """Create the isolated environment and re-execute this script inside it."""
    if not VENV.exists():
        subprocess.run([sys.executable, "-m", "venv", str(VENV)], check=True)
        pip_name = "pip.exe" if os.name == "nt" else "pip"
        pip = VENV / ("Scripts" if os.name == "nt" else "bin") / pip_name
        subprocess.run(
            [str(pip), "install", "--quiet", *DEPENDENCIES],
            check=True,
        )
    python = venv_python()
    os.execv(str(python), [str(python), str(Path(__file__).resolve())])


def export_owl(ontology: Any) -> None:
    """Write the merged ontology modules as a portable RDF/XML OWL document."""
    ontology.serialize(destination=str(OWL_EXPORT), format="xml")


def main() -> int:
    """Validate the examples and refresh the RDF/XML OWL export."""
    from pyshacl import validate
    from rdflib import Graph, Namespace
    from rdflib.namespace import RDF

    ontology = Graph()
    shapes = Graph()
    examples = Graph()

    ontology.parse(ONTOLOGY_DIR / "core.ttl", format="turtle")
    for path in sorted((ONTOLOGY_DIR / "extensions").glob("*.ttl")):
        ontology.parse(path, format="turtle")
    for path in sorted((ONTOLOGY_DIR / "shapes").glob("*.ttl")):
        shapes.parse(path, format="turtle")
    for path in sorted((ONTOLOGY_DIR / "examples").glob("*.ttl")):
        examples.parse(path, format="turtle")

    combined = ontology + examples
    conforms, report, _ = validate(
        combined,
        shacl_graph=shapes,
        inference="rdfs",
        abort_on_first=False,
    )
    if not conforms:
        print("Conforms: False")
        if not isinstance(report, Graph):
            print(report)
            return 1
        sh = Namespace("http://www.w3.org/ns/shacl#")
        for result in report.subjects(RDF.type, sh.ValidationResult):
            focus = report.value(result, sh.focusNode)
            path = report.value(result, sh.resultPath)
            message = report.value(result, sh.resultMessage)
            shape = report.value(result, sh.sourceShape)
            print(
                f"- focusNode={focus}; resultPath={path}; "
                f"message={message}; sourceShape={shape}"
            )
        return 1

    export_owl(ontology)
    print(
        "Conforms: True "
        f"(ontology {len(ontology)} triples, "
        f"examples {len(examples)} triples, shapes {len(shapes)} triples)"
    )
    print(f"OWL export: {OWL_EXPORT.relative_to(ONTOLOGY_DIR.parent.parent)}")
    return 0


if __name__ == "__main__":
    if not in_venv():
        enter_venv()
    sys.exit(main())
