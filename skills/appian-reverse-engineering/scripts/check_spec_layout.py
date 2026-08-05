#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_spec_layout.py — Gate de ESTRUCTURA de la documentacion generada.

Complementa a `check_coverage.py`: aquel comprueba QUE objetos estan
documentados; este comprueba que los documentos estan BIEN FORMADOS.

Uso:
  python check_spec_layout.py <ruta_salida> [--mode onboarding|rebuild]

`<ruta_salida>` es la carpeta `_doc_generada` (tambien se acepta la carpeta
que la contiene).

Comprueba:
  1. Layout    — en modo rebuild, 10-especificacion/ con pantallas/ y procesos/
                 dentro (nunca colgando de la raiz).
  2. Enlaces   — todo link relativo resuelve a un fichero existente.
  3. Anclas    — todo `#fragmento` hacia un documento del arbol existe como
                 heading.
  4. Plantilla — cada ficha de pantalla lleva sus secciones obligatorias y al
                 menos un criterio de reconstruccion verificable (`- [ ]`).
  5. Higiene   — cero placeholders sin rellenar ({{...}}, <TODO>, lorem ipsum).

Exit codes:
  0  estructura correcta
  1  hay problemas (se listan en stdout)
  2  error de uso / IO

Solo stdlib de Python 3.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SPEC_DIR = "10-especificacion"

# Documentos del nivel onboarding: pueden no existir si se enlazan desde una
# spec entregada por separado, pero su nombre debe ser uno del contrato.
ONBOARDING_DOCS = {
    "00-resumen-ejecutivo.md", "01-funcional.md", "02-arquitectura.md",
    "03-modelo-datos.md", "04-seguridad-grupos.md", "05-integraciones-consumidas.md",
    "06-apis-expuestas.md", "07-batches.md", "09-valor-adicional.md",
    "INVENTARIO.md",
}

SECCIONES_PANTALLA = (
    "## Entradas",
    "## Componentes",
    "## Acciones",
    "## Criterios de reconstrucción",
)

PLACEHOLDERS = ("{{", "<TODO>", "lorem ipsum", "TBD")

LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
HEADING_RE = re.compile(r"^#{1,6}\s+(.*)$")


def slug(texto: str) -> str:
    """Slugificacion estilo GitHub (suficiente para las anclas que generamos)."""
    s = texto.strip().lower()
    s = re.sub(r"[`*_]", "", s)
    s = re.sub(r"[^\w\s-]", "", s, flags=re.UNICODE)
    return re.sub(r"\s+", "-", s).strip("-")


def resolve_doc_dir(target: Path) -> Path | None:
    # rglob, no glob: en una salida de nivel 3 los .md pueden estar todos en
    # subcarpetas (10-especificacion/pantallas/...).
    for cand in (target, target / "_doc_generada"):
        if cand.is_dir() and next(cand.rglob("*.md"), None) is not None:
            return cand
    return None


def read_docs(doc_dir: Path) -> dict[str, str]:
    docs: dict[str, str] = {}
    for p in sorted(doc_dir.rglob("*.md")):
        try:
            docs[p.relative_to(doc_dir).as_posix()] = p.read_text(
                encoding="utf-8", errors="replace"
            )
        except OSError:
            continue
    return docs


def check_layout(doc_dir: Path, mode: str) -> list[str]:
    problemas: list[str] = []
    if mode != "rebuild":
        return problemas
    spec = doc_dir / SPEC_DIR
    if not spec.is_dir():
        return [f"falta la carpeta {SPEC_DIR}/ (obligatoria en modo rebuild)"]
    for sub in ("pantallas", "procesos"):
        if (doc_dir / sub).is_dir():
            problemas.append(
                f"{sub}/ cuelga de la raiz; debe estar dentro de {SPEC_DIR}/"
            )
    return problemas


def check_links(doc_dir: Path, docs: dict[str, str]) -> list[str]:
    problemas: list[str] = []
    for rel, texto in docs.items():
        base = (doc_dir / rel).parent
        for destino in LINK_RE.findall(texto):
            if destino.startswith(("http://", "https://", "#", "mailto:")):
                continue
            ruta = destino.split("#")[0]
            if not ruta:
                continue
            if Path(ruta).name in ONBOARDING_DOCS and not (base / ruta).exists():
                continue  # documento del nivel onboarding no incluido en esta salida
            if not (base / ruta).exists():
                problemas.append(f"enlace roto: {rel} -> {destino}")
    return problemas


def check_anchors(doc_dir: Path, docs: dict[str, str]) -> list[str]:
    anclas = {
        rel: {
            slug(m.group(1))
            for m in (HEADING_RE.match(l) for l in texto.splitlines())
            if m
        }
        for rel, texto in docs.items()
    }
    problemas: list[str] = []
    for rel, texto in docs.items():
        base = (doc_dir / rel).parent
        for destino in LINK_RE.findall(texto):
            if "#" not in destino or destino.startswith(("http", "mailto:")):
                continue
            ruta, frag = destino.split("#", 1)
            if not ruta:
                objetivo = rel
            else:
                p = (base / ruta)
                if not p.exists():
                    continue  # ya lo reporta check_links
                objetivo = p.resolve().relative_to(doc_dir.resolve()).as_posix()
            if objetivo in anclas and slug(frag) not in anclas[objetivo]:
                problemas.append(f"ancla rota: {rel} -> {destino}")
    return problemas


def check_pantallas(doc_dir: Path, mode: str) -> list[str]:
    if mode != "rebuild":
        return []
    carpeta = doc_dir / SPEC_DIR / "pantallas"
    if not carpeta.is_dir():
        return []
    problemas: list[str] = []
    for p in sorted(carpeta.glob("*.md")):
        if p.stem == "indice":
            continue
        texto = p.read_text(encoding="utf-8", errors="replace")
        for seccion in SECCIONES_PANTALLA:
            if seccion not in texto:
                problemas.append(f"{p.name}: falta la seccion '{seccion}'")
        bloque = re.search(
            r"## Criterios de reconstrucción.*?(?=\n## |\Z)", texto, re.S
        )
        if bloque and "- [ ]" not in bloque.group(0):
            problemas.append(f"{p.name}: sin criterios de reconstruccion verificables")
    return problemas


def check_hygiene(docs: dict[str, str]) -> list[str]:
    return [
        f"placeholder sin rellenar en {rel}: {t}"
        for rel, texto in docs.items()
        for t in PLACEHOLDERS
        if t in texto
    ]


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("salida", metavar="RUTA")
    ap.add_argument("--mode", choices=("onboarding", "rebuild"), default="onboarding")
    args = ap.parse_args(argv)

    target = Path(args.salida).resolve()
    if not target.exists():
        print(f"ERROR: la ruta {target} no existe", file=sys.stderr)
        return 2
    doc_dir = resolve_doc_dir(target)
    if doc_dir is None:
        print(f"ERROR: no encuentro documentos .md en {target}", file=sys.stderr)
        return 2

    docs = read_docs(doc_dir)
    problemas: list[str] = []
    problemas += check_layout(doc_dir, args.mode)
    problemas += check_links(doc_dir, docs)
    problemas += check_anchors(doc_dir, docs)
    problemas += check_pantallas(doc_dir, args.mode)
    problemas += check_hygiene(docs)

    print(f"Gate de estructura - modo {args.mode}")
    print(f"Salida analizada: {doc_dir}")
    print(f"Ficheros .md escaneados: {len(docs)}\n")

    if problemas:
        print(f"RESULTADO: KO - {len(problemas)} problema(s) de estructura\n")
        for x in problemas:
            print(f"  {x}")
        return 1

    print("RESULTADO: OK - estructura correcta")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
