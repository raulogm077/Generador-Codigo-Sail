#!/usr/bin/env python3
"""
build_summary.py - Consolida inventory.json + graph.json + hallazgos en un summary.json
normalizado que consumen los publishers PDF/Dashboard.

Uso:
  python3 build_summary.py <ruta_doc_generada>

Lee:
  <ruta>/_intermedio/inventory.json
  <ruta>/_intermedio/graph.json
  <ruta>/<seccion>.md  (opcional; si existen, extrae hallazgos top)

Escribe:
  <ruta>/_intermedio/summary.json
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def load_json(p: Path) -> dict:
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))


def confidence_label(orphan_ratio: float, parse_errors: int, has_application: bool) -> str:
    if not has_application or orphan_ratio > 0.8:
        return "Bajo"
    if orphan_ratio > 0.5 or parse_errors > 5:
        return "Medio"
    return "Alto"


def extract_findings_from_md(md_text: str, severity_emojis: dict[str, str]) -> list[dict]:
    """Busca lineas con emoji de severidad (rojo/amarillo) y extrae el hallazgo."""
    findings = []
    for line in md_text.splitlines():
        for emoji, severity in severity_emojis.items():
            if emoji in line:
                cleaned = re.sub(r"^[\s\-\*\d\.]+", "", line).strip()
                if len(cleaned) > 20 and len(cleaned) < 300:
                    findings.append({"severity": severity, "text": cleaned[:280]})
                break
    return findings


def main(doc_root: str) -> int:
    root = Path(doc_root).resolve()
    interm = root / "_intermedio"
    if not interm.exists():
        print(f"ERROR: no existe {interm}", file=sys.stderr)
        return 2

    inv = load_json(interm / "inventory.json")
    graph = load_json(interm / "graph.json")

    counts = inv.get("counts", {})
    objects = inv.get("objects", {})

    # Meta de la app
    app_list = objects.get("application", [])
    app_meta = app_list[0] if app_list else {}

    # Hubs ordenados
    hubs = graph.get("hubs", [])[:10]

    # Confianza
    total_nodes = graph.get("stats", {}).get("nodeCount", 0) or 1
    orphan_count = graph.get("stats", {}).get("orphanCount", 0)
    orphan_ratio = orphan_count / total_nodes if total_nodes else 0
    parse_errors = inv.get("parseErrors", 0)
    confidence = confidence_label(orphan_ratio, parse_errors, bool(app_list))

    # Procesos criticos: PMs con mas grado entrante o que llaman integraciones
    pm_objs = objects.get("processModel", [])
    pm_by_id = {p.get("uuid") or f"processModel::{p.get('name')}": p for p in pm_objs}
    edges = graph.get("edges", [])
    pm_indegree = Counter()
    pm_calls_integrations = Counter()
    for e in edges:
        # OJO con el nombre: cmd_graph emite "subprocess" en minusculas. Escrito
        # "subProcess", este filtro no casaba nunca y los PM invocados como
        # subproceso salian con grado entrante 0 en el resumen.
        if e["target"] in pm_by_id and e["refType"] in ("startProcess", "subprocess", "recordAction"):
            pm_indegree[e["target"]] += 1
        if e["source"] in pm_by_id and e["refType"] == "integrationCall":
            pm_calls_integrations[e["source"]] += 1
    critical_processes = []
    for pm_id, pm in pm_by_id.items():
        score = pm_indegree.get(pm_id, 0) * 2 + pm_calls_integrations.get(pm_id, 0) * 3
        if pm.get("hasRecurrence"):
            score += 5
        if score >= 3:
            critical_processes.append({
                "id": pm_id,
                "name": pm.get("name"),
                "score": score,
                "calledBy": pm_indegree.get(pm_id, 0),
                "callsIntegrations": pm_calls_integrations.get(pm_id, 0),
                "isBatch": bool(pm.get("hasRecurrence")),
                "userTaskCount": pm.get("userTaskCount", 0),
            })
    critical_processes.sort(key=lambda x: -x["score"])
    critical_processes = critical_processes[:10]

    # Integraciones por sistema externo
    integrations = []
    for it in objects.get("integration", []):
        integrations.append({
            "name": it.get("name"),
            "method": it.get("method"),
            "endpoint": it.get("endpoint"),
            "connectedSystemRef": it.get("connectedSystemRef"),
        })

    # Riesgos basicos detectables sin LLM
    risks = []
    # Constants que parecen secretos
    masked_constants = [c for c in objects.get("constant", []) if c.get("maskedSecret")]
    if masked_constants:
        risks.append({
            "severity": "high",
            "category": "security",
            "title": f"{len(masked_constants)} constantes parecen contener secretos",
            "evidence": [c.get("name") for c in masked_constants[:5]],
        })
    # PMs sin user tasks ni recurrencia (huerfanos posibles)
    pms_silent = [p for p in pm_objs if not p.get("hasRecurrence") and (p.get("userTaskCount", 0) == 0)]
    if len(pms_silent) > 10:
        risks.append({
            "severity": "medium",
            "category": "complexity",
            "title": f"{len(pms_silent)} process models sin tareas humanas ni recurrencia (posibles utilities o huerfanos)",
            "evidence": [p.get("name") for p in pms_silent[:5]],
        })
    # Interfaces muy grandes
    big_interfaces = sorted(
        [i for i in objects.get("interface", []) if i.get("sailBytes", 0) > 80000],
        key=lambda x: -x.get("sailBytes", 0)
    )[:5]
    if big_interfaces:
        risks.append({
            "severity": "medium",
            "category": "maintainability",
            "title": f"{len(big_interfaces)} interfaces muy grandes (>80KB de SAIL) - dificiles de mantener",
            "evidence": [f"{i.get('name')} ({i.get('sailBytes', 0)//1024}KB)" for i in big_interfaces],
        })

    # Hallazgos desde los .md generados (si existen)
    md_findings: list[dict] = []
    severity_map = {"🔴": "high", "🟡": "medium", "🔵": "low"}
    for md_name in ["09-valor-adicional.md", "04-seguridad-grupos.md", "05-integraciones-consumidas.md"]:
        md_path = root / md_name
        if md_path.exists():
            md_findings.extend(extract_findings_from_md(md_path.read_text(encoding="utf-8"), severity_map))
    md_findings = md_findings[:30]

    # Layered architecture breakdown
    layer_breakdown = {
        "Presentacion": counts.get("site", 0) + counts.get("interface", 0),
        "Logica": counts.get("processModel", 0) + counts.get("expressionRule", 0) + counts.get("decision", 0),
        "Datos": counts.get("recordType", 0) + counts.get("cdt", 0),
        "Integracion": counts.get("integration", 0) + counts.get("connectedSystem", 0) + counts.get("webApi", 0),
        "Seguridad": counts.get("group", 0),
    }

    summary = {
        "meta": {
            "appName": app_meta.get("name", "?"),
            "appPrefix": app_meta.get("prefix"),
            "appDescription": app_meta.get("description"),
            "appUuid": app_meta.get("uuid"),
            "generatedAt": datetime.now(timezone.utc).isoformat(),
            "confidence": confidence,
        },
        "counts": counts,
        "totals": {
            "objects": sum(counts.values()),
            "nodes": total_nodes,
            "edges": graph.get("stats", {}).get("edgeCount", 0),
            "hubs": len(hubs),
            "orphans": orphan_count,
        },
        "layerBreakdown": layer_breakdown,
        "hubs": [{"name": h.get("name"), "type": h.get("type"), "inDegree": h.get("in")} for h in hubs],
        "criticalProcesses": critical_processes,
        "integrations": integrations,
        "risks": risks,
        "findingsFromMd": md_findings,
        "objects": {
            t: [
                {k: o.get(k) for k in ("name", "description", "uuid", "type", "haulType")
                 if o.get(k) is not None}
                for o in objs
            ]
            for t, objs in objects.items()
        },
    }

    out_path = interm / "summary.json"
    out_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    print(f"Summary escrito en {out_path}")
    print(f"  App: {summary['meta']['appName']}")
    print(f"  Objetos: {summary['totals']['objects']}")
    print(f"  Confianza: {summary['meta']['confidence']}")
    print(f"  Procesos criticos: {len(critical_processes)}")
    print(f"  Riesgos detectados: {len(risks)}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 build_summary.py <ruta_doc_generada>", file=sys.stderr)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
