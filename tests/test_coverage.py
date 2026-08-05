# -*- coding: utf-8 -*-
"""Tests del gate de cobertura (Task 4: scripts/check_coverage.py).

Compatibles con `python -m unittest tests/test_coverage.py -v` y con pytest.
Autocontenidos: construyen una `_doc_generada` sintetica minima en un tmpdir
propio (nombres DEMO_*, UUIDs 00000000-*). No dependen del fixture mini-export
ni de la salida de otros scripts.

Contrato verificado (plan 2026-08-04-reverse-engineering-rebuild-spec, Task 4):
- `python check_coverage.py {ruta_salida} --mode onboarding|rebuild`
- Escribe `{ruta_salida}/_intermedio/coverage.json`.
- Exit 0 si la cobertura requerida es 100%; exit 1 si falta algo; exit 2 si
  error de uso/IO (p. ej. no existe inventory.json).
- Modo onboarding: exige 100% de recordType, cdt, processModel, integration,
  webApi, group y dataStore; interfaces/rules solo se reportan (informativo).
- Modo rebuild: exige ademas interface, expressionRule, decision, constant y
  site — cada uno debe aparecer en `10-especificacion/` (sin contar
  trazabilidad.md) o estar en trazabilidad.md marcado `DESCARTADO: {motivo}`.
- Matching por nombre tecnico exacto (con limites de palabra) y por UUID como
  fallback.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = (
    Path(__file__).parents[1]
    / "skills"
    / "appian-reverse-engineering"
    / "scripts"
    / "check_coverage.py"
)

UUID_RT_1 = "00000000-0000-0000-0000-000000000101"
UUID_RT_2 = "00000000-0000-0000-0000-000000000102"
UUID_IFC = "00000000-0000-0000-0000-000000000201"
UUID_IFC_2 = "00000000-0000-0000-0000-000000000202"
UUID_ER = "00000000-0000-0000-0000-000000000301"


def obj(obj_type: str, name: str, uuid: str) -> dict:
    """Metadato minimo con la misma forma que produce parse_export.py."""
    return {
        "type": obj_type,
        "name": name,
        "uuid": uuid,
        "path": obj_type + "/" + name + ".xml",
    }


class CoverageTestCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)

    # ---------- helpers ----------

    def make_doc(self, objects, docs) -> Path:
        """Crea {tmp}/_doc_generada con _intermedio/inventory.json y los .md dados.

        `objects`: dict tipo -> lista de metadatos (forma actual del parser) o
        lista plana de metadatos. `docs`: dict ruta-relativa -> contenido md.
        """
        doc = self.tmp / "_doc_generada"
        (doc / "_intermedio").mkdir(parents=True)
        if isinstance(objects, dict):
            counts = {k: len(v) for k, v in objects.items()}
        else:
            counts = {}
        inventory = {"counts": counts, "objects": objects, "parseErrors": 0}
        (doc / "_intermedio" / "inventory.json").write_text(
            json.dumps(inventory), encoding="utf-8"
        )
        for rel, text in docs.items():
            p = doc / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(text, encoding="utf-8")
        return doc

    def run_gate(self, doc: Path, mode: str):
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), str(doc), "--mode", mode],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        cov_path = doc / "_intermedio" / "coverage.json"
        coverage = None
        if cov_path.exists():
            coverage = json.loads(cov_path.read_text(encoding="utf-8"))
        return proc, coverage

    # ---------- modo onboarding ----------

    def test_onboarding_rt_sin_documentar_exit_1(self):
        """1 RT documentado y 1 sin documentar -> exit 1 y missing exacto."""
        doc = self.make_doc(
            {
                "recordType": [
                    obj("recordType", "DEMO_RT_Solicitud", UUID_RT_1),
                    obj("recordType", "DEMO_RT_Olvidado", UUID_RT_2),
                ]
            },
            {
                "03-modelo-datos.md": (
                    "# Modelo de datos\n\n"
                    "El record `DEMO_RT_Solicitud` guarda las solicitudes.\n"
                )
            },
        )
        proc, coverage = self.run_gate(doc, "onboarding")
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        self.assertIsNotNone(coverage)
        self.assertIn("DEMO_RT_Olvidado", coverage["missing"]["recordType"])
        self.assertNotIn("DEMO_RT_Solicitud", coverage["missing"]["recordType"])
        # La salida legible lista exactamente lo que falta.
        self.assertIn("DEMO_RT_Olvidado", proc.stdout)

    def test_onboarding_todo_documentado_exit_0(self):
        doc = self.make_doc(
            {
                "recordType": [
                    obj("recordType", "DEMO_RT_Solicitud", UUID_RT_1),
                    obj("recordType", "DEMO_RT_Olvidado", UUID_RT_2),
                ],
                # Entradas sin "name" (p. ej. icf) no deben romper el script.
                "icf": [{"path": "a/import-customization-file.properties", "size": 10}],
            },
            {
                "03-modelo-datos.md": (
                    "Records: `DEMO_RT_Solicitud` y `DEMO_RT_Olvidado`.\n"
                )
            },
        )
        proc, coverage = self.run_gate(doc, "onboarding")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertEqual(coverage["missing"], {})

    def test_onboarding_interfaces_solo_informativas(self):
        """Una interface sin documentar NO hace fallar el modo onboarding."""
        doc = self.make_doc(
            {
                "recordType": [obj("recordType", "DEMO_RT_Solicitud", UUID_RT_1)],
                "interface": [obj("interface", "DEMO_IFC_Form", UUID_IFC)],
            },
            {"03-modelo-datos.md": "`DEMO_RT_Solicitud`\n"},
        )
        proc, coverage = self.run_gate(doc, "onboarding")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertNotIn("interface", coverage["missing"])
        # Pero la tabla documentados/total si la reporta (0/1).
        self.assertIn("0/1", proc.stdout)
        self.assertIn("interface", proc.stdout)

    def test_uuid_como_fallback(self):
        """Si el nombre no aparece pero si su UUID, cuenta como documentado."""
        doc = self.make_doc(
            {"recordType": [obj("recordType", "DEMO_RT_Solicitud", UUID_RT_1)]},
            {"03-modelo-datos.md": "Record principal: `" + UUID_RT_1 + "`\n"},
        )
        proc, coverage = self.run_gate(doc, "onboarding")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertEqual(coverage["missing"], {})

    def test_nombre_exacto_no_por_prefijo(self):
        """`DEMO_RT_Sol` no se da por documentado porque aparezca DEMO_RT_Solicitud."""
        doc = self.make_doc(
            {"recordType": [obj("recordType", "DEMO_RT_Sol", UUID_RT_1)]},
            {"03-modelo-datos.md": "Aqui solo se habla de `DEMO_RT_Solicitud`.\n"},
        )
        proc, coverage = self.run_gate(doc, "onboarding")
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        self.assertIn("DEMO_RT_Sol", coverage["missing"]["recordType"])

    def test_inventory_objects_como_lista(self):
        """Acepta tambien `objects` como lista plana (forma alternativa)."""
        doc = self.make_doc(
            [
                obj("recordType", "DEMO_RT_Solicitud", UUID_RT_1),
                obj("dataStore", "DEMO_DS_Principal", UUID_RT_2),
            ],
            {
                "03-modelo-datos.md": (
                    "`DEMO_RT_Solicitud` persiste en `DEMO_DS_Principal`.\n"
                )
            },
        )
        proc, coverage = self.run_gate(doc, "onboarding")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertEqual(coverage["missing"], {})

    # ---------- modo rebuild ----------

    def test_rebuild_interface_fuera_de_especificacion_exit_1(self):
        """En rebuild, mencion en 00-09 o fila DOCUMENTADO en trazabilidad no bastan:
        la interface debe tener ficha en 10-especificacion/."""
        doc = self.make_doc(
            {
                "recordType": [obj("recordType", "DEMO_RT_Solicitud", UUID_RT_1)],
                "interface": [obj("interface", "DEMO_IFC_Form", UUID_IFC)],
            },
            {
                "03-modelo-datos.md": "`DEMO_RT_Solicitud`\n",
                "02-arquitectura.md": "La pantalla DEMO_IFC_Form consulta el record.\n",
                "10-especificacion/trazabilidad.md": (
                    "| Objeto (tipo) | Caso de uso | Historias | Spec | Estado |\n"
                    "|---|---|---|---|---|\n"
                    "| DEMO_IFC_Form (interface) | CU-01 | HU-001 | pantallas | DOCUMENTADO |\n"
                ),
            },
        )
        proc, coverage = self.run_gate(doc, "rebuild")
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        self.assertIn("DEMO_IFC_Form", coverage["missing"]["interface"])

    def test_rebuild_ficha_en_especificacion_exit_0(self):
        doc = self.make_doc(
            {
                "recordType": [obj("recordType", "DEMO_RT_Solicitud", UUID_RT_1)],
                "interface": [obj("interface", "DEMO_IFC_Form", UUID_IFC)],
            },
            {
                "03-modelo-datos.md": "`DEMO_RT_Solicitud`\n",
                "10-especificacion/pantallas/DEMO_IFC_Form.md": (
                    "# Pantalla: Formulario (`DEMO_IFC_Form`)\n"
                ),
            },
        )
        proc, coverage = self.run_gate(doc, "rebuild")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertEqual(coverage["missing"], {})

    def test_rebuild_mencion_cruzada_no_cuenta_como_ficha(self):
        """Regresion: una interfaz SOLO mencionada por otras fichas no esta documentada.

        Antes, `spec_blob` concatenaba todos los .md de 10-especificacion/, asi que
        bastaba con que el indice o la ficha de otra pantalla la nombraran para darla
        por cubierta — el gate pasaba en verde sin su ficha.
        """
        doc = self.make_doc(
            {
                "recordType": [obj("recordType", "DEMO_RT_Solicitud", UUID_RT_1)],
                "interface": [
                    obj("interface", "DEMO_IFC_Form", UUID_IFC),
                    obj("interface", "DEMO_IFC_List", UUID_IFC_2),
                ],
            },
            {
                "03-modelo-datos.md": "`DEMO_RT_Solicitud`\n",
                # Form SI tiene ficha propia, y menciona a List (la invoca).
                "10-especificacion/pantallas/DEMO_IFC_Form.md": (
                    "# Pantalla: Formulario (`DEMO_IFC_Form`)\n"
                    "\n## Reglas invocadas\n"
                    "| `DEMO_IFC_List` | listado embebido |\n"
                ),
                # El indice tambien la nombra, pero eso no es una ficha.
                "10-especificacion/pantallas/indice.md": (
                    "# Indice\n\n| Pantalla |\n| `DEMO_IFC_Form` |\n| `DEMO_IFC_List` |\n"
                ),
            },
        )
        proc, coverage = self.run_gate(doc, "rebuild")
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        self.assertIn("DEMO_IFC_List", coverage["missing"].get("interface", []))
        self.assertNotIn("DEMO_IFC_Form", coverage["missing"].get("interface", []))

    def test_rebuild_ficha_por_cabecera_cuenta(self):
        """Una rule con su seccion `## rule!X` en reglas-catalogo.md SI esta documentada."""
        doc = self.make_doc(
            {
                "recordType": [obj("recordType", "DEMO_RT_Solicitud", UUID_RT_1)],
                "expressionRule": [obj("expressionRule", "DEMO_VAL_Importe", UUID_IFC)],
            },
            {
                "03-modelo-datos.md": "`DEMO_RT_Solicitud`\n",
                "10-especificacion/reglas-catalogo.md": (
                    "# Catalogo de reglas\n\n"
                    "## rule!DEMO_VAL_Importe\n"
                    "**Firma**: importe -> Text\n"
                ),
            },
        )
        proc, coverage = self.run_gate(doc, "rebuild")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertEqual(coverage["missing"], {})

    def test_rebuild_descartado_en_trazabilidad_cuenta(self):
        """Una rule muerta marcada `DESCARTADO: {motivo}` cuenta como cubierta."""
        doc = self.make_doc(
            {
                "recordType": [obj("recordType", "DEMO_RT_Solicitud", UUID_RT_1)],
                "expressionRule": [obj("expressionRule", "DEMO_VAL_Muerta", UUID_ER)],
            },
            {
                "03-modelo-datos.md": "`DEMO_RT_Solicitud`\n",
                "10-especificacion/trazabilidad.md": (
                    "| Objeto (tipo) | Caso de uso | Historias | Spec | Estado |\n"
                    "|---|---|---|---|---|\n"
                    "| DEMO_VAL_Muerta (expressionRule) | - | - | - | "
                    "DESCARTADO: objeto muerto sin callers |\n"
                ),
            },
        )
        proc, coverage = self.run_gate(doc, "rebuild")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertNotIn("expressionRule", coverage["missing"])

    def test_rebuild_descartado_sin_motivo_no_cuenta(self):
        """`DESCARTADO:` sin motivo no vale (el plan exige DESCARTADO: {motivo})."""
        doc = self.make_doc(
            {
                "recordType": [obj("recordType", "DEMO_RT_Solicitud", UUID_RT_1)],
                "expressionRule": [obj("expressionRule", "DEMO_VAL_Muerta", UUID_ER)],
            },
            {
                "03-modelo-datos.md": "`DEMO_RT_Solicitud`\n",
                "10-especificacion/trazabilidad.md": (
                    "| DEMO_VAL_Muerta (expressionRule) | - | - | - | DESCARTADO: |\n"
                ),
            },
        )
        proc, coverage = self.run_gate(doc, "rebuild")
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        self.assertIn("DEMO_VAL_Muerta", coverage["missing"]["expressionRule"])

    # ---------- errores de uso ----------

    def test_sin_inventory_exit_2(self):
        doc = self.tmp / "_doc_generada"
        doc.mkdir()
        proc, coverage = self.run_gate(doc, "onboarding")
        self.assertEqual(proc.returncode, 2, proc.stdout + proc.stderr)
        self.assertIsNone(coverage)


if __name__ == "__main__":
    unittest.main()
