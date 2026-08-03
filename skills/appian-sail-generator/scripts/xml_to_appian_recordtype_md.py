#!/usr/bin/env python3
"""Convert an Appian recordTypeHaul XML export into the markdown “context reference” format.

Usage:
  python xml_to_appian_recordtype_md.py input.xml -o output.md
"""

from __future__ import annotations

import argparse
import re
import xml.etree.ElementTree as ET

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


def slug(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_").lower()


def friendly_type(type_text: str) -> str:
    t = (type_text or "").strip()
    if t.startswith("{") and "}" in t:
        t = t.split("}", 1)[1]
    return TYPE_MAP.get(t, t)


def parse_recordtype(xml_path: str) -> dict:
    tree = ET.parse(xml_path)
    root = tree.getroot()

    rt = root.find("recordType")
    if rt is None:
        raise ValueError("No <recordType> found. Expected an Appian recordTypeHaul XML.")

    rt_uuid = rt.attrib.get(f"{{{A_NS}}}uuid") or rt.attrib.get("uuid")
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
    tag = slug(rt["name"]) or "record_type"
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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("xml", help="Path to Appian recordTypeHaul XML (e.g., *.xml)")
    ap.add_argument(
        "-o",
        "--out",
        default=None,
        help="Output markdown path. Defaults to <input>.md in the same directory.",
    )
    ap.add_argument(
        "--title",
        default=None,
        help="Markdown H1 title. Defaults to '<Record Type Name> Record Type Context Reference'.",
    )
    args = ap.parse_args()

    rt = parse_recordtype(args.xml)

    title = args.title or f"{rt['name']} Record Type Context Reference"
    md = render_markdown(rt, title)

    out_path = args.out
    if not out_path:
        out_path = re.sub(r"\.xml$", "", args.xml, flags=re.IGNORECASE) + ".md"

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(md)

    print(out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
