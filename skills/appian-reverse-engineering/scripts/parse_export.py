#!/usr/bin/env python3
"""
parse_export.py — Parser de exports de aplicaciones Appian (formato real *Haul).

Solo stdlib de Python 3. Reconoce el formato real de los export packages:
cada XML está envuelto en `<xxxHaul>` y el objeto está dentro como hijo.

Comandos:
  python3 parse_export.py --check <ruta>
  python3 parse_export.py --inventory <ruta> [--out <ruta_json>]
  python3 parse_export.py --graph <ruta> [--out <ruta_json>]
  python3 parse_export.py --all <ruta> --out-dir <ruta_dir>
  python3 parse_export.py --detail <ruta> [--out <ruta_json>]
      (por defecto escribe <ruta>/_doc_generada/_intermedio/detail.json)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any
from urllib.parse import unquote
from xml.etree import ElementTree as ET

HAUL_TO_TYPE = {
    "applicationHaul": "application",
    "siteHaul": "site",
    "portalHaul": "portal",
    "recordTypeHaul": "recordType",
    "processModelHaul": "processModel",
    "processModelFolderHaul": "processModelFolder",
    "connectedSystemHaul": "connectedSystem",
    "groupHaul": "group",
    "groupTypeHaul": "groupType",
    "dataStoreHaul": "dataStore",
    "contentHaul": "content",
}

CONTENT_SUBTYPES = {
    "interface", "rule", "expressionRule", "constant", "decision",
    "outboundIntegration", "integration", "webApi", "document", "folder",
    "rulesFolder", "report", "communityKnowledgeCenter", "knowledgeCenter",
    "freeformRule", "decisionTable",
}

SUBTYPE_TO_CANONICAL = {
    "rule": "expressionRule",
    "freeformRule": "expressionRule",
    "outboundIntegration": "integration",
    "decisionTable": "decision",
    "rulesFolder": "folder",
    "communityKnowledgeCenter": "knowledgeCenter",
}

APPIAN_HAUL_HINTS = set(HAUL_TO_TYPE.keys())


def strip_ns(tag: str) -> str:
    if "}" in tag:
        return tag.split("}", 1)[1]
    return tag


def safe_parse(path: Path) -> ET.Element | None:
    try:
        return ET.parse(str(path)).getroot()
    except (ET.ParseError, OSError, UnicodeDecodeError):
        return None


def first_relevant_child(haul_root: ET.Element) -> ET.Element | None:
    skip = {"versionUuid", "roleMap", "history", "icon", "parentUuid", "rolemap", "folderUuid"}
    for child in haul_root:
        if strip_ns(child.tag) not in skip:
            return child
    return None


def get_attr_any(elem: ET.Element, *names: str) -> str | None:
    for n in names:
        for k in elem.attrib:
            if strip_ns(k) == n:
                return elem.attrib[k]
    return None


def find_first_text(elem: ET.Element, *names: str, max_depth: int = 6) -> str | None:
    target = set(names)

    def walk(e: ET.Element, depth: int):
        if depth > max_depth:
            return None
        for c in e:
            if strip_ns(c.tag) in target:
                txt = (c.text or "").strip()
                if txt:
                    return txt
            result = walk(c, depth + 1)
            if result:
                return result
        return None

    return walk(elem, 0)


def _name_from_element(nm: ET.Element) -> str | None:
    if nm.text and nm.text.strip():
        return nm.text.strip()
    candidates: dict[str, str] = {}
    for pair in nm.iter():
        if strip_ns(pair.tag) != "pair":
            continue
        lang = None
        value = None
        for child in pair:
            if strip_ns(child.tag) == "locale":
                lang = (child.attrib.get("lang") or "").lower()
            elif strip_ns(child.tag) == "value":
                value = (child.text or "").strip()
        # Los exports reales traen el par de un idioma VACIO (<value/>): si se
        # aceptara, el nombre saldria a medias.
        if value:
            candidates[lang or ""] = value
    for k in ("es", "en", ""):
        if candidates.get(k):
            return candidates[k]
    if candidates:
        return next(iter(candidates.values()))
    return None


def extract_localized_name(elem: ET.Element) -> str | None:
    """Nombre del objeto, priorizando el <name> que es HIJO DIRECTO.

    Un process model real lleva <name> anidados que no son suyos —el del
    timer-trigger, el de cada nodo, el de cada variable—. Recorriendo todos los
    descendientes salia el primero que tuviera texto: los batches del export
    real se llamaban `Timer_1`.
    """
    for nm in elem:
        if strip_ns(nm.tag) == "name":
            nombre = _name_from_element(nm)
            if nombre:
                return nombre
    for nm in elem.iter():
        if strip_ns(nm.tag) == "name":
            nombre = _name_from_element(nm)
            if nombre:
                return nombre
    return None


def extract_localized_desc(elem: ET.Element) -> str | None:
    for d in elem.iter():
        if strip_ns(d.tag) not in ("desc", "description", "documentation"):
            continue
        if d.text and d.text.strip():
            return d.text.strip()
        for pair in d.iter():
            if strip_ns(pair.tag) != "pair":
                continue
            lang = None
            value = None
            for child in pair:
                if strip_ns(child.tag) == "locale":
                    lang = (child.attrib.get("lang") or "").lower()
                elif strip_ns(child.tag) == "value":
                    value = (child.text or "").strip()
            if value and (lang == "es" or lang is None):
                return value
    return None


def mask(value: str) -> str:
    if not value:
        return ""
    if len(value) <= 4:
        return "***"
    return value[:2] + "***"


def looks_like_secret_value(value: str) -> bool:
    if not value or len(value) < 6:
        return False
    v = value.strip()
    patterns = [
        r"^[A-Za-z0-9+/]{32,}=*$",
        r"^[A-Fa-f0-9]{32,}$",
        r"^AKIA[0-9A-Z]{16}$",
        r"^gh[pousr]_[A-Za-z0-9]{36,}$",
        r"-----BEGIN (RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----",
    ]
    return any(re.search(p, v) for p in patterns)


def _looks_secret_by_name(name: str | None) -> bool:
    if not name:
        return False
    return bool(re.search(r"(?i)(password|passwd|pwd|secret|token|apikey|api[_-]?key|credential)", name))


def _mask_url(url: str | None) -> str | None:
    if not url:
        return url
    return re.sub(r"(https?://)([^/:]+):([^@/]+)@", lambda m: m.group(1) + m.group(2) + ":***@", url)


def mask_sail(sail: str) -> str:
    """Enmascara secretos dentro de SAIL con las mismas reglas que los valores
    sueltos: URLs con credenciales y literales de texto que parecen secretos."""
    if not sail:
        return sail
    sail = _mask_url(sail) or sail

    def _mask_literal(m: re.Match) -> str:
        inner = m.group(1)
        if looks_like_secret_value(inner):
            return '"' + mask(inner) + '"'
        return m.group(0)

    return re.sub(r'"([^"\n]{6,})"', _mask_literal, sail)


def walk_xml_files(root: Path):
    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in {".xml", ".xsd", ".bpmn"}:
            yield path


def cmd_check(root: Path) -> int:
    hints: list[str] = []
    for sub in ["application", "applications"]:
        d = root / sub
        if d.exists():
            for f in d.glob("*.xml"):
                elem = safe_parse(f)
                if elem is not None and strip_ns(elem.tag) == "applicationHaul":
                    hints.append(f"applicationHaul en {f.relative_to(root)}")
    for sub in ["processModel", "recordType", "site", "datatype", "group", "connectedSystem", "content", "META-INF", "processModelFolder", "dataStore"]:
        d = root / sub
        if d.exists() and d.is_dir():
            n = sum(1 for _ in d.iterdir())
            if n > 0:
                hints.append(f"{sub}/ con {n} ficheros")
    if (root / "application.xml").exists():
        hints.append("application.xml en raíz (formato antiguo)")
    xsd_count = sum(1 for _ in root.rglob("*.xsd"))
    if xsd_count:
        hints.append(f"{xsd_count} XSDs (CDTs)")
    icf_count = sum(1 for _ in root.rglob("import-customization-file*.properties"))
    if icf_count:
        hints.append(f"{icf_count} ICF")
    haul_seen: set[str] = set()
    seen_count = 0
    for p in walk_xml_files(root):
        if p.suffix.lower() == ".xsd":
            continue
        elem = safe_parse(p)
        if elem is None:
            continue
        local = strip_ns(elem.tag)
        if local in APPIAN_HAUL_HINTS:
            haul_seen.add(local)
            seen_count += 1
            if seen_count >= 100:
                break
    if haul_seen:
        hints.append(f"{seen_count}+ Hauls reconocidos: {', '.join(sorted(haul_seen))}")
    if hints:
        print("OK Parece un export Appian. Senales detectadas:")
        for h in hints:
            print(f"  - {h}")
        return 0
    print("KO No parece un export Appian.")
    return 1


def _has_timer_trigger(pm_root: ET.Element) -> bool:
    """True si el modelo arranca por temporizador.

    Un export real no lo declara en el nodo de start: lo lleva en
    <pre-triggers><timer-trigger><recurrence>, y `recurrence` es un elemento CON
    HIJOS — buscar su texto devolvia None y ningun batch se detectaba.
    """
    return any(
        strip_ns(el.tag) in ("timer-trigger", "timerTrigger", "recurrence")
        for el in pm_root.iter()
    )


def _detect_start_type(pm_root: ET.Element) -> str:
    for node in pm_root.iter():
        if strip_ns(node.tag) == "node" and node.attrib.get("type") in {"start", "startEvent"}:
            st = node.attrib.get("startType") or find_first_text(node, "startType")
            if st:
                return st
            for sub in node.iter():
                if strip_ns(sub.tag) == "recurrence":
                    return "timer"
                if strip_ns(sub.tag) == "messageTrigger":
                    return "message"
            return "none"
    return "timer" if _has_timer_trigger(pm_root) else "unknown"


def extract_haul_object(path: Path, haul_root: ET.Element) -> dict[str, Any] | None:
    haul_tag = strip_ns(haul_root.tag)
    base_type = HAUL_TO_TYPE.get(haul_tag)
    if base_type is None:
        return None

    inner = None
    if base_type == "content":
        inner = first_relevant_child(haul_root)
    else:
        alias = HAUL_INNER_ALIASES.get(base_type, ())
        candidatos = {base_type, base_type.replace("Type", "type"), *alias}
        # Busqueda en profundidad limitada: en un export real el process model
        # no cuelga del haul, va dentro de <process_model_port><pm>. Buscando
        # solo hijos directos, `inner` acababa siendo <versionUuid> y todo
        # (nombre, nodos, recurrencia) se leia del sitio equivocado.
        pendientes = [(haul_root, 0)]
        while pendientes and inner is None:
            el, nivel = pendientes.pop(0)
            for child in el:
                if strip_ns(child.tag) in candidatos:
                    inner = child
                    break
                if nivel < 2:
                    pendientes.append((child, nivel + 1))
        if inner is None:
            inner = first_relevant_child(haul_root) or haul_root

    if inner is None:
        return None

    obj_type = base_type
    if base_type == "content":
        inner_tag = strip_ns(inner.tag)
        obj_type = SUBTYPE_TO_CANONICAL.get(inner_tag, inner_tag)
        if inner_tag not in CONTENT_SUBTYPES:
            obj_type = "content"

    # extract_localized_name ANTES que find_first_text: aquella prioriza el
    # <name> hijo directo (el del objeto), esta busca en profundidad y se
    # quedaba con el primero que tuviera texto — el <name> del timer-trigger,
    # asi que los batches del export real se llamaban "Timer_1".
    name = (
        get_attr_any(inner, "name", "displayName")
        or extract_localized_name(inner)
        or find_first_text(inner, "name", "displayName", "label", "pluralName", "staticName")
        or path.stem
    )
    uuid = (
        get_attr_any(inner, "uuid", "id")
        or find_first_text(inner, "uuid", "id", "versionUuid")
        or find_first_text(haul_root, "versionUuid")
    )
    description = (
        find_first_text(inner, "description", "documentation")
        or extract_localized_desc(inner)
    )
    meta: dict[str, Any] = {
        "type": obj_type,
        "name": name,
        "uuid": uuid,
        "description": description,
        "path": str(path),
        "haulType": haul_tag,
    }

    # Refinamiento del nombre para process models: el name real esta en
    # process_model_port/pm/meta/process-name o meta/name (string-map localized).
    if obj_type == "processModel":
        for meta_el in inner.iter():
            if strip_ns(meta_el.tag) != "meta":
                continue
            # `name` ANTES que `process-name`: el primero es el nombre del
            # MODELO y el segundo la expresion que nombra cada INSTANCIA
            # (="X - " & pp!starttime). Al reves, y tras limpiarle las comillas,
            # los process models quedaban bautizados "X - ".
            for cand_tag in ("name", "process-name"):
                for child in meta_el:
                    if strip_ns(child.tag) != cand_tag:
                        continue
                    nm_candidates: dict[str, str] = {}
                    for pair in child.iter():
                        if strip_ns(pair.tag) != "pair":
                            continue
                        lang = None
                        value = None
                        for c in pair:
                            if strip_ns(c.tag) == "locale":
                                lang = (c.attrib.get("lang") or "").lower()
                            elif strip_ns(c.tag) == "value":
                                value = (c.text or "").strip()
                        if value:
                            nm_candidates[lang or ""] = value
                    for k in ("es", "en", ""):
                        if nm_candidates.get(k):
                            name = nm_candidates[k]
                            break
                    if name and name not in ("Start Node", "End Node"):
                        # Limpiar expresiones SAIL del nombre (algunos PMs tienen el nombre como expresion)
                        if name.startswith('='):
                            m = re.match(r'^="([^"]+)"', name)
                            if m:
                                name = m.group(1)
                        meta["name"] = name
                        break
                if name and name not in ("Start Node", "End Node") and not name.startswith('='):
                    break
            break  # solo el primer <meta>

    if obj_type == "constant":
        val = find_first_text(inner, "value")
        if val:
            if looks_like_secret_value(val) or _looks_secret_by_name(name):
                meta["value"] = mask(val)
                meta["maskedSecret"] = True
            else:
                meta["value"] = val[:200]
        type_ref = find_first_text(inner, "typeRef", "type")
        if type_ref:
            meta["typeRef"] = type_ref
    elif obj_type == "integration":
        meta["method"] = find_first_text(inner, "method", "httpMethod")
        meta["endpoint"] = _mask_url(find_first_text(inner, "endpoint", "url", "uri"))
        meta["connectedSystemRef"] = find_first_text(inner, "connectedSystemRef", "connectedSystem")
    elif obj_type == "connectedSystem":
        meta["csType"] = find_first_text(inner, "connectedSystemType", "type")
        meta["baseUrl"] = _mask_url(find_first_text(inner, "baseUrl", "url"))
        meta["authType"] = find_first_text(inner, "authenticationType", "authType")
    elif obj_type == "webApi":
        meta["method"] = find_first_text(inner, "httpMethod")
        meta["endpointPath"] = find_first_text(inner, "endpointPath")
    elif obj_type == "processModel":
        meta["startType"] = _detect_start_type(inner)
        node_count = sub_count = user_task_count = 0
        for n in inner.iter():
            if strip_ns(n.tag) == "node":
                node_count += 1
                ntype = n.attrib.get("type") or ""
                if ntype == "subProcess":
                    sub_count += 1
                if ntype == "userInput":
                    user_task_count += 1
        meta["nodeCount"] = node_count
        meta["subProcessCount"] = sub_count
        meta["userTaskCount"] = user_task_count
        if _has_timer_trigger(inner):
            meta["hasRecurrence"] = True
    elif obj_type == "site":
        page_count = sum(1 for n in inner.iter() if strip_ns(n.tag) in ("page", "sitePage"))
        meta["pageCount"] = page_count
    elif obj_type == "group":
        meta["parentGroup"] = find_first_text(inner, "parentGroup")
        meta["groupType"] = find_first_text(inner, "groupType")
    elif obj_type == "recordType":
        field_count = sum(1 for n in inner.iter() if strip_ns(n.tag) == "field")
        meta["fieldCount"] = field_count
        meta["urlStub"] = find_first_text(inner, "urlStub")
    elif obj_type == "interface":
        try:
            meta["sailBytes"] = path.stat().st_size
        except OSError:
            pass
    elif obj_type == "application":
        meta["prefix"] = find_first_text(inner, "prefix")
        meta["urlIdentifier"] = find_first_text(inner, "urlIdentifier")
    return meta


def cmd_inventory(root: Path) -> dict[str, Any]:
    inventory: dict[str, list[dict[str, Any]]] = defaultdict(list)
    parse_errors = 0

    for xsd in root.rglob("*.xsd"):
        cdt_root = safe_parse(xsd)
        decoded_name = unquote(xsd.stem)
        m = re.search(r"\}([^}]+)$", decoded_name)
        clean_name = m.group(1) if m else decoded_name
        meta = {"type": "cdt", "name": clean_name, "path": str(xsd)}
        if cdt_root is not None:
            ns = cdt_root.attrib.get("targetNamespace")
            if ns:
                meta["namespace"] = ns
            fields = [
                e for e in cdt_root.iter()
                if strip_ns(e.tag) == "element" and "name" in e.attrib
            ]
            meta["fieldCount"] = len(fields)
            for ann in cdt_root.iter():
                txt = (ann.text or "")
                if "@Table" in txt:
                    m = re.search(r'@Table\s*\(\s*name\s*=\s*"([^"]+)"', txt)
                    if m:
                        meta["table"] = m.group(1)
                        break
        inventory["cdt"].append(meta)

    for path in walk_xml_files(root):
        if path.suffix.lower() == ".xsd":
            continue
        elem = safe_parse(path)
        if elem is None:
            parse_errors += 1
            continue
        root_local = strip_ns(elem.tag)
        if root_local not in APPIAN_HAUL_HINTS:
            continue
        meta = extract_haul_object(path, elem)
        if meta is None:
            continue
        inventory[meta["type"]].append(meta)

    icfs = []
    for icf in root.rglob("import-customization-file*.properties"):
        icfs.append({"path": str(icf), "size": icf.stat().st_size})
    if icfs:
        inventory["icf"] = icfs

    counts = {k: len(v) for k, v in inventory.items()}
    return {"counts": counts, "objects": dict(inventory), "parseErrors": parse_errors}


# Como se llama de verdad el elemento del objeto dentro de su <xxxHaul>. Los
# exports reales no siempre usan el nombre del tipo: un process model vive en
# <process_model_port><pm>.
HAUL_INNER_ALIASES = {
    "processModel": ("pm", "process_model", "process-model"),
    "recordType": ("record_type",),
    "dataStore": ("data_store", "datastore"),
}


REF_PATTERNS = {
    # --- Formato CANONICO: el que Appian exporta de verdad --------------------
    # En el Designer se escribe `rule!MiRegla(...)`, pero el XML exportado lleva
    # la forma canonica `#"{uuid}"(...)`. En un export real de 106 objetos,
    # `rule!`, `cons!` y `recordType!` tenian CERO apariciones — el grafo daba
    # 91 huerfanos y habria hecho descartar media aplicacion por "0 callers".
    "canonicalRef": re.compile(r'#"([^"\n]{2,300})"'),
    # Los roleMap referencian grupos con un UUID de prefijo distinto (`_e-`).
    "groupUuid": re.compile(
        r"<(?:[\w.\-]+:)?groupUuid>\s*([^<\s][^<]*?)\s*</(?:[\w.\-]+:)?groupUuid>"
    ),
    # {recordTypeUuid}/{fieldUuid}: el primero identifica el record type. Es la
    # referencia mas frecuente con diferencia (960 apariciones en ese export).
    "recordFieldRef": re.compile(
        r"urn:appian:record-field:v1:([0-9a-fA-F\-]{36})/"
    ),
    # --- Formato del Designer / SAIL escrito a mano ---------------------------
    "expressionRule": re.compile(r"rule!([A-Za-z0-9_]+)"),
    "constant": re.compile(r"cons!([A-Za-z0-9_]+)"),
    "uuidRecordType": re.compile(r'urn:appian:record-type:v1:([0-9a-fA-F\-]{36})'),
    "startProcess": re.compile(r"a!startProcess\s*\(\s*processModel\s*:\s*([A-Za-z0-9_!\{\}\-]+)"),
    "integrationCall": re.compile(r"a!integrationCall\s*\(\s*integration\s*:\s*([A-Za-z0-9_!\{\}\-]+)"),
    # Patrones documentados en analysis-workflow.md que faltaban:
    "queryEntity": re.compile(r"a!queryEntity\s*\(\s*entity\s*:\s*cons!([A-Za-z0-9_]+)"),
    "writeEntity": re.compile(r"a!writeToDataStoreEntity\s*\(\s*dataStoreEntity\s*:\s*cons!([A-Za-z0-9_]+)"),
    "writeRecords": re.compile(r"a!writeRecords\s*\([\s\S]{0,400}?\{([0-9a-fA-F\-]{36})\}"),
    "subprocess": re.compile(r"<(?:[\w.\-]+:)?processModelUuid>\s*([0-9a-fA-F\-]{36})\s*</(?:[\w.\-]+:)?processModelUuid>"),
    "memberOfGroup": re.compile(r"a!isUserMemberOfGroup\s*\([\s\S]{0,200}?groups?\s*:\s*(?:cons!)?([A-Za-z0-9_]+)"),
    "connectedSystemRef": re.compile(r"<(?:[\w.\-]+:)?connectedSystemRef>\s*([^<\s][^<]*?)\s*</(?:[\w.\-]+:)?connectedSystemRef>"),
}

# Referencias ESTRUCTURALES: no viajan en SAIL sino en tags/atributos del XML.
# Sin ellas, objetos vivos salian huerfanos y `backlog-writer` los proponia como
# DESCARTADO por "0 callers": el formulario principal de la app (form de start
# event, de user task, vista del record y pagina del site) y la integracion con
# el ERP (<integrationRef> en su nodo) eran los dos casos del fixture.
#
#   (tag, atributo o None para el texto, tipos candidatos, refType)
STRUCT_REF_RULES = (
    ("form", None, ("interface",), "form"),
    ("formRef", None, ("interface",), "form"),
    ("integrationRef", None, ("integration",), "integrationCall"),
    ("assignees", None, ("group",), "assignment"),
    ("assignee", None, ("group",), "assignment"),
    ("view", "interface", ("interface",), "recordView"),
    ("recordView", "interface", ("interface",), "recordView"),
    ("action", "process", ("processModel",), "recordAction"),
    ("recordAction", "process", ("processModel",), "recordAction"),
    ("page", "objectUuid", ("recordType", "interface", "report"), "sitePage"),
    ("sitePage", "objectUuid", ("recordType", "interface", "report"), "sitePage"),
    ("visibilityGroup", None, ("group",), "security"),
    ("entity", "cdt", ("cdt",), "entityCdt"),
    ("variable", "type", ("cdt",), "variableType"),
)

# Barrido de UUIDs: red de seguridad para las referencias que viajan en tags o
# atributos y no en expresiones (un record type lanza su related action con
# <a:target a:uuid="...">). Sin esto, en el export real los 13 process models
# salian huerfanos los 13.
# El prefijo de letra varia con el tipo de objeto: `_a-` en los de content,
# `_e-` en los grupos (<groupUuid> de los roleMap). Fijandolo a `_a-`, los 8
# grupos del export real salian huerfanos los 8.
ANY_UUID_RE = re.compile(
    r"(_[a-z]-[0-9a-fA-F\-]{36}_\d+"
    r"|[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})"
)

# Tipos que LISTAN objetos por contrato: son catalogos y contenedores, no
# callers. La application enumera toda la app, asi que contarla como referencia
# dejaria el concepto de huerfano sin sentido (mismo problema que INVENTARIO.md
# en el gate de cobertura).
CATALOG_SOURCE_TYPES = {"application", "folder", "knowledgeCenter", "processModelFolder"}

# Prefijos de las referencias canonicas que NO son objetos del export:
# `SYSTEM_SYSRULES_*` son los componentes de plataforma (a!formLayout se llama
# asi por dentro) y los `urn:appian:*` tienen sus propios patrones.
CANONICAL_IGNORED_PREFIXES = ("SYSTEM_", "urn:appian:", "http://", "https://")

# Que clase de arista es una referencia canonica, segun lo que resulte ser el
# destino (la forma `#"{uuid}"` no dice el tipo, hay que mirar el inventario).
CANONICAL_REF_TYPE = {
    "expressionRule": "ruleRef",
    "interface": "ruleRef",
    "decision": "ruleRef",
    "webApi": "ruleRef",
    "constant": "constRef",
    "recordType": "recordTypeRef",
    "processModel": "startProcess",
    "integration": "integrationCall",
    "connectedSystem": "connectedSystem",
    "dataStore": "dataStoreEntity",
    "group": "security",
}

# Precedencia al resolver una referencia canonica escrita por NOMBRE (algunos
# exports antiguos lo hacen). Misma que la de `rule!`, ampliada.
CANONICAL_NAME_PRECEDENCE = (
    "expressionRule", "interface", "decision", "constant", "recordType",
    "processModel", "integration", "connectedSystem", "dataStore", "group",
)

# Aristas que representan INVOCACION (A ejecuta B). Solo estas cuentan para
# detectar ciclos: en Appian es normal y sano que un record type tenga como
# vista una interfaz que consulta ese mismo record, y reportarlo como ciclo
# seria ruido en todas las apps.
CYCLE_REF_TYPES = {"ruleRef", "startProcess", "subprocess", "recordAction", "form"}

# Puntos de entrada: nada dentro del export los invoca, asi que grado entrante 0
# es su estado NORMAL y no evidencia de objeto muerto. Los process models con
# recurrencia (batches) se anaden en tiempo de ejecucion.
ENTRY_POINT_TYPES = {
    "application", "site", "webApi", "portal",
    # Contenedores: nadie los "llama", contienen. Grado entrante 0 es su estado
    # normal y listarlos como huerfanos solo genera ruido.
    "folder", "knowledgeCenter", "processModelFolder",
}

# Umbral de acoplamiento fuerte (grado entrante). Documentado en
# references/analysis-workflow.md — si cambia aqui, cambia alli.
HUB_MIN_INDEGREE = 5


def cmd_graph(root: Path, inventory: dict[str, Any]) -> dict[str, Any]:
    name_index: dict[tuple[str, str], dict[str, Any]] = {}
    uuid_index: dict[str, dict[str, Any]] = {}
    for obj_type, objs in inventory.get("objects", {}).items():
        for o in objs:
            if o.get("name"):
                name_index[(obj_type, o["name"])] = o
            if o.get("uuid"):
                uuid_index[o["uuid"]] = o

    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    edge_set: set[tuple[str, str, str]] = set()

    def node_id(obj: dict[str, Any]) -> str:
        return obj.get("uuid") or f"{obj.get('type')}::{obj.get('name')}"

    for obj_type, objs in inventory.get("objects", {}).items():
        for o in objs:
            nodes.append({
                "id": node_id(o),
                "type": obj_type,
                "name": o.get("name"),
                "path": o.get("path"),
            })

    def add_edge(source: dict[str, Any], target: dict[str, Any], ref_type: str):
        e = (node_id(source), node_id(target), ref_type)
        if e in edge_set:
            return
        edge_set.add(e)
        edges.append({
            "source": e[0],
            "target": e[1],
            "from": source.get("name"),
            "to": target.get("name"),
            "refType": ref_type,
        })

    # Indice por nombre agnostico de tipo, para las referencias canonicas que
    # vienen escritas por nombre en vez de por UUID.
    name_any: dict[str, dict[str, Any]] = {}
    for cand_type in reversed(CANONICAL_NAME_PRECEDENCE):
        for (t, n), obj in name_index.items():
            if t == cand_type:
                name_any[n] = obj

    for obj_type, objs in inventory.get("objects", {}).items():
        for o in objs:
            p = Path(o["path"])
            try:
                content = p.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            # Referencias canonicas #"{uuid}" / #"{nombre}".
            for m in REF_PATTERNS["canonicalRef"].finditer(content):
                token = m.group(1).strip()
                if not token or token.startswith(CANONICAL_IGNORED_PREFIXES):
                    continue
                target = uuid_index.get(token) or name_any.get(token)
                if target and target is not o:
                    add_edge(
                        o,
                        target,
                        CANONICAL_REF_TYPE.get(target.get("type"), "canonicalRef"),
                    )
            for m in REF_PATTERNS["recordFieldRef"].finditer(content):
                target = uuid_index.get(m.group(1))
                if target and target is not o:
                    add_edge(o, target, "recordFieldRef")
            for m in REF_PATTERNS["groupUuid"].finditer(content):
                tgt = m.group(1)
                target = uuid_index.get(tgt) or name_index.get(("group", tgt))
                if target and target is not o:
                    add_edge(o, target, "security")
            # Barrido de UUIDs. refType generico a proposito: sabemos que hay
            # una referencia, no de que clase — no vale para inferir invocacion
            # (por eso `uuidRef` no cuenta para los ciclos).
            if obj_type not in CATALOG_SOURCE_TYPES:
                for token in set(ANY_UUID_RE.findall(content)):
                    target = uuid_index.get(token)
                    if target and target is not o:
                        add_edge(o, target, "uuidRef")
            for m in REF_PATTERNS["expressionRule"].finditer(content):
                # rule! puede apuntar a expression rule, interfaz o decision (bug
                # de interfaces-huerfanas: antes solo se probaba expressionRule).
                target = (
                    name_index.get(("expressionRule", m.group(1)))
                    or name_index.get(("interface", m.group(1)))
                    or name_index.get(("decision", m.group(1)))
                )
                if target and target is not o:
                    add_edge(o, target, "ruleRef")
            for m in REF_PATTERNS["constant"].finditer(content):
                target = name_index.get(("constant", m.group(1)))
                if target and target is not o:
                    add_edge(o, target, "constRef")
            for m in REF_PATTERNS["uuidRecordType"].finditer(content):
                target = uuid_index.get(m.group(1))
                if target and target is not o:
                    add_edge(o, target, "recordTypeRef")
            for m in REF_PATTERNS["startProcess"].finditer(content):
                tgt = m.group(1).lstrip("!").strip("{}")
                target = name_index.get(("processModel", tgt)) or uuid_index.get(tgt)
                if target and target is not o:
                    add_edge(o, target, "startProcess")
            for m in REF_PATTERNS["integrationCall"].finditer(content):
                tgt = m.group(1).lstrip("!").strip("{}")
                target = name_index.get(("integration", tgt)) or uuid_index.get(tgt)
                if target and target is not o:
                    add_edge(o, target, "integrationCall")
            for m in REF_PATTERNS["queryEntity"].finditer(content):
                target = name_index.get(("constant", m.group(1)))
                if target and target is not o:
                    add_edge(o, target, "queryEntity")
            for m in REF_PATTERNS["writeEntity"].finditer(content):
                target = name_index.get(("constant", m.group(1)))
                if target and target is not o:
                    add_edge(o, target, "writeEntity")
            for m in REF_PATTERNS["writeRecords"].finditer(content):
                target = uuid_index.get(m.group(1))
                if target and target is not o:
                    add_edge(o, target, "writeRecords")
            for m in REF_PATTERNS["subprocess"].finditer(content):
                target = uuid_index.get(m.group(1))
                if target and target is not o:
                    add_edge(o, target, "subprocess")
            for m in REF_PATTERNS["memberOfGroup"].finditer(content):
                target = (
                    name_index.get(("group", m.group(1)))
                    or name_index.get(("constant", m.group(1)))
                )
                if target and target is not o:
                    add_edge(o, target, "security")
            for m in REF_PATTERNS["connectedSystemRef"].finditer(content):
                tgt = m.group(1)
                target = name_index.get(("connectedSystem", tgt)) or uuid_index.get(tgt)
                if target and target is not o:
                    add_edge(o, target, "connectedSystem")
            # Referencias estructurales (tags/atributos, no SAIL).
            elem = safe_parse(p)
            if elem is None:
                continue
            for node in elem.iter():
                tag = strip_ns(node.tag)
                for rule_tag, attr, tipos, ref_type in STRUCT_REF_RULES:
                    if tag != rule_tag:
                        continue
                    raw = get_attr_any(node, attr) if attr else (node.text or "")
                    tgt = (raw or "").strip()
                    if not tgt:
                        continue
                    target = uuid_index.get(tgt)
                    if target is None:
                        for cand in tipos:
                            target = name_index.get((cand, tgt))
                            if target is not None:
                                break
                    if target is not None and target is not o:
                        add_edge(o, target, ref_type)
            # Constantes TIPADAS: su <value> es el unico vinculo con el objeto al
            # que apuntan (una constante de tipo Group es como SAIL referencia un
            # grupo: no existe literal `group!X`).
            if obj_type == "constant":
                type_ref = (o.get("typeRef") or "").lower()
                val = (o.get("value") or "").strip()
                target, ref_type = None, None
                if "data store" in type_ref:
                    target = name_index.get(("dataStore", val.split(".")[0].strip()))
                    ref_type = "dataStoreEntity"
                elif "group" in type_ref:
                    target = uuid_index.get(val) or name_index.get(("group", val))
                    ref_type = "constGroup"
                elif "document" in type_ref or "folder" in type_ref:
                    target = uuid_index.get(val)
                    ref_type = "constContent"
                if target is not None and target is not o:
                    add_edge(o, target, ref_type)

    group_by_name = {g["name"]: g for g in inventory.get("objects", {}).get("group", []) if g.get("name")}
    for g in inventory.get("objects", {}).get("group", []):
        parent = g.get("parentGroup")
        if parent and parent in group_by_name:
            add_edge(group_by_name[parent], g, "memberGroup")

    indegree: dict[str, int] = defaultdict(int)
    outdegree: dict[str, int] = defaultdict(int)
    for e in edges:
        indegree[e["target"]] += 1
        outdegree[e["source"]] += 1

    batch_ids = {
        node_id(o)
        for o in inventory.get("objects", {}).get("processModel", [])
        if o.get("hasRecurrence") or (o.get("startType") or "") in {"timer", "recurrence"}
    }
    orphans = [
        n["name"] or n["id"]
        for n in nodes
        if indegree[n["id"]] == 0
        and n["type"] not in ENTRY_POINT_TYPES
        and n["id"] not in batch_ids
    ]
    hubs = sorted(
        (
            {
                "id": n["id"],
                "name": n["name"],
                "type": n["type"],
                "in": indegree[n["id"]],
                "out": outdegree[n["id"]],
            }
            for n in nodes
            if indegree[n["id"]] >= HUB_MIN_INDEGREE
        ),
        key=lambda x: -x["in"],
    )
    cycles = find_cycles(nodes, [e for e in edges if e["refType"] in CYCLE_REF_TYPES])
    return {
        "nodes": nodes,
        "edges": edges,
        "stats": {
            "nodeCount": len(nodes),
            "edgeCount": len(edges),
            "orphanCount": len(orphans),
            "hubCount": len(hubs),
            "cycleCount": len(cycles),
        },
        # orphans va COMPLETA a proposito: backlog-writer la usa como evidencia
        # de "objeto muerto" para justificar un DESCARTADO, y una lista truncada
        # afirmaria muerte sobre datos incompletos. hubs si es un top-N.
        "orphans": orphans,
        "hubs": hubs[:30],  # top-30 por indegree (deliberado)
        "cycles": cycles,
    }


def find_cycles(nodes: list[dict[str, Any]], edges: list[dict[str, Any]]) -> list[list[str]]:
    """Componentes fuertemente conexas de tamano > 1 (Tarjan iterativo).

    Un ciclo de invocacion (A llama a B que vuelve a llamar a A) es un riesgo de
    recursion infinita y un obstaculo para reconstruir la app por capas: hay que
    verlo antes de planificar el orden de construccion.
    """
    succ: dict[str, list[str]] = defaultdict(list)
    for e in edges:
        succ[e["source"]].append(e["target"])
    name_of = {n["id"]: (n["name"] or n["id"]) for n in nodes}

    index: dict[str, int] = {}
    low: dict[str, int] = {}
    on_stack: set[str] = set()
    stack: list[str] = []
    counter = 0
    out: list[list[str]] = []

    for raiz in [n["id"] for n in nodes]:
        if raiz in index:
            continue
        # (nodo, iterador de sucesores) — pila explicita: un grafo de miles de
        # objetos desbordaria la recursion de Python.
        work: list[tuple[str, int]] = [(raiz, 0)]
        index[raiz] = low[raiz] = counter
        counter += 1
        stack.append(raiz)
        on_stack.add(raiz)
        while work:
            v, i = work[-1]
            vecinos = succ.get(v, ())
            if i < len(vecinos):
                work[-1] = (v, i + 1)
                w = vecinos[i]
                if w not in index:
                    index[w] = low[w] = counter
                    counter += 1
                    stack.append(w)
                    on_stack.add(w)
                    work.append((w, 0))
                elif w in on_stack:
                    low[v] = min(low[v], index[w])
                continue
            work.pop()
            if work:
                padre = work[-1][0]
                low[padre] = min(low[padre], low[v])
            if low[v] == index[v]:
                comp = []
                while True:
                    w = stack.pop()
                    on_stack.discard(w)
                    comp.append(name_of.get(w, w))
                    if w == v:
                        break
                if len(comp) > 1:
                    out.append(sorted(comp))
    return out


def _to_bool(val: str | None) -> bool:
    return (val or "").strip().lower() in {"true", "1", "yes"}


def _haul_inner(path: Path) -> ET.Element | None:
    """Devuelve el elemento del objeto dentro de su envoltorio <xxxHaul>."""
    haul_root = safe_parse(path)
    if haul_root is None:
        return None
    base_type = HAUL_TO_TYPE.get(strip_ns(haul_root.tag))
    if base_type is None:
        return None
    if base_type == "content":
        return first_relevant_child(haul_root)
    for child in haul_root:
        t = strip_ns(child.tag)
        if t == base_type or t == base_type.replace("Type", "type"):
            return child
    return first_relevant_child(haul_root) or haul_root


RT_FIELD_UUID_RE = re.compile(r"recordType!\{([0-9a-fA-F\-]{36})\}")


def _sail_of(inner: ET.Element) -> str:
    for el in inner.iter():
        if strip_ns(el.tag) == "definition" and el.text:
            return el.text.strip()
    return ""


def _rule_inputs_of(inner: ET.Element) -> list[dict[str, Any]]:
    out = []
    for el in inner.iter():
        if strip_ns(el.tag) != "ruleInput":
            continue
        out.append({
            "name": get_attr_any(el, "name") or find_first_text(el, "name"),
            "type": get_attr_any(el, "type") or find_first_text(el, "type", "typeName"),
            "required": _to_bool(get_attr_any(el, "required")),
        })
    return out


def _sail_references(
    sail: str,
    own_name: str | None,
    uuid_to_name: dict[str, str],
    type_by_name: dict[str, str] | None = None,
) -> dict[str, list[str]]:
    """Extrae las referencias salientes de una expresion SAIL, POR TIPO.

    En Appian el prefijo `rule!` sirve para expression rules, interfaces Y
    decisions. Devolver todo en una sola lista `referencedRules` hacia que el
    agente enlazara interfaces al catalogo de reglas (enlace muerto), asi que
    se desambigua contra el inventario con la MISMA precedencia que cmd_graph:
    expressionRule -> interface -> decision.

    `referencedUnresolved` es obligatorio: un `rule!X` que no esta en el
    inventario es una dependencia no exportada (riesgo real). Sin ese bucket
    desapareceria en silencio al filtrar.
    """
    type_by_name = type_by_name or {}
    buckets: dict[str, list[str]] = {
        "referencedRules": [],
        "referencedInterfaces": [],
        "referencedDecisions": [],
        "referencedUnresolved": [],
        "referencedRecordTypes": [],
    }
    bucket_of = {
        "expressionRule": "referencedRules",
        "interface": "referencedInterfaces",
        "decision": "referencedDecisions",
    }
    for m in REF_PATTERNS["expressionRule"].finditer(sail):
        nm = m.group(1)
        if nm == own_name:
            continue
        key = bucket_of.get(type_by_name.get(nm, ""), "referencedUnresolved")
        if nm not in buckets[key]:
            buckets[key].append(nm)
    for pat in (RT_FIELD_UUID_RE, REF_PATTERNS["uuidRecordType"]):
        for m in pat.finditer(sail):
            nm = uuid_to_name.get(m.group(1), m.group(1))
            if nm not in buckets["referencedRecordTypes"]:
                buckets["referencedRecordTypes"].append(nm)
    return buckets


def cmd_detail(root: Path, inventory: dict[str, Any]) -> dict[str, Any]:
    objects = inventory.get("objects", {})
    uuid_to_name = {
        o["uuid"]: o["name"]
        for objs in objects.values()
        if isinstance(objs, list)
        for o in objs
        if isinstance(o, dict) and o.get("uuid") and o.get("name")
    }
    # Precedencia identica a cmd_graph para resolver `rule!X`: una interfaz y
    # una expression rule pueden llamarse igual, y el grafo y el detalle no
    # deben discrepar nunca.
    type_by_name: dict[str, str] = {}
    for obj_type in ("decision", "interface", "expressionRule"):
        for o in objects.get(obj_type, []):
            if isinstance(o, dict) and o.get("name"):
                type_by_name[o["name"]] = obj_type

    detail: dict[str, dict[str, Any]] = {
        "recordTypes": {},
        "interfaces": {},
        "expressionRules": {},
        "processModels": {},
        "decisions": {},
        "constants": {},
        "dataStores": {},
        "sites": {},
        "cdts": {},
    }

    for o in objects.get("recordType", []):
        inner = _haul_inner(Path(o["path"]))
        if inner is None:
            continue
        entry: dict[str, Any] = {"uuid": o.get("uuid"), "path": o["path"], "fields": [], "relationships": [], "views": [], "actions": []}
        for el in inner.iter():
            tag = strip_ns(el.tag)
            if tag == "field":
                entry["fields"].append({
                    "name": get_attr_any(el, "name"),
                    "type": get_attr_any(el, "type"),
                    "required": _to_bool(get_attr_any(el, "required")),
                })
            elif tag == "relationship":
                entry["relationships"].append({
                    "name": get_attr_any(el, "name"),
                    "target": get_attr_any(el, "target", "targetRecordType"),
                    "type": get_attr_any(el, "type", "relationshipType"),
                })
            elif tag in ("view", "recordView"):
                nm = get_attr_any(el, "name")
                if nm:
                    entry["views"].append(nm)
            elif tag in ("action", "recordAction", "relatedAction"):
                nm = get_attr_any(el, "name")
                if nm:
                    entry["actions"].append(nm)
        detail["recordTypes"][o["name"]] = entry

    for section, obj_type in (("interfaces", "interface"), ("expressionRules", "expressionRule")):
        for o in objects.get(obj_type, []):
            inner = _haul_inner(Path(o["path"]))
            if inner is None:
                continue
            sail = mask_sail(_sail_of(inner))
            refs = _sail_references(sail, o.get("name"), uuid_to_name, type_by_name)
            detail[section][o["name"]] = {
                "uuid": o.get("uuid"),
                "path": o["path"],
                "ruleInputs": _rule_inputs_of(inner),
                **refs,
                "sail": sail,
            }

    for o in objects.get("processModel", []):
        inner = _haul_inner(Path(o["path"]))
        if inner is None:
            continue
        pvs: list[dict[str, Any]] = []
        for container in inner.iter():
            if strip_ns(container.tag) not in ("processVariables", "pvs"):
                continue
            for var in container:
                if strip_ns(var.tag) not in ("variable", "pv", "processVariable"):
                    continue
                pvs.append({
                    "name": get_attr_any(var, "name") or find_first_text(var, "name"),
                    "type": get_attr_any(var, "type") or find_first_text(var, "type-name", "type", "typeName"),
                    "isParameter": _to_bool(get_attr_any(var, "parameter") or find_first_text(var, "parameter")),
                })
        nodes: list[dict[str, Any]] = []
        for el in inner.iter():
            if strip_ns(el.tag) != "node":
                continue
            node: dict[str, Any] = {
                "id": get_attr_any(el, "id", "uuid"),
                "name": get_attr_any(el, "name") or find_first_text(el, "name", max_depth=2),
                "type": get_attr_any(el, "type"),
            }
            assignees = find_first_text(el, "assignees", "assignee", max_depth=2)
            if assignees:
                node["assignees"] = assignees
            expr = find_first_text(el, "expression", "condition", "outputExpr", max_depth=2)
            if expr:
                node["expressionSummary"] = mask_sail(expr)[:300]
            form = find_first_text(el, "form", max_depth=2)
            if form:
                node["form"] = form
            nodes.append(node)
        detail["processModels"][o["name"]] = {
            "uuid": o.get("uuid"),
            "path": o["path"],
            "processVariables": pvs,
            "nodes": nodes,
        }

    for o in objects.get("decision", []):
        inner = _haul_inner(Path(o["path"]))
        if inner is None:
            continue
        entry = {"uuid": o.get("uuid"), "path": o["path"], "inputs": [], "outputs": [], "rows": []}
        for el in inner.iter():
            tag = strip_ns(el.tag)
            if tag == "input":
                entry["inputs"].append({"name": get_attr_any(el, "name"), "type": get_attr_any(el, "type")})
            elif tag == "output":
                entry["outputs"].append({"name": get_attr_any(el, "name"), "type": get_attr_any(el, "type")})
            elif tag == "row":
                conditions = [
                    (c.text or "").strip()
                    for c in el
                    if strip_ns(c.tag) == "condition"
                ]
                result = next(
                    ((c.text or "").strip() for c in el if strip_ns(c.tag) == "result"),
                    None,
                )
                entry["rows"].append({"conditions": conditions, "result": result})
        detail["decisions"][o["name"]] = entry

    for o in objects.get("constant", []):
        detail["constants"][o["name"]] = {
            "uuid": o.get("uuid"),
            "path": o["path"],
            "value": o.get("value"),
            "typeRef": o.get("typeRef"),
            "maskedSecret": o.get("maskedSecret", False),
        }

    for o in objects.get("dataStore", []):
        inner = _haul_inner(Path(o["path"]))
        if inner is None:
            continue
        entities = [
            {"name": get_attr_any(el, "name"), "cdt": get_attr_any(el, "cdt", "type", "typeRef")}
            for el in inner.iter()
            if strip_ns(el.tag) == "entity"
        ]
        detail["dataStores"][o["name"]] = {"uuid": o.get("uuid"), "path": o["path"], "entities": entities}

    # Sites: paginas con su objeto destino. Sin esto, la ficha de navegacion
    # del nivel 3 no tendria datos y el agente se inventaria las paginas.
    for o in objects.get("site", []):
        inner = _haul_inner(Path(o["path"]))
        if inner is None:
            continue
        pages: list[dict[str, Any]] = []
        for el in inner.iter():
            if strip_ns(el.tag) not in ("page", "sitePage"):
                continue
            target_uuid = (
                get_attr_any(el, "objectUuid", "uuid", "targetUuid")
                or find_first_text(el, "objectUuid", "targetUuid", "uuid", max_depth=3)
            )
            pages.append({
                "name": get_attr_any(el, "name") or find_first_text(el, "name", max_depth=2),
                "type": get_attr_any(el, "type", "pageType")
                or find_first_text(el, "type", "pageType", max_depth=2),
                "target": uuid_to_name.get(target_uuid or "", target_uuid),
                "urlStub": get_attr_any(el, "urlStub") or find_first_text(el, "urlStub", max_depth=2),
            })
        detail["sites"][o["name"]] = {
            "uuid": o.get("uuid"),
            "path": o["path"],
            "pages": pages,
            "groups": [
                g for g in (find_first_text(inner, "visibilityGroup", "group"),) if g
            ],
        }

    for o in objects.get("cdt", []):
        xsd_root = safe_parse(Path(o["path"]))
        if xsd_root is None:
            continue
        fields = []
        for el in xsd_root.iter():
            if strip_ns(el.tag) != "element" or "name" not in el.attrib:
                continue
            ftype = get_attr_any(el, "type") or ""
            if ":" in ftype:
                ftype = ftype.split(":", 1)[1]
            min_occurs = el.attrib.get("minOccurs", "1")
            fields.append({
                "name": el.attrib["name"],
                "type": ftype,
                "required": min_occurs != "0",
            })
        detail["cdts"][o["name"]] = {"path": o["path"], "fields": fields}

    counts = {k: len(v) for k, v in detail.items()}
    return {"counts": counts, **detail}


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--check", metavar="RUTA")
    g.add_argument("--inventory", metavar="RUTA")
    g.add_argument("--graph", metavar="RUTA")
    g.add_argument("--all", metavar="RUTA")
    g.add_argument("--detail", metavar="RUTA")
    ap.add_argument("--out", metavar="FICHERO")
    ap.add_argument("--out-dir", metavar="DIR")
    args = ap.parse_args(argv)
    target = args.check or args.inventory or args.graph or args.all or args.detail
    root = Path(target).resolve()
    if not root.exists():
        print(f"ERROR: la ruta {root} no existe", file=sys.stderr)
        return 2
    if args.check:
        return cmd_check(root)
    if args.inventory:
        inv = cmd_inventory(root)
        data = json.dumps(inv, indent=2, ensure_ascii=False, default=str)
        if args.out:
            Path(args.out).write_text(data, encoding="utf-8")
            print(f"Inventario escrito en {args.out} ({inv['counts']})")
        else:
            print(data)
        return 0
    if args.graph:
        inv = cmd_inventory(root)
        graph = cmd_graph(root, inv)
        data = json.dumps(graph, indent=2, ensure_ascii=False, default=str)
        if args.out:
            Path(args.out).write_text(data, encoding="utf-8")
            print(f"Grafo escrito en {args.out} (nodos={graph['stats']['nodeCount']}, aristas={graph['stats']['edgeCount']})")
        else:
            print(data)
        return 0
    if args.all:
        if not args.out_dir:
            print("ERROR: --all requiere --out-dir", file=sys.stderr)
            return 2
        out_dir = Path(args.out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        inv = cmd_inventory(root)
        (out_dir / "inventory.json").write_text(
            json.dumps(inv, indent=2, ensure_ascii=False, default=str), encoding="utf-8"
        )
        graph = cmd_graph(root, inv)
        (out_dir / "graph.json").write_text(
            json.dumps(graph, indent=2, ensure_ascii=False, default=str), encoding="utf-8"
        )
        print(f"Escritos: {out_dir / 'inventory.json'} y {out_dir / 'graph.json'}")
        print(f"Inventario: {inv['counts']}")
        print(f"Grafo: nodos={graph['stats']['nodeCount']}, aristas={graph['stats']['edgeCount']}, huerfanos={graph['stats']['orphanCount']}, hubs={graph['stats']['hubCount']}, ciclos={graph['stats']['cycleCount']}")
        return 0
    if args.detail:
        inv = cmd_inventory(root)
        detail = cmd_detail(root, inv)
        out_path = Path(args.out) if args.out else root / "_doc_generada" / "_intermedio" / "detail.json"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(
            json.dumps(detail, indent=2, ensure_ascii=False, default=str), encoding="utf-8"
        )
        print(f"Detalle escrito en {out_path} ({detail['counts']})")
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
