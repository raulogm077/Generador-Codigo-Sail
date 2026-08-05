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

    # --- I5: aristas REALES de los 5 patrones que solo tenian test de regex.
    # Las hospeda DEMO_PM_ReintentarEnvios (namespaced a proposito, ver M6).

    def test_query_entity_edge(self):
        self.assertIn(
            ("DEMO_PM_ReintentarEnvios", "DEMO_CONS_ENTITY_SOLICITUD", "queryEntity"),
            self.edges_with_type(),
        )

    def test_write_entity_edge(self):
        self.assertIn(
            ("DEMO_PM_ReintentarEnvios", "DEMO_CONS_ENTITY_SOLICITUD", "writeEntity"),
            self.edges_with_type(),
        )

    def test_write_records_edge(self):
        self.assertIn(
            ("DEMO_PM_ReintentarEnvios", "DEMO Solicitud", "writeRecords"),
            self.edges_with_type(),
        )

    def test_subprocess_edge(self):
        """<a:processModelUuid> CON prefijo de namespace: si el parser no lo
        tolerase (M6), esta arista no existiria."""
        self.assertIn(
            ("DEMO_PM_ReintentarEnvios", "DEMO_PM_AprobarSolicitud", "subprocess"),
            self.edges_with_type(),
        )

    def test_member_of_group_edge(self):
        """La cadena real de Appian: el SAIL no puede nombrar un grupo, asi que
        `a!isUserMemberOfGroup` apunta a una CONSTANTE de tipo Group y es esa
        constante la que resuelve al grupo. Antes el fixture escribia
        `cons!DEMO_GRP_Aprobadores` — un nombre de grupo tras el prefijo de
        constante — y la arista salia del fallback por nombre, no del patron."""
        self.assertIn(
            ("DEMO_PM_ReintentarEnvios", "DEMO_CONS_GRP_APROBADORES", "security"),
            self.edges_with_type(),
        )
        self.assertIn(
            ("DEMO_CONS_GRP_APROBADORES", "DEMO_GRP_Aprobadores", "constGroup"),
            self.edges_with_type(),
        )

    def test_pm_invocado_como_subproceso_ya_no_es_huerfano(self):
        self.assertNotIn("DEMO_PM_AprobarSolicitud", self.graph["orphans"])

    def test_grupo_referenciado_ya_no_es_huerfano(self):
        self.assertNotIn("DEMO_GRP_Aprobadores", self.graph["orphans"])

    # --- Referencias ESTRUCTURALES (auditoria B7) -------------------------
    # Todas viajan en tags/atributos del XML, no en SAIL. Sin ellas el grafo
    # daba por muertos objetos vivos y backlog-writer los proponia como
    # DESCARTADO: el formulario principal de la app y la integracion con el ERP.

    def test_site_page_apunta_al_record_type(self):
        """La arista sale del `objectUuid` de la pagina. Antes salia del URN que
        el fixture llevaba escrito en la prosa del <description>: un export real
        no lo lleva y el site no generaba ni una arista."""
        self.assertIn(
            ("DEMO_SITE_Solicitudes", "DEMO Solicitud", "sitePage"),
            self.edges_with_type(),
        )

    def test_site_page_apunta_a_la_interfaz(self):
        self.assertIn(
            ("DEMO_SITE_Solicitudes", "DEMO_IFC_SolicitudForm", "sitePage"),
            self.edges_with_type(),
        )

    def test_form_de_process_model_apunta_a_la_interfaz(self):
        self.assertIn(
            ("DEMO_PM_AprobarSolicitud", "DEMO_IFC_SolicitudForm", "form"),
            self.edges_with_type(),
        )

    def test_integration_ref_de_nodo_apunta_a_la_integracion(self):
        self.assertIn(
            ("DEMO_PM_AprobarSolicitud", "DEMO_INT_EnviarERP", "integrationCall"),
            self.edges_with_type(),
        )

    def test_record_view_y_record_action(self):
        self.assertIn(
            ("DEMO Solicitud", "DEMO_IFC_SolicitudForm", "recordView"),
            self.edges_with_type(),
        )
        self.assertIn(
            ("DEMO Solicitud", "DEMO_PM_AprobarSolicitud", "recordAction"),
            self.edges_with_type(),
        )

    def test_constante_de_entidad_apunta_a_su_data_store(self):
        self.assertIn(
            ("DEMO_CONS_ENTITY_SOLICITUD", "DEMO_DS_Principal", "dataStoreEntity"),
            self.edges_with_type(),
        )

    def test_el_formulario_principal_no_es_huerfano(self):
        """El caso que mas dolia: pagina de site, form de start event, form de
        user task y vista del record type — y aun asi salia en `orphans`."""
        self.assertNotIn("DEMO_IFC_SolicitudForm", self.graph["orphans"])

    def test_la_integracion_no_es_huerfana(self):
        self.assertNotIn("DEMO_INT_EnviarERP", self.graph["orphans"])

    def test_solo_queda_huerfano_lo_que_de_verdad_no_se_usa(self):
        """DEMO_CONS_ESTADOS no la referencia nadie en el fixture (el gateway
        compara contra un literal). El resto de objetos SI tienen caller."""
        self.assertEqual(self.graph["orphans"], ["DEMO_CONS_ESTADOS"])

    def test_batch_no_cuenta_como_huerfano(self):
        """Un PM con recurrencia lo dispara el planificador, no otro objeto:
        grado entrante 0 es su estado normal."""
        self.assertNotIn("DEMO_PM_ReintentarEnvios", self.graph["orphans"])

    def test_el_fixture_no_tiene_ciclos_de_invocacion(self):
        self.assertEqual(self.graph["cycles"], [])
        self.assertEqual(self.graph["stats"]["cycleCount"], 0)


class TestParserRobustness(unittest.TestCase):
    """M5 y M6: huerfanos completos y tags con prefijo de namespace."""

    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("parse_export", SCRIPT)
        cls.mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.mod)

    def test_subprocess_pattern_con_prefijo_de_namespace(self):
        """Los exports Haul reales llevan prefijo (<a:processModelUuid>); el
        fixture sintetico no, asi que el test verde no distinguia el caso."""
        xml = '<a:processModelUuid>00000000-0000-0000-0000-000000000009</a:processModelUuid>'
        m = self.mod.REF_PATTERNS["subprocess"].search(xml)
        self.assertIsNotNone(m)
        self.assertEqual(m.group(1), "00000000-0000-0000-0000-000000000009")

    def test_connected_system_ref_con_prefijo_de_namespace(self):
        xml = "<ns2:connectedSystemRef>DEMO_CS_ERP</ns2:connectedSystemRef>"
        m = self.mod.REF_PATTERNS["connectedSystemRef"].search(xml)
        self.assertIsNotNone(m)
        self.assertEqual(m.group(1), "DEMO_CS_ERP")

    def test_orphans_no_se_truncan(self):
        """backlog-writer usa graph.json#orphans como evidencia de 'objeto
        muerto': truncada a 50, afirmaria muerte sobre datos incompletos."""
        objetos = [
            {
                "type": "expressionRule",
                "name": f"DEMO_R{i:03d}",
                "uuid": f"00000000-0000-0000-0000-{i:012d}",
                "path": f"/no/existe/DEMO_R{i:03d}.xml",  # read_text falla -> 0 aristas
            }
            for i in range(60)
        ]
        inventory = {"objects": {"expressionRule": objetos}}
        graph = self.mod.cmd_graph(Path("."), inventory)
        self.assertEqual(graph["stats"]["orphanCount"], 60)
        self.assertEqual(len(graph["orphans"]), 60)

    # --- Deteccion de ciclos (la prometia analysis-workflow.md y no existia) ---

    def _nodos(self, *nombres):
        return [{"id": n.lower(), "name": n, "type": "expressionRule"} for n in nombres]

    def _aristas(self, *pares):
        return [{"source": a.lower(), "target": b.lower(), "refType": "ruleRef"}
                for a, b in pares]

    def test_find_cycles_detecta_el_ciclo(self):
        ciclos = self.mod.find_cycles(
            self._nodos("A", "B", "C"),
            self._aristas(("A", "B"), ("B", "A"), ("B", "C")),
        )
        self.assertEqual(ciclos, [["A", "B"]])

    def test_find_cycles_no_inventa_ciclos_en_un_arbol(self):
        ciclos = self.mod.find_cycles(
            self._nodos("A", "B", "C", "D"),
            self._aristas(("A", "B"), ("A", "C"), ("B", "D"), ("C", "D")),
        )
        self.assertEqual(ciclos, [])

    def test_find_cycles_aguanta_una_cadena_larga(self):
        """Pila explicita, no recursion: 5000 objetos encadenados desbordarian
        el limite de Python y el script moriria en apps grandes."""
        nombres = [f"N{i}" for i in range(5000)]
        pares = [(nombres[i], nombres[i + 1]) for i in range(len(nombres) - 1)]
        self.assertEqual(self.mod.find_cycles(self._nodos(*nombres), self._aristas(*pares)), [])


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
