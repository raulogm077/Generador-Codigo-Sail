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
  constant y site. Cada uno debe tener FICHA PROPIA en `10-especificacion/`
  o estar en `trazabilidad.md` marcado `DESCARTADO: {motivo}` con motivo no
  vacio.
  Nota de diseno: ni `trazabilidad.md` ni `INVENTARIO.md` cuentan como
  evidencia en NINGUN modo — ambos listan TODOS los objetos por contrato, asi
  que contarlos hacia el gate trivialmente verde (con la matriz de
  trazabilidad como unico documento, los 7 tipos de onboarding salian al
  100%).

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

# En modo `rebuild` TODOS los tipos de REBUILD_EXTRA necesitan FICHA PROPIA:
# una mencion de pasada no basta, porque las fichas se citan entre si (el indice
# las lista, una pantalla nombra las reglas que invoca) y eso convertia el gate
# en un tramite.
#
# Donde vive la ficha de cada tipo, y como se reconoce:
#   interface      -> 10-especificacion/pantallas/{interfaz}.md  (fichero o su H1)
#   expressionRule -> ### rule!X     en reglas-catalogo.md
#   decision       -> ### decision!X en reglas-catalogo.md
#   constant       -> ### cons!X     en reglas-catalogo.md  (seccion Constantes)
#   site           -> ## site!X      en navegacion.md
#
# El prefijo tipado (`rule!`, `cons!`, ...) es lo que distingue una FICHA de una
# MENCION: sin el, cabeceras que la propia plantilla induce ("## Reglas
# invocadas", "## Constantes usadas: X") daban por documentado cualquier objeto
# citado bajo ellas.
SHEET_PREFIXES = {
    "expressionRule": ("rule!",),
    "decision": ("decision!", "rule!"),
    "constant": ("cons!",),
    "site": ("site!",),
}
# Tipos cuya ficha es un documento entero, no una cabecera dentro de otro.
SHEET_DOC_DIR = {"interface": "pantallas"}

SPEC_DIR_NAME = "10-especificacion"
TRAZA_FILE_NAME = "trazabilidad.md"
CATALOG_FILE_NAME = "INVENTARIO.md"

# Documentos que listan TODOS los objetos del export por contrato: son catalogos,
# no documentacion. Si contaran como evidencia, cualquier objeto estaria siempre
# "documentado" y el gate no podria fallar nunca.
NOT_EVIDENCE = {CATALOG_FILE_NAME, TRAZA_FILE_NAME}

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
    objetos de diseno documentables) y fuerza `name`/`uuid`/`type` a str: un
    inventario con `"name": 123` reventaba con TypeError dentro de re.escape.
    """
    raw = inventory.get("objects", {})
    flat: list[dict[str, Any]] = []
    if isinstance(raw, dict):
        for lst in raw.values():
            if isinstance(lst, list):
                flat.extend(x for x in lst if isinstance(x, dict))
    elif isinstance(raw, list):
        flat = [x for x in raw if isinstance(x, dict)]
    out: list[dict[str, Any]] = []
    for o in flat:
        if not o.get("type") or not o.get("name"):
            continue
        norm = dict(o)
        norm["type"] = str(o["type"])
        norm["name"] = str(o["name"])
        norm["uuid"] = str(o["uuid"]) if o.get("uuid") else None
        out.append(norm)
    return out


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


def _covered_by_longer(blob: str, start: int, end: int, longer: tuple[str, ...]) -> bool:
    """True si el match [start,end) cae dentro de un nombre mas largo."""
    for l in longer:
        idx = blob.find(l)
        while idx != -1:
            if idx <= start and end <= idx + len(l):
                return True
            idx = blob.find(l, idx + 1)
    return False


def found_in(
    blob: str, name: str | None, uuid: str | None, longer: tuple[str, ...] = ()
) -> bool:
    """Aparicion del objeto en el texto, ignorando las que son parte de otro.

    `longer` son los nombres del inventario que CONTIENEN a `name`. Los record
    types de Appian llevan espacios ("DEMO Solicitud"), y los limites de palabra
    los aceptan como separador: sin este filtro, documentar solo
    "DEMO Solicitud Historica" daba por documentada tambien "DEMO Solicitud".
    """
    for token in (name, str(uuid) if uuid else None):
        if not token:
            continue
        for m in word_pattern(token).finditer(blob):
            if longer and _covered_by_longer(blob, m.start(), m.end(), longer):
                continue
            return True
    return False


def _sheet_heading_pats(obj_type: str, tokens: list[str]) -> list[re.Pattern]:
    """Patrones de cabecera-ficha: `### rule!X`, `## site!X`, ..."""
    return [
        re.compile(re.escape(prefix + token) + r"(?![A-Za-z0-9_])")
        for prefix in SHEET_PREFIXES.get(obj_type, ())
        for token in tokens
    ]


def has_own_sheet(
    spec_docs: list[tuple[Path, str, tuple[str, ...]]],
    obj_type: str,
    name: str | None,
    uuid: str | None,
) -> bool:
    """True si el objeto tiene FICHA PROPIA en 10-especificacion/.

    Ficha propia significa, segun el tipo:
      - fichero dedicado cuyo nombre ES el del objeto (cualquier tipo);
      - interface: ademas, el H1 de un documento bajo `pantallas/` que lo nombra;
      - resto: una cabecera con el PREFIJO TIPADO (`### rule!X`, `## site!X`).

    El prefijo es lo que separa ficha de mencion. Aceptar "cualquier cabecera que
    nombre al objeto" dejaba pasar las que la propia plantilla induce — una ficha
    con `## Constantes usadas: X` y `## Otras pantallas: Y` daba por documentados
    a X e Y sin que existiera su ficha.
    """
    tokens = [t for t in (name, str(uuid) if uuid else None) if t]
    if not tokens:
        return False
    heading_pats = _sheet_heading_pats(obj_type, tokens)
    doc_dir_req = SHEET_DOC_DIR.get(obj_type)
    word_pats = [word_pattern(t) for t in tokens]
    for path, text, rel_parts in spec_docs:
        if path.stem in tokens:
            return True
        if heading_pats:
            for line in text.splitlines():
                if line.lstrip().startswith("#") and any(p.search(line) for p in heading_pats):
                    return True
        elif doc_dir_req is None or doc_dir_req in rel_parts:
            # Sin prefijo tipado la ficha es el documento entero: solo cuenta su
            # H1, nunca una cabecera de listado de nivel inferior.
            for line in text.splitlines():
                stripped = line.lstrip()
                if stripped.startswith("# ") and any(p.search(stripped) for p in word_pats):
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
        # El objeto debe ser el SUJETO, no aparecer citado en el motivo:
        # "DESCARTADO: obsoleta, su UI paso a X" descarta la fila, no a X. En
        # una tabla el sujeto es la primera celda; fuera de tabla, lo que hay
        # antes del marcador (el motivo va siempre detras).
        if line.count("|") >= 2:
            subject = line.split("|")[1]
        else:
            subject = line.split("DESCARTADO")[0]
        if any(p.search(subject) for p in pats):
            return True
    return False


def build_coverage(doc_dir: Path, objects: list[dict[str, Any]], mode: str) -> dict[str, Any]:
    docs = read_markdown(doc_dir)
    full_blob = "\n".join(text for path, text in docs if path.name not in NOT_EVIDENCE)
    spec_docs = [
        (path, text, path.relative_to(doc_dir).parts)
        for path, text in docs
        if in_spec_dir(path, doc_dir) and path.name not in NOT_EVIDENCE
    ]
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

    all_names = {o["name"] for o in objects}
    longer_of = {
        n: tuple(sorted(x for x in all_names if x != n and n in x)) for n in all_names
    }

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
                if has_own_sheet(spec_docs, obj_type, name, uuid):
                    documented.append(name)
                elif is_discarded(traza_lines, name, uuid):
                    discarded.append(name)
                else:
                    missing.append(name)
            else:
                if found_in(full_blob, name, uuid, longer_of.get(name, ())):
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
