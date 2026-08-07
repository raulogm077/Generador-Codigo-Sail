#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
import xml.etree.ElementTree as ET
from zipfile import ZipFile
from io import BytesIO

A_NS = "http://www.appian.com/ae/types/2009"
NS = {"a": A_NS}

TYPE_MAP = {
    "Int": "Integer",
    "Integer": "Integer",
    "Long": "Integer",
    "Text": "Text",
    "Boolean": "Boolean",
    "Date": "Date",
    "Datetime": "Datetime",
    "User": "User",
    "CollaborationDocument": "CollaborationDocument",
    "Document": "Document",
    "Guid": "Text",
}

REL_MAP = {
    "ONE_TO_MANY": "one-to-many",
    "MANY_TO_ONE": "many-to-one",
    "ONE_TO_ONE": "one-to-one",
    "MANY_TO_MANY": "many-to-many",
}


def to_snake_case(s: str) -> str:
    s = (s or "").strip()
    # Replace non-alphanumerics with spaces
    s = re.sub(r"[^A-Za-z0-9]+", " ", s)
    # Split and lowercase
    parts = [p.lower() for p in s.split() if p]
    return "_".join(parts) if parts else "record_type"


def friendly_type(type_text: str) -> str:
    t = (type_text or "").strip()
    if t.startswith("{") and "}" in t:
        t = t.split("}", 1)[1]
    return TYPE_MAP.get(t, t)


def strip_ns(tag: str) -> str:
    """`{http://…}field` -> `field`. Los exports reales van con namespace y los
    XML de ejemplo casi nunca; buscar por tag literal se come unos u otros."""
    return tag.rsplit("}", 1)[-1]


def iter_tag(root, *tags: str):
    """Descendientes cuyo tag, sin namespace, esta en `tags`."""
    wanted = set(tags)
    for el in root.iter():
        if strip_ns(el.tag) in wanted:
            yield el


def attr_any(el, *names: str) -> str:
    """Atributo por nombre, ignorando el namespace del atributo."""
    for n in names:
        for key, value in el.attrib.items():
            if strip_ns(key) == n and (value or "").strip():
                return value.strip()
    return ""


def child_text(el, *names: str) -> str:
    """Texto de un hijo directo por nombre, ignorando namespace."""
    for n in names:
        for child in el:
            if strip_ns(child.tag) == n and (child.text or "").strip():
                return child.text.strip()
    return ""


def parse_recordtype_from_file(file_obj) -> dict:
    """Parse record type from a file object or path."""
    tree = ET.parse(file_obj)
    root = tree.getroot()

    rt = next((el for el in root.iter() if strip_ns(el.tag) == "recordType"), None)
    if rt is None:
        raise ValueError("No <recordType> found in XML")

    rt_uuid = attr_any(rt, "uuid")
    rt_name = attr_any(rt, "name")

    desc = child_text(rt, "description")

    # Ver la nota en xml_to_appian_recordtype_md.py: en un export real los datos
    # del campo son elementos hijos; en XML simplificados, atributos. Se lee el
    # hijo primero y el atributo como respaldo.
    fields = []
    for f in iter_tag(rt, "field"):
        fname = child_text(f, "fieldName", "name") or attr_any(f, "name", "fieldName")
        fuuid = child_text(f, "uuid") or attr_any(f, "uuid")
        ftype = friendly_type(
            child_text(f, "type", "sourceFieldType") or attr_any(f, "type")
        )
        if fname and fuuid:
            fields.append({"name": fname, "uuid": fuuid, "type": ftype})

    rels = []
    for rcfg in iter_tag(rt, "recordRelationshipCfg", "relationship"):
        ruuid = child_text(rcfg, "uuid") or attr_any(rcfg, "uuid")
        rname = child_text(rcfg, "relationshipName") or attr_any(rcfg, "name", "relationshipName")
        raw = child_text(rcfg, "relationshipType") or attr_any(rcfg, "type", "relationshipType")
        rtype = REL_MAP.get(raw, raw.lower().replace("_", "-"))
        if ruuid and rname:
            rels.append({"name": rname, "uuid": ruuid, "type": rtype})

    actions = []
    for ac in iter_tag(rt, "recordListActionCfg", "relatedActionCfg"):
        auuid = attr_any(ac, "uuid") or child_text(ac, "uuid")
        akey = child_text(ac, "referenceKey") or attr_any(ac, "referenceKey")
        title = child_text(ac, "staticTitle", "staticTitleString") or attr_any(ac, "name")

        if auuid and akey:
            actions.append({"name": title or akey, "uuid": auuid, "key": akey})

    return {
        "uuid": rt_uuid,
        "name": rt_name,
        "description": desc,
        "fields": fields,
        "relationships": rels,
        "actions": actions,
    }


def render_markdown(rt: dict, doc_title: str) -> str:
    tag = to_snake_case(rt["name"])
    rt_ref = f"'recordType!{{{rt['uuid']}}}{rt['name']}'"

    out = []
    out.append(f"# {doc_title}\n")
    out.append(
        "This document provides the specific record type definitions for use when creating SAIL expressions.\n"
    )
    out.append("<available_record_types>")
    out.append("## Available Record Types\n")

    out.append(f"<{tag}>")
    out.append(f"### {rt['name']}")
    out.append(f"**Record Type**: `{rt_ref}`\n")

    out.append("**Description**: ")
    out.append(rt["description"] or "Not provided.")

    out.append("\n**Fields**:\n")
    out.append("| **Field Name** | **Data Type** | **Field Reference** |")
    out.append("|----------------|---------------|---------------------|")
    for f in rt["fields"]:
        fref = f"'recordType!{{{rt['uuid']}}}{rt['name']}.fields.{{{f['uuid']}}}{f['name']}'"
        out.append(f"| {f['name']} | {f['type']} | `{fref}` |")

    out.append("\n**Relationships**:\n")
    if rt["relationships"]:
        out.append("| **Relationship Name** | **Type** | **Relationship Reference** |")
        out.append("|----------------------|----------|---------------------------|")
        for r in rt["relationships"]:
            rref = f"'recordType!{{{rt['uuid']}}}{rt['name']}.relationships.{{{r['uuid']}}}{r['name']}'"
            out.append(f"| {r['name']} | {r['type']} | `{rref}` |")
        out.append(
            "\n**Note**: Access any field from related records using: `[relationshipReference].fields.{fieldUuid}fieldName`\n"
        )
    else:
        out.append("Not available\n")

    out.append("**User Filters**:\n\nNot available\n")

    out.append("**Record Actions**:\n")
    if rt["actions"]:
        out.append("\n| **Action Name** | **Action Reference** |")
        out.append("|----------------|---------------------|")
        for a in rt["actions"]:
            aref = f"'recordType!{{{rt['uuid']}}}{rt['name']}.actions.{{{a['uuid']}}}{a['key']}'"
            out.append(f"| {a['name']} | `{aref}` |")
        out.append("")
    else:
        out.append("\nNot available\n")

    out.append(f"</{tag}>\n")
    out.append("</available_record_types>\n")

    return "\n".join(out)


def process_directory(in_dir: Path, out_dir: Path) -> int:
    """Process XML files from a regular directory."""
    out_dir.mkdir(parents=True, exist_ok=True)

    xml_files = sorted(in_dir.glob("*.xml"))
    if not xml_files:
        print(f"No .xml files found in: {in_dir}")
        return 0, []

    empty: list[str] = []
    count_ok = 0
    for xml_path in xml_files:
        try:
            rt = parse_recordtype_from_file(xml_path)
            if not rt["fields"]:
                print(f"VACIO: {xml_path.name}: 0 campos legibles, no se escribe")
                empty.append(xml_path.name)
                continue
            name_snake = to_snake_case(rt["name"])
            out_name = f"data-model-context-{name_snake}.md"
            out_path = out_dir / out_name

            title = f"{rt['name']} Record Type Context Reference"
            md = render_markdown(rt, title)

            out_path.write_text(md, encoding="utf-8")
            print(f"OK: {xml_path.name} -> {out_path}")
            count_ok += 1
        except Exception as e:
            print(f"FAIL: {xml_path.name}: {e}")
            empty.append(xml_path.name)

    return count_ok, empty


def process_zip(zip_path: Path, internal_folder: str, out_dir: Path) -> int:
    """Process XML files from within a zip archive."""
    out_dir.mkdir(parents=True, exist_ok=True)

    empty: list[str] = []
    count_ok = 0
    with ZipFile(zip_path, 'r') as zf:
        # Normalize the internal folder path
        folder = internal_folder.strip("/").strip("\\")
        if folder and not folder.endswith("/"):
            folder += "/"

        # Find all XML files in the specified folder
        xml_files = [
            name for name in sorted(zf.namelist())
            if name.startswith(folder) and name.lower().endswith(".xml") and "/" not in name[len(folder):]
        ]

        if not xml_files:
            print(f"No .xml files found in zip folder: {folder or '(root)'}")
            return 0, []

        for xml_name in xml_files:
            try:
                with zf.open(xml_name) as xml_file:
                    rt = parse_recordtype_from_file(BytesIO(xml_file.read()))
                    if not rt["fields"]:
                        print(f"VACIO: {xml_name}: 0 campos legibles, no se escribe")
                        empty.append(xml_name)
                        continue
                    name_snake = to_snake_case(rt["name"])
                    out_name = f"data-model-context-{name_snake}.md"
                    out_path = out_dir / out_name

                    title = f"{rt['name']} Record Type Context Reference"
                    md = render_markdown(rt, title)

                    out_path.write_text(md, encoding="utf-8")
                    print(f"OK: {xml_name} -> {out_path}")
                    count_ok += 1
            except Exception as e:
                print(f"FAIL: {xml_name}: {e}")
                empty.append(xml_name)

    return count_ok, empty


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Process Appian recordTypeHaul XML files from a directory or zip archive"
    )
    ap.add_argument(
        "input_path",
        help="Directory containing XML files OR path to zip file",
    )
    ap.add_argument(
        "-f",
        "--folder",
        default="",
        help="Folder path within the zip file containing XML files (only used if input is a zip)",
    )
    ap.add_argument(
        "-o",
        "--output_dir",
        default=None,
        help="Directory to write markdown outputs. Defaults to current directory for zip, or input_path for directory.",
    )
    args = ap.parse_args()

    input_path = Path(args.input_path).expanduser().resolve()

    # Check if input is a zip file
    if input_path.suffix.lower() == ".zip":
        if not input_path.exists() or not input_path.is_file():
            raise SystemExit(f"Zip file does not exist: {input_path}")

        out_dir = Path(args.output_dir).expanduser().resolve() if args.output_dir else Path.cwd()
        processed, empty = process_zip(input_path, args.folder, out_dir)
    else:
        # Regular directory
        if not input_path.exists() or not input_path.is_dir():
            raise SystemExit(f"Input directory does not exist or is not a directory: {input_path}")

        out_dir = Path(args.output_dir).expanduser().resolve() if args.output_dir else input_path
        processed, empty = process_directory(input_path, out_dir)

    print(f"Processed: {processed} file(s)")

    # El lote no se aborta a medias — los XML buenos se escriben igual — pero si
    # alguno se ha quedado sin campos hay que salir en rojo. Con exit 0 el fallo
    # se pierde entre las lineas OK y luego la Fase 2 trabaja con un modelo
    # incompleto sin que nadie se haya enterado.
    if empty:
        print(
            f"\nERROR: {len(empty)} fichero(s) sin campos legibles, no escritos:",
            file=sys.stderr,
        )
        for name in empty:
            print(f"  - {name}", file=sys.stderr)
        print(
            "  Se buscaron <field> con hijos <fieldName>/<uuid>/<type> y esos\n"
            "  mismos datos como atributos. Revisa que sean recordTypeHaul.",
            file=sys.stderr,
        )
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
