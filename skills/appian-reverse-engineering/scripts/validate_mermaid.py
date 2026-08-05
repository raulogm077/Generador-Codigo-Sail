#!/usr/bin/env python3
"""
validate_mermaid.py — Valida y sanea un diagrama Mermaid según las reglas
del skill appian-reverse-engineering (references/mermaid-rules.md).

Tipos soportados (dispatch por cabecera):
    - Tipo A: flowchart TD/LR sin subgraph → saneado completo (renombrado N1..Nn,
      etiquetas, tope de 30 nodos). Comportamiento histórico, sin cambios.
    - Tipo B: erDiagram (modelo de datos) → validación de relaciones canónicas
      (||--||, ||--o{, }o--||, }o--o{) y bloques de atributos emparejados.
      SIN tope de nodos. Salida pass-through (no se reescribe).
    - Tipo C: flowchart con subgraph (lanes BPMN-styled) → se validan las
      aperturas/cierres emparejados (subgraph ... end). Salida pass-through
      con cabecera normalizada (no se aplica el saneado destructivo del Tipo A).

Uso:
    python validate_mermaid.py <fichero.mmd>
    python validate_mermaid.py -                # lee de stdin
    python validate_mermaid.py --check <archivo.md>   # busca bloques ```mermaid en un MD

Salida:
    - stdout: el diagrama saneado (o el original si ya es válido).
    - stderr: avisos y motivos de rechazo.
    - exit code:
        0 — válido (con o sin saneamiento)
        1 — no se ha podido sanear; usar tabla alternativa
        2 — error de uso
"""

from __future__ import annotations
import sys
import re
import argparse
from typing import List, Tuple

MAX_NODES = 30  # Solo aplica al Tipo A (flowchart sin subgraph).
MAX_LABEL_LEN = 50
ALLOWED_HEADERS = ("flowchart TD", "flowchart LR")

# --- Tipo B (erDiagram) -------------------------------------------------------
# Relaciones canónicas permitidas por mermaid-rules.md.
RE_ER_REL = re.compile(
    r'^(?P<left>[A-Za-z][A-Za-z0-9_]*)\s*'
    r'(?P<card>\|\|--\|\||\|\|--o\{|\}o--\|\||\}o--o\{)\s*'
    r'(?P<right>[A-Za-z][A-Za-z0-9_]*)'
    r'(?:\s*:\s*(?P<label>"[^"]*"|\S.*?))?\s*$'
)
RE_ER_BLOCK_OPEN = re.compile(r'^(?P<name>[A-Za-z][A-Za-z0-9_]*)\s*\{$')
RE_ER_ENTITY = re.compile(r'^[A-Za-z][A-Za-z0-9_]*$')

# --- Tipo C (flowchart con lanes) ---------------------------------------------
RE_SUBGRAPH_OPEN = re.compile(r'^\s*subgraph\b')

# Regex aproximadas (suficientes para nuestro subconjunto seguro).
RE_NODE = re.compile(
    r'(?P<id>[A-Za-z][A-Za-z0-9_]*)\s*'
    r'(?:\[(?P<rect>"[^"]*"|[^\[\]\n]+)\]|\{(?P<diam>"[^"]*"|[^{}\n]+)\})'
)
RE_ID_ONLY = re.compile(r'(?<![A-Za-z0-9_])([A-Za-z][A-Za-z0-9_]*)(?![A-Za-z0-9_\["{])')
RE_EDGE = re.compile(
    r'(?P<src>[A-Za-z][A-Za-z0-9_]*)\s*'
    r'(?P<arrow>-\.->|--->|-->)'
    r'(?:\s*\|\s*(?P<label>"[^"]*"|[^|]+)\s*\|\s*)?'
    r'\s*(?P<dst>[A-Za-z][A-Za-z0-9_]*)'
)


def _clean_label(raw: str) -> str:
    """Sanea una etiqueta: sin saltos, sin dobles comillas, max 50 chars."""
    s = raw.strip()
    # Si está entre comillas dobles, quita las externas.
    if s.startswith('"') and s.endswith('"') and len(s) >= 2:
        s = s[1:-1]
    s = s.replace("\n", " ").replace("\r", " ")
    s = s.replace('"', "'")
    s = re.sub(r"\s+", " ", s).strip()
    if not s:
        s = "Elemento sin nombre"
    if s.lower() == "end":
        s = "Finalización"
    if len(s) > MAX_LABEL_LEN:
        s = s[: MAX_LABEL_LEN - 1].rstrip() + "…"
    return s


def _validate_er(body: List[str], warnings: List[str]) -> None:
    """
    Valida un erDiagram (Tipo B): relaciones con notación canónica y bloques
    de atributos `ENTIDAD { ... }` bien emparejados. Sin tope de nodos
    (mermaid-rules.md: el particionamiento del modelo de datos es una regla
    de legibilidad para el agente, no un techo duro del validador).
    Lanza ValueError si algo no es válido.
    """
    in_block = False
    entities: set = set()
    for ln in body:
        s = ln.strip()
        if not s or s.startswith("%%"):
            continue
        if in_block:
            if s == "}":
                in_block = False
            elif s.endswith("{"):
                raise ValueError("erDiagram: bloque de atributos anidado no permitido.")
            # Línea de atributo (`tipo nombre [PK|FK] ...`): se acepta.
            continue
        m_open = RE_ER_BLOCK_OPEN.match(s)
        if m_open:
            entities.add(m_open.group("name"))
            in_block = True
            continue
        if s == "}":
            raise ValueError("erDiagram: '}' sin bloque de atributos abierto.")
        m_rel = RE_ER_REL.match(s)
        if m_rel:
            entities.add(m_rel.group("left"))
            entities.add(m_rel.group("right"))
            label = m_rel.group("label")
            if label is not None and not (label.startswith('"') and label.endswith('"')):
                warnings.append(
                    f"erDiagram: etiqueta de relación sin comillas dobles: {label!r} "
                    "(recomendado: \"...\")."
                )
            continue
        if RE_ER_ENTITY.match(s):
            entities.add(s)  # entidad declarada sin atributos ni relación
            continue
        if "--" in s:
            raise ValueError(
                f"erDiagram: relación con notación no canónica: '{s}'. "
                "Permitidas: ||--||, ||--o{, }o--||, }o--o{."
            )
        raise ValueError(f"erDiagram: línea no reconocida: '{s}'.")
    if in_block:
        raise ValueError("erDiagram: bloque de atributos sin cerrar ('}').")
    if not entities:
        raise ValueError("erDiagram sin entidades.")


def _validate_subgraph_lanes(body: List[str], warnings: List[str]) -> None:
    """
    Valida la estructura de lanes de un flowchart Tipo C: cada `subgraph`
    debe cerrarse con su `end` (aperturas/cierres emparejados).
    Lanza ValueError si están desemparejados.
    """
    depth = 0
    for ln in body:
        s = ln.strip()
        if RE_SUBGRAPH_OPEN.match(s):
            depth += 1
            continue
        if s == "end":
            depth -= 1
            if depth < 0:
                raise ValueError("Tipo C: 'end' sin 'subgraph' abierto.")
    if depth != 0:
        raise ValueError(
            f"Tipo C: {depth} subgraph(s) sin cerrar con 'end' (lanes desemparejados)."
        )


def sanitize(diagram_text: str) -> Tuple[str, List[str]]:
    """
    Devuelve (diagrama_saneado, lista_de_avisos).
    Lanza ValueError si el diagrama no puede sanearse.

    Dispatch por cabecera: erDiagram → Tipo B (pass-through validado);
    flowchart con subgraph → Tipo C (pass-through validado);
    flowchart sin subgraph → Tipo A (saneado histórico completo).
    """
    warnings: List[str] = []
    lines = [ln.rstrip() for ln in diagram_text.strip().splitlines() if ln.strip()]
    if not lines:
        raise ValueError("Diagrama vacío.")

    header = lines[0].strip()

    # --- Tipo B: erDiagram (modelo de datos) — sin tope de nodos. ---
    if header.split("%%", 1)[0].strip() == "erDiagram":
        _validate_er(lines[1:], warnings)
        return diagram_text.strip() + "\n", warnings

    if header not in ALLOWED_HEADERS:
        # Intenta corregir flowchart sin dirección o con dirección distinta.
        if header.startswith("flowchart"):
            warnings.append(f"Cabecera '{header}' normalizada a 'flowchart TD'.")
            header = "flowchart TD"
        elif header.startswith("graph"):
            warnings.append(f"Cabecera '{header}' convertida a 'flowchart TD'.")
            header = "flowchart TD"
        else:
            raise ValueError(
                f"Cabecera no permitida: '{header}'. Solo 'flowchart TD' o 'flowchart LR'."
            )
    body = lines[1:]

    # --- Tipo C: flowchart con lanes (subgraph ... end). ---
    # Se valida la estructura y se deja pasar tal cual: los shapes BPMN-styled
    # ((( ))), :::clase, emojis y classDef no entran en el subconjunto del Tipo A.
    if any(RE_SUBGRAPH_OPEN.match(ln) for ln in body):
        _validate_subgraph_lanes(body, warnings)
        return "\n".join([header] + body) + "\n", warnings

    # --- Tipo A: saneado histórico (sin cambios). ---
    # Detección de sintaxis prohibida.
    for ln in body:
        if re.search(r"\bsubgraph\b", ln):
            raise ValueError("'subgraph' no permitido en este subconjunto.")
        if re.search(r"\bclassDef\b|:::\w+|\bstyle\b", ln):
            warnings.append("Se ignoran estilos avanzados (classDef/style).")
        if "<br>" in ln or "<br/>" in ln or "<b>" in ln:
            warnings.append("Etiquetas con HTML detectadas: se eliminará el HTML.")
            # se limpiará al sanear etiquetas más abajo.

    # Recopila IDs originales y sus etiquetas/forma.
    id_to_label: dict[str, str] = {}
    id_to_shape: dict[str, str] = {}  # 'rect' | 'diam'
    id_order: List[str] = []

    edges_raw: List[Tuple[str, str, str, str]] = []  # (src, arrow, label, dst)

    # Primera pasada: identifica nodos con etiqueta explícita.
    for ln in body:
        clean_ln = re.sub(r"<[^>]+>", "", ln)  # quita HTML inline
        for m in RE_NODE.finditer(clean_ln):
            nid = m.group("id")
            if m.group("rect") is not None:
                label = _clean_label(m.group("rect"))
                shape = "rect"
            else:
                label = _clean_label(m.group("diam"))
                shape = "diam"
            # Si el ID ya existe con otra etiqueta, primer registro gana.
            if nid not in id_to_label:
                id_to_label[nid] = label
                id_to_shape[nid] = shape
                id_order.append(nid)

    # Segunda pasada: aristas. Permitimos referenciar IDs no declarados
    # explícitamente: se crearán como nodo rectangular con su propio nombre.
    for ln in body:
        clean_ln = re.sub(r"<[^>]+>", "", ln)
        # Sustituye nodos declarados para no confundir la regex de aristas.
        edge_line = RE_NODE.sub(lambda m: m.group("id"), clean_ln)
        for m in RE_EDGE.finditer(edge_line):
            src = m.group("src")
            dst = m.group("dst")
            arrow = m.group("arrow")
            label = m.group("label") or ""
            label = _clean_label(label) if label else ""
            edges_raw.append((src, arrow, label, dst))
            for nid in (src, dst):
                if nid not in id_to_label:
                    auto_label = _clean_label(nid)
                    id_to_label[nid] = auto_label
                    id_to_shape[nid] = "rect"
                    id_order.append(nid)
                    warnings.append(f"Nodo '{nid}' sin etiqueta declarada; se autocompleta.")

    if not id_order:
        raise ValueError("No se han detectado nodos válidos.")

    # Validación de cantidad.
    if len(id_order) > MAX_NODES:
        raise ValueError(
            f"Diagrama con {len(id_order)} nodos supera el máximo permitido ({MAX_NODES}). "
            "Dividir en varios diagramas o usar tabla."
        )

    # Renombrado a N1, N2, N3...
    remap = {old: f"N{i + 1}" for i, old in enumerate(id_order)}

    # Detección de IDs problemáticos para informar.
    problematic = [oid for oid in id_order if oid.lower() in ("end", "o", "x")
                   or re.search(r"[^A-Za-z0-9_]", oid)
                   or oid[0].lower() in ("o", "x")]
    if problematic:
        warnings.append(
            "IDs problemáticos renombrados: " + ", ".join(problematic)
        )

    # Construcción del diagrama saneado.
    out_lines: List[str] = [header]
    seen_edges: set[tuple] = set()
    declared: set[str] = set()

    # Declarar todos los nodos explícitamente para evitar ambigüedades.
    for old in id_order:
        new = remap[old]
        label = id_to_label[old]
        shape = id_to_shape[old]
        if shape == "diam":
            out_lines.append(f'  {new}{{"{label}"}}')
        else:
            out_lines.append(f'  {new}["{label}"]')
        declared.add(new)

    # Añadir aristas.
    for (src, arrow, label, dst) in edges_raw:
        nsrc, ndst = remap[src], remap[dst]
        key = (nsrc, arrow, label, ndst)
        if key in seen_edges:
            continue
        seen_edges.add(key)
        if label:
            out_lines.append(f'  {nsrc} {arrow}|"{label}"| {ndst}')
        else:
            out_lines.append(f'  {nsrc} {arrow} {ndst}')

    return "\n".join(out_lines) + "\n", warnings


def extract_mermaid_blocks(md_text: str) -> List[str]:
    """Extrae bloques ```mermaid ... ``` de un texto Markdown."""
    return re.findall(r"```mermaid\s*\n(.*?)```", md_text, flags=re.DOTALL)


def main() -> int:
    # En Windows la consola puede ser cp1252: los diagramas Tipo C llevan
    # emojis (iconos BPMN) y romperían al imprimirse. Forzamos UTF-8.
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8")
            except Exception:
                pass

    parser = argparse.ArgumentParser(description="Valida y sanea diagramas Mermaid.")
    parser.add_argument("source", help="Fichero a procesar, '-' para stdin.")
    parser.add_argument(
        "--check", action="store_true",
        help="Si el fichero es Markdown, busca bloques ```mermaid y valida cada uno."
    )
    args = parser.parse_args()

    if args.source == "-":
        raw = sys.stdin.read()
        diagrams = [raw]
    else:
        try:
            with open(args.source, encoding="utf-8") as f:
                raw = f.read()
        except OSError as e:
            print(f"[error] No se puede leer {args.source}: {e}", file=sys.stderr)
            return 2
        if args.check:
            diagrams = extract_mermaid_blocks(raw)
            if not diagrams:
                print("[info] No se han encontrado bloques mermaid.", file=sys.stderr)
                return 0
        else:
            diagrams = [raw]

    overall_ok = True
    for idx, diag in enumerate(diagrams, 1):
        try:
            clean, warns = sanitize(diag)
        except ValueError as e:
            print(f"[rechazado] Diagrama #{idx}: {e}", file=sys.stderr)
            print(
                "[acción]    Sustituir por tabla alternativa según mermaid-rules.md.",
                file=sys.stderr,
            )
            overall_ok = False
            continue
        for w in warns:
            print(f"[aviso #{idx}] {w}", file=sys.stderr)
        if len(diagrams) > 1:
            print(f"---- diagrama #{idx} ----")
        print(clean, end="")

    return 0 if overall_ok else 1


if __name__ == "__main__":
    sys.exit(main())
