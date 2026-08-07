#!/usr/bin/env python3
"""Convert an Appian recordTypeHaul XML export into the markdown “context reference” format.

Usage:
  python xml_to_appian_recordtype_md.py input.xml -o output.md
"""

from __future__ import annotations

import argparse
import re
import sys
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


def parse_recordtype(xml_path: str) -> dict:
    tree = ET.parse(xml_path)
    root = tree.getroot()

    rt = next((el for el in root.iter() if strip_ns(el.tag) == "recordType"), None)
    if rt is None:
        raise ValueError("No <recordType> found. Expected an Appian recordTypeHaul XML.")

    rt_uuid = attr_any(rt, "uuid")
    rt_name = attr_any(rt, "name")

    desc = child_text(rt, "description")

    # En un export real los datos del campo son elementos hijos (<fieldName>,
    # <uuid>, <type>); en XML simplificados o escritos a mano son atributos.
    # Se lee primero el hijo — el formato real manda — y el atributo como
    # respaldo. Es la misma leccion que ya aprendio parse_export.py de la skill
    # de reingenieria inversa; alli lo pago con 354 campos leidos como `null`.
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

    # Sin campos no hay contexto de modelo de datos, y un fichero bien formado
    # con la tabla vacia es peor que ningun fichero: la Fase 2 lo lee, no ve
    # campos y no tiene forma de saber si el record type es asi o si el parseo
    # fallo. Se aborta sin escribir.
    if not rt["fields"]:
        print(
            f"ERROR: no se ha leido ningun campo de {args.xml}.\n"
            "  Se buscaron elementos <field> con hijos <fieldName>/<uuid>/<type>\n"
            "  (formato de export real) y con esos mismos datos como atributos.\n"
            "  Si el XML no es un recordTypeHaul de Appian, este no es el script.\n"
            "  No se ha escrito nada: un data-model-context vacio se lee como\n"
            "  'este record type no tiene campos' y eso es mentira.",
            file=sys.stderr,
        )
        return 1

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
