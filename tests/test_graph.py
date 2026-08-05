# tests/test_graph.py — Task 2: resolucion de referencias del grafo.
# Fixture 100% sintetico (DEMO_*, UUIDs 00000000-*). Corre con `python -m unittest tests/test_graph.py -v`.
import importlib.util
import json
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

FIXTURE = Path(__file__).parent / "fixtures" / "mini-export"
SCRIPT = Path(__file__).parents[1] / "skills" / "appian-reverse-engineering" / "scripts" / "parse_export.py"
OUT = FIXTURE / "_doc_generada" / "_intermedio"


def _load_module():
    spec = importlib.util.spec_from_file_location("parse_export", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestGraph(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # --all requiere --out-dir (el propio script lo exige)
        subprocess.run(
            [sys.executable, str(SCRIPT), "--all", str(FIXTURE), "--out-dir", str(OUT)],
            check=True,
        )
        cls.graph = json.loads((OUT / "graph.json").read_text(encoding="utf-8"))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(FIXTURE / "_doc_generada", ignore_errors=True)

    def edges(self):
        return {(e["from"], e["to"]) for e in self.graph["edges"]}

    def edges_with_type(self):
        return {(e["from"], e["to"], e["refType"]) for e in self.graph["edges"]}

    # --- Bug actual: rule! solo resolvia contra expressionRule ---

    def test_interface_call_creates_edge(self):
        # rule!DEMO_IFC_SolicitudList dentro de DEMO_IFC_SolicitudForm debe resolver a la INTERFAZ
        self.assertIn(("DEMO_IFC_SolicitudForm", "DEMO_IFC_SolicitudList"), self.edges())

    def test_called_interface_not_orphan(self):
        self.assertNotIn("DEMO_IFC_SolicitudList", self.graph["orphans"])

    def test_rule_edge_still_works(self):
        self.assertIn(("DEMO_IFC_SolicitudForm", "DEMO_VAL_ValidarImporte"), self.edges())

    def test_decision_call_creates_edge(self):
        # rule!DEMO_DEC_NivelAprobacion dentro del PM debe resolver a la DECISION
        self.assertIn(("DEMO_PM_AprobarSolicitud", "DEMO_DEC_NivelAprobacion"), self.edges())

    # --- Patrones nuevos (los que analysis-workflow.md documenta y faltaban) ---

    def test_connected_system_ref_edge(self):
        # <connectedSystemRef>DEMO_CS_ERP</connectedSystemRef> en la integration
        self.assertIn(
            ("DEMO_INT_EnviarERP", "DEMO_CS_ERP", "connectedSystem"),
            self.edges_with_type(),
        )


class TestNewRefPatterns(unittest.TestCase):
    """Los patrones sin ejemplar en el fixture se validan a nivel de regex,
    importando parse_export.py como modulo (solo stdlib)."""

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_query_entity_pattern(self):
        m = self.mod.REF_PATTERNS["queryEntity"].search(
            "a!queryEntity(entity: cons!DEMO_ENTITY_SOLICITUD, query: a!query())"
        )
        self.assertIsNotNone(m)
        self.assertEqual(m.group(1), "DEMO_ENTITY_SOLICITUD")

    def test_write_to_data_store_entity_pattern(self):
        m = self.mod.REF_PATTERNS["writeEntity"].search(
            "a!writeToDataStoreEntity(dataStoreEntity: cons!DEMO_ENTITY_SOLICITUD, valueToStore: ri!s)"
        )
        self.assertIsNotNone(m)
        self.assertEqual(m.group(1), "DEMO_ENTITY_SOLICITUD")

    def test_write_records_pattern(self):
        sail = (
            "a!writeRecords(records: 'recordType!{00000000-0000-0000-0000-000000000011}DEMO Solicitud'())"
        )
        m = self.mod.REF_PATTERNS["writeRecords"].search(sail)
        self.assertIsNotNone(m)
        self.assertEqual(m.group(1), "00000000-0000-0000-0000-000000000011")

    def test_subprocess_uuid_pattern(self):
        xml = "<processModelUuid>00000000-0000-0000-0000-000000000009</processModelUuid>"
        m = self.mod.REF_PATTERNS["subprocess"].search(xml)
        self.assertIsNotNone(m)
        self.assertEqual(m.group(1), "00000000-0000-0000-0000-000000000009")

    def test_is_user_member_of_group_pattern(self):
        m = self.mod.REF_PATTERNS["memberOfGroup"].search(
            "a!isUserMemberOfGroup(username: loggedInUser(), groups: cons!DEMO_GRP_Aprobadores)"
        )
        self.assertIsNotNone(m)
        self.assertEqual(m.group(1), "DEMO_GRP_Aprobadores")


if __name__ == "__main__":
    unittest.main()
