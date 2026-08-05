#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_spec_layout.py — Gate de ESTRUCTURA de la documentacion generada.

Complementa a `check_coverage.py`: aquel comprueba QUE objetos estan
documentados; este comprueba que los documentos estan BIEN FORMADOS.

Uso:
  python check_spec_layout.py <ruta_salida> [--mode onboarding|rebuild]

`<ruta_salida>` es la carpeta `_doc_generada` (tambien se acepta la carpeta
que la contiene: si existe `<ruta>/_doc_generada` se usa ESA, nunca el
contenedor — buscarlo al reves daba por buena una salida sin `10-especificacion/`
y con todos los enlaces relativos resueltos contra la raiz equivocada).

Comprueba:
  1. Layout    — en modo rebuild, 10-especificacion/ con pantallas/ y procesos/
                 dentro (nunca colgando de la raiz).
  2. Enlaces   — todo link relativo resuelve a un FICHERO existente dentro del
                 arbol de salida.
  3. Anclas    — todo `#fragmento` hacia un documento del arbol existe como
                 heading.
  4. Plantilla — cada ficha de pantalla lleva sus secciones obligatorias CON
                 contenido y al menos un criterio de reconstruccion verificable.
  5. Higiene   — cero placeholders sin rellenar ({{...}}, <TODO>, lorem ipsum,
                 TBD) fuera de los bloques de codigo.

Los bloques de codigo (``` / ~~~) se excluyen de 2, 3 y 5: un ejemplo que
ilustra el propio contrato no es un enlace roto ni un placeholder olvidado.

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
from urllib.parse import unquote

SPEC_DIR = "10-especificacion"
PANTALLAS_DIR = "pantallas"

# Documentos del nivel onboarding: pueden no existir si la spec se entrega por
# separado, pero su nombre debe ser uno del contrato.
ONBOARDING_DOCS = {
    "00-resumen-ejecutivo.md", "01-funcional.md", "02-arquitectura.md",
    "03-modelo-datos.md", "04-seguridad-grupos.md", "05-integraciones-consumidas.md",
    "06-apis-expuestas.md", "07-batches.md", "09-valor-adicional.md",
    "INVENTARIO.md",
}

# Secciones obligatorias de pantalla-template.md (H2). Se comparan por prefijo:
# el titulo real lleva coletilla ("## Entradas (rule inputs)").
SECCIONES_PANTALLA = (
    "Entradas",
    "Variables locales",
    "Componentes",
    "Acciones",
    "Reglas invocadas",
    "Estados de la pantalla",
    "Criterios de reconstrucción",
)

SECCION_CRITERIOS = "Criterios de reconstrucción"

PLACEHOLDER_RES = (
    ("{{", re.compile(r"\{\{")),
    ("<TODO>", re.compile(r"<TODO>", re.IGNORECASE)),
    ("lorem ipsum", re.compile(r"lorem\s+ipsum", re.IGNORECASE)),
    ("TBD", re.compile(r"(?<![A-Za-z0-9_])TBD(?![A-Za-z0-9_])")),
)

# Enlace markdown tolerante a las formas de CommonMark que un LLM emite sin
# avisar: destino entre <>, titulo tras el destino, y %-encoding en la ruta.
LINK_RE = re.compile(
    r"\[[^\]]*\]\(\s*(<[^>\n]*>|[^)\s]+)"
    r"(?:\s+(?:\"[^\"\n]*\"|'[^'\n]*'|\([^)\n]*\)))?\s*\)"
)
HEADING_RE = re.compile(r"^\s{0,3}(#{1,6})\s+(.*?)\s*#*\s*$")
FENCE_RE = re.compile(r"^\s{0,3}(`{3,}|~{3,})")
CRITERIO_RE = re.compile(r"^\s*[-*]\s+\[[ xX]\]")


def slug(texto: str) -> str:
    """Slugificacion estilo GitHub.

    GitHub convierte CADA espacio en un guion, sin colapsar los consecutivos.
    Importa mas de lo que parece: un titulo como `### 5.1 🔴 Las candidaturas`
    pierde el emoji y deja dos espacios, asi que su ancla real es
    `#51--las-candidaturas` con DOS guiones. Colapsandolos, el gate marcaba como
    rota toda ancla hacia un titulo con emoji o con doble espacio — es decir,
    casi todas las de una salida real, que usa emojis por contrato.
    """
    s = texto.strip().lower()
    s = re.sub(r"[`*_]", "", s)
    s = re.sub(r"[^\w\s-]", "", s, flags=re.UNICODE)
    return re.sub(r"\s", "-", s).strip("-")


def strip_code_blocks(texto: str) -> str:
    """Vacia las lineas dentro de fences, conservando el numero de lineas.

    Un bloque ```markdown que ilustra la tabla de enlaces del contrato no puede
    contar como enlace roto, ni un `{{nombre}}` de ejemplo como placeholder sin
    rellenar. Los spans inline (`x`) SI se conservan: forman parte del texto de
    las cabeceras y quitarlos cambiaria sus anclas.
    """
    out: list[str] = []
    fence: str | None = None
    for line in texto.splitlines():
        m = FENCE_RE.match(line)
        if fence is not None:
            out.append("")
            if m and m.group(1)[0] == fence[0] and len(m.group(1)) >= len(fence):
                fence = None
            continue
        if m:
            fence = m.group(1)
            out.append("")
            continue
        out.append(line)
    return "\n".join(out)


def link_targets(texto: str) -> list[str]:
    destinos = []
    for m in LINK_RE.finditer(texto):
        raw = m.group(1).strip()
        if raw.startswith("<") and raw.endswith(">"):
            raw = raw[1:-1].strip()
        if raw:
            destinos.append(raw)
    return destinos


def headings_of(texto: str) -> list[tuple[int, str]]:
    return [
        (len(m.group(1)), m.group(2))
        for m in (HEADING_RE.match(l) for l in texto.splitlines())
        if m
    ]


def is_inside(path: Path, base: Path) -> bool:
    try:
        path.resolve().relative_to(base.resolve())
        return True
    except (ValueError, OSError):
        return False


def rel_within(path: Path, base: Path) -> str | None:
    try:
        return path.resolve().relative_to(base.resolve()).as_posix()
    except (ValueError, OSError):
        return None


def resolve_doc_dir(target: Path) -> Path | None:
    """La salida real manda sobre el contenedor.

    Se prueba `<target>/_doc_generada` ANTES que `<target>`: con rglob, el
    contenedor siempre "tiene .md" (los de dentro de _doc_generada), asi que
    probarlo primero devolvia la carpeta equivocada y todo lo demas — layout,
    enlaces relativos — se evaluaba contra una raiz que no era la salida.
    """
    for cand in (target / "_doc_generada", target):
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
    for sub in (PANTALLAS_DIR, "procesos"):
        if (doc_dir / sub).is_dir():
            problemas.append(
                f"{sub}/ cuelga de la raiz; debe estar dentro de {SPEC_DIR}/"
            )
    return problemas


def check_links(doc_dir: Path, docs: dict[str, str], presentes: set[str]) -> list[str]:
    problemas: list[str] = []
    for rel, texto in docs.items():
        base = (doc_dir / rel).parent
        for destino in link_targets(texto):
            if destino.startswith(("http://", "https://", "#", "mailto:", "tel:")):
                continue
            ruta = unquote(destino.split("#")[0])
            if not ruta:
                continue
            p = base / ruta
            if not is_inside(p, doc_dir):
                problemas.append(f"enlace fuera del arbol de salida: {rel} -> {destino}")
                continue
            if p.is_file():
                continue
            if p.is_dir():
                problemas.append(
                    f"enlace a un directorio (debe apuntar a un fichero): {rel} -> {destino}"
                )
                continue
            nombre = Path(ruta).name
            # Escotilla para los documentos 00-09: solo vale si el documento NO
            # esta en la salida. Si esta y la ruta no resuelve, la ruta esta mal
            # construida (typo o ../ de menos) y hay que reportarla.
            if nombre in ONBOARDING_DOCS and nombre not in presentes:
                continue
            problemas.append(f"enlace roto: {rel} -> {destino}")
    return problemas


def check_anchors(doc_dir: Path, docs: dict[str, str]) -> list[str]:
    anclas = {
        rel: {slug(texto_h) for _, texto_h in headings_of(texto)}
        for rel, texto in docs.items()
    }
    problemas: list[str] = []
    for rel, texto in docs.items():
        base = (doc_dir / rel).parent
        for destino in link_targets(texto):
            if "#" not in destino or destino.startswith(("http", "mailto:")):
                continue
            ruta, frag = destino.split("#", 1)
            if not frag.strip():
                continue  # `[subir](#)` es idiom estandar, no un ancla rota
            if not ruta:
                objetivo = rel
            else:
                p = base / unquote(ruta)
                if not p.is_file():
                    continue  # ya lo reporta check_links
                objetivo = rel_within(p, doc_dir)
                if objetivo is None:
                    continue  # fuera del arbol: ya lo reporta check_links
            if objetivo in anclas and slug(frag) not in anclas[objetivo]:
                problemas.append(f"ancla rota: {rel} -> {destino}")
    return problemas


def secciones_de(texto: str) -> dict[str, str]:
    """Mapa titulo H2 -> cuerpo (hasta el siguiente H1/H2)."""
    lineas = texto.splitlines()
    marcas: list[tuple[int, str]] = []
    fence: str | None = None
    for i, line in enumerate(lineas):
        m = FENCE_RE.match(line)
        if fence is not None:
            if m and m.group(1)[0] == fence[0]:
                fence = None
            continue
        if m:
            fence = m.group(1)
            continue
        h = HEADING_RE.match(line)
        if h and len(h.group(1)) <= 2:
            marcas.append((i, h.group(2) if len(h.group(1)) == 2 else ""))
    out: dict[str, str] = {}
    for idx, (i, titulo) in enumerate(marcas):
        if not titulo:
            continue
        fin = marcas[idx + 1][0] if idx + 1 < len(marcas) else len(lineas)
        out[titulo] = "\n".join(lineas[i + 1:fin])
    return out


def check_pantallas(doc_dir: Path, mode: str) -> list[str]:
    if mode != "rebuild":
        return []
    carpeta = doc_dir / SPEC_DIR / PANTALLAS_DIR
    if not carpeta.is_dir():
        return []
    problemas: list[str] = []
    # rglob, no glob: las fichas pueden agruparse por modulo
    # (pantallas/modulo1/X.md) y antes esas se saltaban la validacion entera.
    for p in sorted(carpeta.rglob("*.md")):
        if p.stem == "indice":
            continue
        texto = p.read_text(encoding="utf-8", errors="replace")
        secciones = secciones_de(texto)
        for esperada in SECCIONES_PANTALLA:
            casadas = [t for t in secciones if t.startswith(esperada)]
            if not casadas:
                problemas.append(f"{p.name}: falta la seccion '## {esperada}'")
                continue
            # Una cabecera sin cuerpo no documenta nada: el contrato exige
            # contenido o un "N/A — {motivo}" explicito.
            if not any(secciones[t].strip() for t in casadas):
                problemas.append(f"{p.name}: la seccion '## {esperada}' esta vacia")
        for titulo in secciones:
            if not titulo.startswith(SECCION_CRITERIOS):
                continue
            if not any(CRITERIO_RE.match(l) for l in secciones[titulo].splitlines()):
                problemas.append(
                    f"{p.name}: sin criterios de reconstruccion verificables "
                    "(se esperan items '- [ ]')"
                )
    return problemas


def check_hygiene(docs: dict[str, str]) -> list[str]:
    return [
        f"placeholder sin rellenar en {rel}: {etiqueta}"
        for rel, texto in docs.items()
        for etiqueta, patron in PLACEHOLDER_RES
        if patron.search(texto)
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
    # El analisis de enlaces, anclas e higiene ignora los bloques de codigo.
    limpios = {rel: strip_code_blocks(texto) for rel, texto in docs.items()}
    presentes = {Path(rel).name for rel in docs}

    problemas: list[str] = []
    problemas += check_layout(doc_dir, args.mode)
    problemas += check_links(doc_dir, limpios, presentes)
    problemas += check_anchors(doc_dir, limpios)
    problemas += check_pantallas(doc_dir, args.mode)
    problemas += check_hygiene(limpios)

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
