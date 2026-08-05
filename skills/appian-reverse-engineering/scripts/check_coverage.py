#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_coverage.py — Gate de cobertura documental de la reingenieria inversa.

Uso:
  python check_coverage.py <ruta_salida> [--mode onboarding|rebuild]

`<ruta_salida>` es la carpeta `_doc_generada` (tambien se acepta la carpeta
que la contiene). Lee `_intermedio/inventory.json`, escanea todos los `.md`
de la salida buscando cada objeto por su nombre tecnico (con limites de
palabra) o, como fallback, por su UUID, y escribe
`_intermedio/coverage.json` con el resultado.

Exit codes:
  0  cobertura requerida al 100%
  1  hay objetos requeridos sin documentar (el gate NO se cumple)
  2  error de uso / IO (ruta invalida, inventory.json ausente o corrupto)

Reglas (plan 2026-08-04-reverse-engineering-rebuild-spec, Task 4):
- `--mode onboarding`: exige 100% de recordType, cdt, processModel,
  integration, webApi, group y dataStore. Los demas tipos (interfaces,
  rules, ...) solo se reportan (informativo).
- `--mode rebuild`: exige ademas interface, expressionRule, decision,
  constant y site. Cada uno debe aparecer en `10-especificacion/` (sin
  contar `trazabilidad.md`) o estar en `trazabilidad.md` marcado
  `DESCARTADO: {motivo}` con motivo no vacio.
  Nota de diseno: la fila `DOCUMENTADO` de trazabilidad.md no cuenta como
  ficha — la matriz lista TODOS los objetos por contrato, asi que contarla
  haria el gate trivialmente verde.

Solo stdlib de Python 3.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

# Tipos cuya cobertura al 100% exige el modo onboarding (los que promete
# response-format.md MAS los data stores).
ONBOARDING_REQUIRED = (
    "recordType",
    "cdt",
    "processModel",
    "integration",
    "webApi",
    "group",
    "dataStore",
)

# Tipos que el modo rebuild exige ADEMAS, con ficha en 10-especificacion/.
REBUILD_EXTRA = (
    "interface",
    "expressionRule",
    "decision",
    "constant",
    "site",
)

# En modo `rebuild` TODOS los tipos de REBUILD_EXTRA necesitan FICHA PROPIA
# (fichero dedicado o cabecera Markdown): una mencion de pasada no basta, porque
# las fichas se citan entre si (el indice las lista, una pantalla nombra las
# reglas que invoca) y eso convertia el gate en un tramite.
#
# Donde vive la ficha de cada tipo:
#   interface      -> 10-especificacion/pantallas/{interfaz}.md
#   expressionRule -> ### rule!X     en reglas-catalogo.md
#   decision       -> ### decision!X en reglas-catalogo.md
#   constant       -> ### cons!X     en reglas-catalogo.md  (seccion Constantes)
#   site           -> ## site!X      en navegacion.md
SHEET_REQUIRED = REBUILD_EXTRA

SPEC_DIR_NAME = "10-especificacion"
TRAZA_FILE_NAME = "trazabilidad.md"

# INVENTARIO.md lista TODOS los objetos del export por contrato (es un catalogo,
# no documentacion). Si contara como evidencia, cualquier objeto estaria siempre
# "documentado" y el gate no podria fallar nunca. Se excluye por el mismo motivo
# que trazabilidad.md en el modo rebuild.
CATALOG_FILE_NAME = "INVENTARIO.md"

# DESCARTADO: {motivo} — el motivo es obligatorio. En una fila de tabla md el
# motivo vive en la celda: termina en `|` o fin de linea, y no vale que sea
# vacio o solo guiones.
DISCARDED_RE = re.compile(r"DESCARTADO\s*:\s*([^|\n]*)")


def has_discard_reason(line: str) -> bool:
    m = DISCARDED_RE.search(line)
    if not m:
        return False
    motivo = m.group(1).strip()
    return bool(motivo.strip("-—– \t"))


def word_pattern(token: str) -> re.Pattern:
    """Patron de aparicion exacta: sin letras/digitos/_ pegados a los lados."""
    return re.compile(r"(?<![A-Za-z0-9_])" + re.escape(token) + r"(?![A-Za-z0-9_])")


def resolve_doc_dir(target: Path) -> Path | None:
    """Admite la propia _doc_generada o la carpeta que la contiene."""
    for cand in (target, target / "_doc_generada"):
        if (cand / "_intermedio" / "inventory.json").is_file():
            return cand
    return None


def flatten_objects(inventory: dict[str, Any]) -> list[dict[str, Any]]:
    """Normaliza `objects` (dict tipo->lista, forma del parser, o lista plana).

    Descarta entradas sin `type` o sin `name` (p. ej. los ICF, que no son
    objetos de diseno documentables).
    """
    raw = inventory.get("objects", {})
    flat: list[dict[str, Any]] = []
    if isinstance(raw, dict):
        for lst in raw.values():
            if isinstance(lst, list):
                flat.extend(x for x in lst if isinstance(x, dict))
    elif isinstance(raw, list):
        flat = [x for x in raw if isinstance(x, dict)]
    return [o for o in flat if o.get("type") and o.get("name")]


def read_markdown(doc_dir: Path) -> list[tuple[Path, str]]:
    docs = []
    for p in sorted(doc_dir.rglob("*.md")):
        try:
            docs.append((p, p.read_text(encoding="utf-8", errors="replace")))
        except OSError:
            continue
    return docs


def in_spec_dir(path: Path, doc_dir: Path) -> bool:
    try:
        rel = path.relative_to(doc_dir)
    except ValueError:
        return False
    return SPEC_DIR_NAME in rel.parts


def found_in(blob: str, name: str | None, uuid: str | None) -> bool:
    if name and word_pattern(name).search(blob):
        return True
    if uuid and word_pattern(str(uuid)).search(blob):
        return True
    return False


def has_own_sheet(
    spec_docs: list[tuple[Path, str]], name: str | None, uuid: str | None
) -> bool:
    """True si el objeto tiene FICHA PROPIA en 10-especificacion/.

    Ficha propia = un fichero dedicado (su nombre coincide con el del objeto) o
    una cabecera Markdown que lo nombra (`## rule!X`, `# Pantalla: ... (X)`).

    Una simple mencion NO cuenta: en las fichas los objetos se citan entre si
    (una pantalla nombra las reglas que invoca, el indice las lista todas), asi
    que buscar en el texto concatenado daba por documentado cualquier objeto
    citado de pasada y el gate pasaba en verde sin su ficha.
    """
    pats = [word_pattern(t) for t in (name, str(uuid) if uuid else None) if t]
    if not pats:
        return False
    for path, text in spec_docs:
        if any(p.search(path.stem) for p in pats):
            return True
        for line in text.splitlines():
            if line.lstrip().startswith("#") and any(p.search(line) for p in pats):
                return True
    return False


def is_discarded(traza_lines: list[str], name: str | None, uuid: str | None) -> bool:
    """True si trazabilidad.md tiene una fila del objeto con DESCARTADO: {motivo}."""
    pats = []
    if name:
        pats.append(word_pattern(name))
    if uuid:
        pats.append(word_pattern(str(uuid)))
    for line in traza_lines:
        if not has_discard_reason(line):
            continue
        # El objeto debe ser el SUJETO de la fila (primera celda), no aparecer
        # citado en el motivo: "DESCARTADO: obsoleta, su UI paso a X" descarta
        # la fila, no a X. Sin esto, una sola fila podia dar por cubiertos a
        # todos los objetos que nombrara.
        subject = line.split("|")[1] if line.count("|") >= 2 else line
        if any(p.search(subject) for p in pats):
            return True
    return False


def build_coverage(doc_dir: Path, objects: list[dict[str, Any]], mode: str) -> dict[str, Any]:
    docs = read_markdown(doc_dir)
    full_blob = "\n".join(
        text for path, text in docs if path.name != CATALOG_FILE_NAME
    )
    spec_docs = [
        (path, text)
        for path, text in docs
        if in_spec_dir(path, doc_dir) and path.name != TRAZA_FILE_NAME
    ]
    spec_blob = "\n".join(text for _, text in spec_docs)
    traza_lines: list[str] = []
    for path, text in docs:
        if path.name == TRAZA_FILE_NAME:
            traza_lines.extend(text.splitlines())

    required: set[str] = set(ONBOARDING_REQUIRED)
    if mode == "rebuild":
        required |= set(REBUILD_EXTRA)

    by_type: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for o in objects:
        by_type[o["type"]].append(o)

    types_report: dict[str, Any] = {}
    missing_map: dict[str, list[str]] = {}
    for obj_type in sorted(by_type):
        entries = by_type[obj_type]
        documented: list[str] = []
        discarded: list[str] = []
        missing: list[str] = []
        # En rebuild, los tipos del nivel 3 solo cuentan si tienen ficha en
        # 10-especificacion/ (o estan DESCARTADO en trazabilidad.md).
        spec_scope = mode == "rebuild" and obj_type in REBUILD_EXTRA
        for o in entries:
            name, uuid = o.get("name"), o.get("uuid")
            if spec_scope:
                covered = (
                    has_own_sheet(spec_docs, name, uuid)
                    if obj_type in SHEET_REQUIRED
                    else found_in(spec_blob, name, uuid)
                )
                if covered:
                    documented.append(name)
                elif is_discarded(traza_lines, name, uuid):
                    discarded.append(name)
                else:
                    missing.append(name)
            else:
                if found_in(full_blob, name, uuid):
                    documented.append(name)
                else:
                    missing.append(name)
        types_report[obj_type] = {
            "total": len(entries),
            "documented": len(documented),
            "discarded": sorted(discarded),
            "missing": sorted(missing),
            "required": obj_type in required,
        }
        if obj_type in required and missing:
            missing_map[obj_type] = sorted(missing)

    return {
        "mode": mode,
        "docDir": str(doc_dir),
        "scannedMarkdownFiles": len(docs),
        "requiredTypes": sorted(required),
        "types": types_report,
        "missing": missing_map,
        "ok": not missing_map,
    }


def print_report(coverage: dict[str, Any]) -> None:
    print("Gate de cobertura - modo " + coverage["mode"])
    print("Salida analizada: " + coverage["docDir"])
    print("Ficheros .md escaneados: " + str(coverage["scannedMarkdownFiles"]))
    print()
    header = "{:<22} {:>18}  {}".format("Tipo", "Documentados/Total", "Regla")
    print(header)
    print("-" * len(header))
    types = coverage["types"]
    if not types:
        print("(inventario vacio: no hay objetos que cubrir)")
    for obj_type in sorted(types):
        t = types[obj_type]
        covered = t["total"] - len(t["missing"])
        cell = "{}/{}".format(covered, t["total"])
        if t["discarded"]:
            cell += " ({} descartado{})".format(
                len(t["discarded"]), "s" if len(t["discarded"]) != 1 else ""
            )
        rule = "requerido" if t["required"] else "informativo"
        print("{:<22} {:>18}  {}".format(obj_type, cell, rule))
    print()

    if coverage["missing"]:
        print("Objetos requeridos sin documentar:")
        for obj_type in sorted(coverage["missing"]):
            for name in coverage["missing"][obj_type]:
                print("  [{}] {}".format(obj_type, name))
        print()

    informative_missing = [
        (obj_type, name)
        for obj_type, t in sorted(types.items())
        if not t["required"]
        for name in t["missing"]
    ]
    if informative_missing:
        print("Objetos informativos sin documentar (no bloquean):")
        for obj_type, name in informative_missing:
            print("  [{}] {}".format(obj_type, name))
        print()

    if coverage["ok"]:
        print("RESULTADO: OK - cobertura requerida al 100%")
    else:
        total_missing = sum(len(v) for v in coverage["missing"].values())
        print(
            "RESULTADO: KO - {} objeto{} requerido{} sin documentar".format(
                total_missing,
                "s" if total_missing != 1 else "",
                "s" if total_missing != 1 else "",
            )
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Gate de cobertura documental (onboarding|rebuild)."
    )
    parser.add_argument(
        "ruta_salida",
        help="Carpeta _doc_generada (o la carpeta del export que la contiene)",
    )
    parser.add_argument(
        "--mode",
        choices=("onboarding", "rebuild"),
        default="onboarding",
        help="Nivel de exigencia del gate (default: onboarding)",
    )
    args = parser.parse_args(argv)

    doc_dir = resolve_doc_dir(Path(args.ruta_salida))
    if doc_dir is None:
        print(
            "ERROR: no se encontro _intermedio/inventory.json bajo '{}'. "
            "Ejecuta antes parse_export.py --all.".format(args.ruta_salida),
            file=sys.stderr,
        )
        return 2

    inventory_path = doc_dir / "_intermedio" / "inventory.json"
    try:
        inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print("ERROR: no se pudo leer {}: {}".format(inventory_path, exc), file=sys.stderr)
        return 2
    if not isinstance(inventory, dict):
        print("ERROR: inventory.json no tiene la forma esperada", file=sys.stderr)
        return 2

    objects = flatten_objects(inventory)
    coverage = build_coverage(doc_dir, objects, args.mode)

    out_path = doc_dir / "_intermedio" / "coverage.json"
    try:
        out_path.write_text(
            json.dumps(coverage, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    except OSError as exc:
        print("ERROR: no se pudo escribir {}: {}".format(out_path, exc), file=sys.stderr)
        return 2

    print_report(coverage)
    print("Detalle: " + str(out_path))
    return 0 if coverage["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
