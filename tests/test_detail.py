# tests/test_detail.py — Task 3: extraccion estructurada para el Nivel 3 (--detail).
# Fixture 100% sintetico (DEMO_*, UUIDs 00000000-*). Corre con `python -m unittest tests/test_detail.py -v`.
import json
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

FIXTURE = Path(__file__).parent / "fixtures" / "mini-export"
SCRIPT = Path(__file__).parents[1] / "skills" / "appian-reverse-engineering" / "scripts" / "parse_export.py"
OUT = FIXTURE / "_doc_generada" / "_intermedio"


class TestDetail(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.out = OUT
        # --all requiere --out-dir; --detail escribe _doc_generada/_intermedio/detail.json por defecto
        subprocess.run(
            [sys.executable, str(SCRIPT), "--all", str(FIXTURE), "--out-dir", str(OUT)],
            check=True,
        )
        subprocess.run(
            [sys.executable, str(SCRIPT), "--detail", str(FIXTURE)],
            check=True,
        )
        cls.detail = json.loads((OUT / "detail.json").read_text(encoding="utf-8"))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(FIXTURE / "_doc_generada", ignore_errors=True)

    # --- Los 4 asserts del plan ---

    def test_record_type_fields(self):
        # Nombre tecnico real del RT en el fixture: "DEMO Solicitud" (asi lo referencia el SAIL)
        rt = self.detail["recordTypes"]["DEMO Solicitud"]
        names = [f["name"] for f in rt["fields"]]
        self.assertIn("estado", names)

    def test_interface_rule_inputs(self):
        ifc = self.detail["interfaces"]["DEMO_IFC_SolicitudForm"]
        self.assertIn("importe", [ri["name"] for ri in ifc["ruleInputs"]])
        self.assertIn("DEMO_VAL_ValidarImporte", ifc["referencedRules"])

    # --- M4: referencias desambiguadas por tipo ---

    def test_referenced_rules_excluye_interfaces(self):
        """En Appian una interfaz se invoca con `rule!`, pero NO es una regla:
        colarla en referencedRules generaba enlaces muertos al catalogo."""
        ifc = self.detail["interfaces"]["DEMO_IFC_SolicitudForm"]
        self.assertNotIn("DEMO_IFC_SolicitudList", ifc["referencedRules"])

    def test_referenced_interfaces_capturadas(self):
        ifc = self.detail["interfaces"]["DEMO_IFC_SolicitudForm"]
        self.assertIn("DEMO_IFC_SolicitudList", ifc["referencedInterfaces"])

    def test_buckets_de_referencias_existen_siempre(self):
        """Las 4 claves deben estar aunque esten vacias: un consumidor que haga
        entry["referencedDecisions"] no puede reventar con KeyError."""
        for section in ("interfaces", "expressionRules"):
            for name, entry in self.detail[section].items():
                for key in (
                    "referencedRules",
                    "referencedInterfaces",
                    "referencedDecisions",
                    "referencedUnresolved",
                    "referencedRecordTypes",
                ):
                    self.assertIn(key, entry, f"{section}.{name} sin {key}")
                    self.assertIsInstance(entry[key], list)

    def test_seccion_sites_existe(self):
        self.assertIn("sites", self.detail)
        self.assertIsInstance(self.detail["sites"], dict)

    def test_site_con_sus_paginas(self):
        site = self.detail["sites"]["DEMO_SITE_Solicitudes"]
        paginas = {p["name"]: p for p in site["pages"]}
        self.assertEqual(len(paginas), 2)
        self.assertEqual(paginas["Solicitudes"]["type"], "RECORD_LIST")
        # El objeto destino se resuelve de UUID a nombre tecnico.
        self.assertEqual(paginas["Solicitudes"]["target"], "DEMO Solicitud")
        self.assertEqual(paginas["Nueva solicitud"]["target"], "DEMO_IFC_SolicitudForm")

    # --- I5/M6: el PM batch con prefijo de namespace ---

    def test_pm_con_namespace_se_parsea(self):
        """Si faltara el xmlns:a, ET.parse fallaria y el PM desapareceria del
        inventario EN SILENCIO (parseErrors lo delata)."""
        inv = json.loads((self.out / "inventory.json").read_text(encoding="utf-8"))
        self.assertEqual(inv["parseErrors"], 0)
        pm = self.detail["processModels"]["DEMO_PM_ReintentarEnvios"]
        self.assertEqual(len(pm["nodes"]), 7)
        b1 = next(n for n in pm["nodes"] if n["id"] == "b1")
        self.assertIn("a!queryEntity", b1.get("expressionSummary") or "")

    def test_batch_pm_es_timer_con_recurrence(self):
        inv = json.loads((self.out / "inventory.json").read_text(encoding="utf-8"))
        pm = next(
            o for o in inv["objects"]["processModel"]
            if o["name"] == "DEMO_PM_ReintentarEnvios"
        )
        self.assertEqual(pm["startType"], "timer")
        self.assertTrue(pm.get("hasRecurrence"))
        self.assertEqual(pm["subProcessCount"], 1)

    def test_pm_process_variables(self):
        pm = self.detail["processModels"]["DEMO_PM_AprobarSolicitud"]
        self.assertTrue(any(pv["name"] == "solicitud" for pv in pm["processVariables"]))

    def test_datastore_inventoried(self):
        inv = json.loads((self.out / "inventory.json").read_text(encoding="utf-8"))
        all_objects = [
            o
            for objs in inv["objects"].values()
            if isinstance(objs, list)
            for o in objs
            if isinstance(o, dict)
        ]
        self.assertTrue(any(o.get("type") == "dataStore" for o in all_objects))

    # --- Contrato que consumen los agentes de la Fase 4.5 ---

    def test_record_type_relationships_views_actions(self):
        rt = self.detail["recordTypes"]["DEMO Solicitud"]
        self.assertEqual(rt["relationships"][0]["target"], "DEMO Historial")
        self.assertIn("Resumen", rt["views"])
        # Las acciones ya no son solo el nombre: la spec necesita saber QUE
        # proceso lanzan y si estan ocultas (`visibilityExpr: =false()` deja una
        # accion inalcanzable desde la UI sin borrarla).
        accion = rt["actions"][0]
        self.assertEqual(accion["name"], "Nueva solicitud")
        self.assertEqual(accion["target"], "DEMO_PM_AprobarSolicitud")
        self.assertIn("visibilityExpr", accion)

    def test_record_type_fields_con_nombre_y_uuid(self):
        """Regresion del export real: los datos del campo son elementos hijos,
        no atributos. Leyendo solo atributos, los 354 campos de una app real
        salian con `name: null` y la spec no podia traducir las referencias
        `urn:appian:record-field:v1:{rt}/{campo}` a ningun nombre legible."""
        rt = self.detail["recordTypes"]["DEMO Solicitud"]
        campos = rt["fields"]
        self.assertTrue(campos)
        for c in campos:
            self.assertTrue(c["name"], c)
            self.assertIn("uuid", c)  # es lo que resuelve urn:appian:record-field
        nombres = {c["name"] for c in campos}
        self.assertIn("estado", nombres)

    def test_interface_sail_and_referenced_record_types(self):
        ifc = self.detail["interfaces"]["DEMO_IFC_SolicitudForm"]
        self.assertIn("ri!importe > 1000", ifc["sail"])
        self.assertIn("DEMO Solicitud", ifc["referencedRecordTypes"])

    def test_pm_nodes_with_assignees(self):
        pm = self.detail["processModels"]["DEMO_PM_AprobarSolicitud"]
        by_id = {n["id"]: n for n in pm["nodes"]}
        self.assertEqual(by_id["n3"]["type"], "userInput")
        self.assertEqual(by_id["n3"]["assignees"], "DEMO_GRP_Aprobadores")
        self.assertIn("RESPONSABLE", by_id["n2"].get("expressionSummary", ""))

    def test_decision_rows(self):
        dec = self.detail["decisions"]["DEMO_DEC_NivelAprobacion"]
        self.assertEqual(len(dec["rows"]), 3)
        self.assertEqual(dec["rows"][0]["result"], "RESPONSABLE")
        self.assertIn("importe", dec["inputs"][0]["name"])

    def test_constant_value_for_state_domain(self):
        cons = self.detail["constants"]["DEMO_CONS_ESTADOS"]
        self.assertIn("BORRADOR", cons["value"])

    def test_cdt_required_from_min_occurs(self):
        cdt = self.detail["cdts"]["DEMO_CDT_Solicitud"]
        by_name = {f["name"]: f for f in cdt["fields"]}
        self.assertTrue(by_name["estado"]["required"])
        self.assertFalse(by_name["justificacion"]["required"])

    def test_datastore_entities(self):
        ds = self.detail["dataStores"]["DEMO_DS_Principal"]
        self.assertEqual(ds["entities"][0]["cdt"], "DEMO_CDT_Solicitud")


if __name__ == "__main__":
    unittest.main()
