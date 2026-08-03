#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
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


def parse_recordtype_from_file(file_obj) -> dict:
    """Parse record type from a file object or path."""
    tree = ET.parse(file_obj)
    root = tree.getroot()

    rt = root.find("recordType")
    if rt is None:
        raise ValueError("No <recordType> found in XML")

    rt_uuid = rt.attrib.get(f"{{{A_NS}}}uuid") or rt.attrib.get("uuid") or ""
    rt_name = rt.attrib.get("name") or ""

    desc_el = rt.find("a:description", namespaces=NS)
    desc = (desc_el.text or "").strip() if desc_el is not None else ""

    fields = []
    for f in rt.findall(".//field"):
        fname = (f.findtext("fieldName") or "").strip()
        fuuid = (f.findtext("uuid") or "").strip()
        ftype = friendly_type(f.findtext("type") or "")
        if fname and fuuid:
            fields.append({"name": fname, "uuid": fuuid, "type": ftype})

    rels = []
    for rcfg in rt.findall(".//a:recordRelationshipCfg", namespaces=NS):
        ruuid = (rcfg.findtext("uuid") or "").strip()
        rname = (rcfg.findtext("relationshipName") or "").strip()
        raw = (rcfg.findtext("relationshipType") or "").strip()
        rtype = REL_MAP.get(raw, raw.lower().replace("_", "-"))
        if ruuid and rname:
            rels.append({"name": rname, "uuid": ruuid, "type": rtype})

    actions = []
    act_cfgs = rt.findall(".//a:recordListActionCfg", namespaces=NS) + rt.findall(
        ".//a:relatedActionCfg", namespaces=NS
    )
    for ac in act_cfgs:
        auuid = ac.attrib.get(f"{{{A_NS}}}uuid") or ""
        akey = (ac.findtext("a:referenceKey", default="", namespaces=NS) or "").strip()
        title = (
            (ac.findtext("a:staticTitle", default="", namespaces=NS) or "")
            or (ac.findtext("a:staticTitleString", default="", namespaces=NS) or "")
        ).strip()

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
        return 0

    count_ok = 0
    for xml_path in xml_files:
        try:
            rt = parse_recordtype_from_file(xml_path)
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

    return count_ok


def process_zip(zip_path: Path, internal_folder: str, out_dir: Path) -> int:
    """Process XML files from within a zip archive."""
    out_dir.mkdir(parents=True, exist_ok=True)

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
            return 0

        for xml_name in xml_files:
            try:
                with zf.open(xml_name) as xml_file:
                    rt = parse_recordtype_from_file(BytesIO(xml_file.read()))
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

    return count_ok


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
        processed = process_zip(input_path, args.folder, out_dir)
    else:
        # Regular directory
        if not input_path.exists() or not input_path.is_dir():
            raise SystemExit(f"Input directory does not exist or is not a directory: {input_path}")

        out_dir = Path(args.output_dir).expanduser().resolve() if args.output_dir else input_path
        processed = process_directory(input_path, out_dir)

    print(f"Processed: {processed} file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
