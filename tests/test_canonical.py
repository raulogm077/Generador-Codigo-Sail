# -*- coding: utf-8 -*-
"""Formato CANONICO de export: el que Appian produce de verdad.

Descubierto probando el skill contra un export real (106 objetos): salian 91
huerfanos. Los patrones del parser estaban escritos contra la sintaxis que se ve
en el DESIGNER (`rule!X`, `cons!X`, `a!formLayout`), y esa sintaxis tiene CERO
apariciones en un export real:

  - componentes  -> #"SYSTEM_SYSRULES_formLayout_v2"(...)   (no a!formLayout)
  - objetos      -> #"_a-0000f01f-..._2358028"(...)          (no rule!/cons!)
  - campos       -> #"urn:appian:record-field:v1:{rtUuid}/{fieldUuid}"

Con el grafo asi, `backlog-writer` habria propuesto DESCARTAR media aplicacion
por "0 callers". Fixture: tests/fixtures/canonical-export (5 objetos, sintetico).

Corre con: python -m unittest tests.test_canonical -v
"""
import importlib.util
import json
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

FIXTURE = Path(__file__).parent / "fixtures" / "canonical-export"
SCRIPT = (
    Path(__file__).parents[1]
    / "skills" / "appian-reverse-engineering" / "scripts" / "parse_export.py"
)
OUT = FIXTURE / "_doc_generada" / "_intermedio"

IFC = "DEMO_CANON_Form"
RULE = "DEMO_CANON_Validar"
CONS = "DEMO_CANON_ESTADOS"
RT = "DEMO Registro"
PM = "DEMO_CANON_PM"


class TestCanonicalExport(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run(
            [sys.executable, str(SCRIPT), "--all", str(FIXTURE), "--out-dir", str(OUT)],
            check=True, capture_output=True,
        )
        cls.inventory = json.loads((OUT / "inventory.json").read_text(encoding="utf-8"))
        cls.graph = json.loads((OUT / "graph.json").read_text(encoding="utf-8"))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(FIXTURE / "_doc_generada", ignore_errors=True)

    def edges(self):
        return {(e["from"], e["to"], e["refType"]) for e in self.graph["edges"]}

    def test_el_export_canonico_se_inventaria(self):
        counts = self.inventory["counts"]
        self.assertEqual(self.inventory["parseErrors"], 0)
        for tipo in ("interface", "expressionRule", "constant", "recordType", "processModel"):
            self.assertEqual(counts.get(tipo), 1, f"falta {tipo}: {counts}")

    def test_referencia_canonica_a_expression_rule(self):
        """#"_a-..._0002"(importe: ...) es como una interfaz llama a una regla."""
        self.assertIn((IFC, RULE, "ruleRef"), self.edges())

    def test_referencia_canonica_a_constante(self):
        self.assertIn((IFC, CONS, "constRef"), self.edges())

    def test_campo_de_record_resuelve_al_record_type(self):
        """El primer UUID de urn:appian:record-field:v1:{rt}/{campo} es el record
        type: 960 apariciones en el export real, y ni una arista."""
        self.assertIn((IFC, RT, "recordFieldRef"), self.edges())

    def test_process_model_referencia_la_interfaz_por_uuid(self):
        """Un PM real no lleva <form>: la referencia va en la expresion del nodo."""
        self.assertIn((PM, IFC, "ruleRef"), self.edges())

    def test_los_componentes_de_plataforma_no_generan_ruido(self):
        """#"SYSTEM_SYSRULES_*" son componentes de Appian, no objetos del export:
        no pueden aparecer como nodos ni como aristas."""
        nombres = {n["name"] for n in self.graph["nodes"]}
        self.assertFalse({n for n in nombres if n and n.startswith("SYSTEM_")})
        for _, destino, _ in self.edges():
            self.assertFalse(str(destino).startswith("SYSTEM_"))

    def test_el_nombre_del_pm_es_el_del_modelo_no_el_de_la_instancia(self):
        """Un PM real trae dos <name>: el del modelo y la expresion que nombra
        cada instancia (="X - " & pp!starttime). Cogiendo la segunda y limpiando
        las comillas, TODOS los process models salian con el sufijo ' - ' pegado
        en inventario, grafo y documentacion."""
        nombres = [o["name"] for o in self.inventory["objects"]["processModel"]]
        self.assertEqual(nombres, [PM])
        for n in nombres:
            self.assertFalse(n.endswith(" - "), n)
            self.assertFalse(n.startswith("="), n)

    def test_el_batch_se_detecta_por_su_timer_trigger(self):
        """<recurrence> tiene HIJOS, no texto: buscar su texto no lo encontraba,
        asi que ningun batch se marcaba como tal y todos salian huerfanos."""
        pm = self.inventory["objects"]["processModel"][0]
        self.assertTrue(pm.get("hasRecurrence"), pm)
        self.assertEqual(pm.get("startType"), "timer")

    def test_referencia_por_uuid_en_un_atributo(self):
        """Los record types lanzan procesos con <a:relatedActionCfg><a:target
        a:uuid="..."/>: el UUID va en un atributo, no en una expresion. En el
        export real eso dejaba los 13 process models huerfanos, los 13."""
        self.assertIn((RT, PM, "uuidRef"), self.edges())

    def test_el_rolemap_conecta_con_el_grupo(self):
        """Los grupos llevan UUID con prefijo `_e-`, no `_a-`, y se referencian
        desde <roleMap><groupUuid>. Con el prefijo fijado a `_a-`, los 8 grupos
        del export real salian huerfanos los 8."""
        self.assertIn((PM, "DEMO Canon Admins", "security"), self.edges())

    def test_la_application_no_cuenta_como_caller(self):
        """EL DISCRIMINANTE del barrido de UUIDs: la application lista TODOS los
        objetos de la app por UUID. Si contara, nada seria huerfano nunca y la
        deteccion de objetos muertos quedaria inservible — el mismo problema que
        INVENTARIO.md en el gate de cobertura."""
        fuentes = {origen for origen, _, _ in self.edges()}
        self.assertNotIn("DEMO Canon App", fuentes)

    def test_nada_queda_huerfano_salvo_los_puntos_de_entrada(self):
        """La app sintetica esta toda conectada. Quedan sin callers la
        application (punto de entrada por tipo) y el PM, que solo lo lanza el
        record type... que si lo referencia: asi que no queda ninguno."""
        self.assertEqual(self.graph["orphans"], [])


class TestCanonicalPatterns(unittest.TestCase):
    """Unidad: los patrones, sin tocar disco."""

    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("parse_export", SCRIPT)
        cls.mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.mod)

    def test_patron_de_referencia_canonica(self):
        encontrados = self.mod.REF_PATTERNS["canonicalRef"].findall(
            '#"SYSTEM_SYSRULES_formLayout_v2"(contents: #"_a-0000f01f_2358028"(x: 1))'
        )
        self.assertIn("_a-0000f01f_2358028", encontrados)

    def test_patron_de_campo_de_record(self):
        m = self.mod.REF_PATTERNS["recordFieldRef"].search(
            'ri!r[#"urn:appian:record-field:v1:05b0b9f4-ac94-4454-91ea-a4f42d16d21c/773aea05-4803-413d-9557-42df14074cba"]'
        )
        self.assertIsNotNone(m)
        self.assertEqual(m.group(1), "05b0b9f4-ac94-4454-91ea-a4f42d16d21c")


if __name__ == "__main__":
    unittest.main()
