# -*- coding: utf-8 -*-
"""Tests de xml_to_appian_recordtype_md.py y su hermano map_*.

Cubren las dos formas en que un recordTypeHaul nombra los datos de un campo
—elementos hijos (export real) y atributos (XML simplificados, como el fixture
de este repo)— y el contrato que faltaba: **cero campos no puede salir en verde**.

Antes de estos tests, pasarle el fixture al script devolvia exit 0 y un markdown
bien formado con la tabla de campos vacia. La Fase 2 no tiene forma de
distinguir eso de "este record type no tiene campos".

Corre con:  python -m unittest tests/test_xml_to_recordtype.py -v
(y tambien con pytest si esta disponible).
"""
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
SCRIPTS = ROOT / "skills" / "appian-sail-generator" / "scripts"
SINGLE = SCRIPTS / "xml_to_appian_recordtype_md.py"
BATCH = SCRIPTS / "map_xml_to_appian_recordtype_md.py"
FIXTURE_RT = ROOT / "tests" / "fixtures" / "mini-export" / "recordType" / "DEMO_RT_Solicitud.xml"


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


X1 = _load(SINGLE, "xml_to_recordtype")
XN = _load(BATCH, "map_xml_to_recordtype")


# --- XML sinteticos (cero datos reales: solo DEMO_*) -------------------------

# Forma de export real: los datos del campo son elementos hijos, y todo va
# dentro del namespace de Appian. Es la forma que parse_export.py documenta
# como la que de verdad sale del Application Designer.
REAL_SHAPE = """<?xml version="1.0" encoding="UTF-8"?>
<recordTypeHaul xmlns:a="http://www.appian.com/ae/types/2009">
  <a:recordType a:name="DEMO Real" a:uuid="uuid-rt-real">
    <a:description>Con namespace y elementos hijos.</a:description>
    <a:fields>
      <a:field>
        <a:fieldName>importe</a:fieldName>
        <a:uuid>uuid-campo-1</a:uuid>
        <a:type>Number (Decimal)</a:type>
      </a:field>
      <a:field>
        <a:fieldName>estado</a:fieldName>
        <a:uuid>uuid-campo-2</a:uuid>
        <a:type>Text</a:type>
      </a:field>
    </a:fields>
    <a:recordRelationshipCfg>
      <a:uuid>uuid-rel-1</a:uuid>
      <a:relationshipName>historial</a:relationshipName>
      <a:relationshipType>ONE_TO_MANY</a:relationshipType>
    </a:recordRelationshipCfg>
  </a:recordType>
</recordTypeHaul>
"""

SIN_CAMPOS = """<?xml version="1.0" encoding="UTF-8"?>
<recordTypeHaul>
  <recordType name="DEMO Vacio" uuid="uuid-rt-vacio"><fields/></recordType>
</recordTypeHaul>
"""

NO_ES_RECORDTYPE = """<?xml version="1.0" encoding="UTF-8"?>
<processModelHaul><processModel name="DEMO PM"/></processModelHaul>
"""


class TestFormaAtributos(unittest.TestCase):
    """El fixture del repo nombra los datos del campo como atributos."""

    def setUp(self):
        self.rt = X1.parse_recordtype(str(FIXTURE_RT))

    def test_lee_los_cinco_campos(self):
        self.assertEqual(len(self.rt["fields"]), 5, self.rt["fields"])
        self.assertEqual(
            [f["name"] for f in self.rt["fields"]],
            ["solicitudId", "solicitante", "importe", "justificacion", "estado"],
        )

    def test_conserva_uuid_y_tipo(self):
        primero = self.rt["fields"][0]
        self.assertEqual(primero["uuid"], "00000000-0000-0000-0000-000000000020")
        self.assertEqual(primero["type"], "Number (Integer)")

    def test_lee_la_relacion(self):
        self.assertEqual(len(self.rt["relationships"]), 1, self.rt["relationships"])
        rel = self.rt["relationships"][0]
        self.assertEqual(rel["name"], "historial")
        self.assertEqual(rel["type"], "one-to-many")

    def test_nombre_y_uuid_del_record_type(self):
        self.assertEqual(self.rt["name"], "DEMO Solicitud")
        self.assertEqual(self.rt["uuid"], "00000000-0000-0000-0000-000000000011")


class TestFormaExportReal(unittest.TestCase):
    """Elementos hijos + namespace: la forma que sale de verdad de Appian."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "real.xml"
        self.path.write_text(REAL_SHAPE, encoding="utf-8")
        self.rt = X1.parse_recordtype(str(self.path))

    def tearDown(self):
        self.tmp.cleanup()

    def test_lee_campos_con_namespace(self):
        self.assertEqual([f["name"] for f in self.rt["fields"]], ["importe", "estado"])
        self.assertEqual(self.rt["fields"][0]["uuid"], "uuid-campo-1")

    def test_lee_relacion_con_namespace(self):
        self.assertEqual(len(self.rt["relationships"]), 1)
        self.assertEqual(self.rt["relationships"][0]["type"], "one-to-many")

    def test_lee_metadatos_con_namespace(self):
        self.assertEqual(self.rt["name"], "DEMO Real")
        self.assertEqual(self.rt["uuid"], "uuid-rt-real")
        self.assertIn("elementos hijos", self.rt["description"])


class TestElGateFalla(unittest.TestCase):
    """Un gate que no puede fallar no es un gate: cero campos = exit no-cero."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def _run(self, script, *args):
        return subprocess.run(
            [sys.executable, str(script), *args],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )

    def test_sin_campos_sale_en_rojo_y_no_escribe(self):
        src = self.dir / "vacio.xml"
        src.write_text(SIN_CAMPOS, encoding="utf-8")
        out = self.dir / "vacio.md"

        res = self._run(SINGLE, str(src), "-o", str(out))

        self.assertEqual(res.returncode, 1, res.stdout + res.stderr)
        self.assertIn("ningun campo", res.stderr)
        self.assertFalse(out.exists(), "no debe escribir un contexto vacio")

    def test_xml_que_no_es_recordtype_no_pasa(self):
        src = self.dir / "otro.xml"
        src.write_text(NO_ES_RECORDTYPE, encoding="utf-8")
        with self.assertRaises(ValueError):
            X1.parse_recordtype(str(src))

    def test_el_fixture_si_pasa(self):
        """Contrapeso: el gate no puede estar fallando siempre."""
        out = self.dir / "ok.md"
        res = self._run(SINGLE, str(FIXTURE_RT), "-o", str(out))

        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        self.assertTrue(out.exists())
        self.assertIn("solicitudId", out.read_text(encoding="utf-8"))


class TestLote(unittest.TestCase):
    """El lote no se aborta a medias, pero termina en rojo si algo se cayo."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.entrada = self.dir / "in"
        self.entrada.mkdir()
        self.salida = self.dir / "out"

    def tearDown(self):
        self.tmp.cleanup()

    def _run(self):
        return subprocess.run(
            [sys.executable, str(BATCH), str(self.entrada), "-o", str(self.salida)],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )

    def test_lote_limpio_sale_en_verde(self):
        (self.entrada / "rt.xml").write_text(
            FIXTURE_RT.read_text(encoding="utf-8"), encoding="utf-8"
        )
        res = self._run()
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        self.assertEqual(len(list(self.salida.glob("*.md"))), 1)

    def test_un_vacio_tine_el_lote_de_rojo_pero_escribe_los_buenos(self):
        (self.entrada / "rt.xml").write_text(
            FIXTURE_RT.read_text(encoding="utf-8"), encoding="utf-8"
        )
        (self.entrada / "vacio.xml").write_text(SIN_CAMPOS, encoding="utf-8")

        res = self._run()

        self.assertEqual(res.returncode, 1, res.stdout + res.stderr)
        self.assertIn("vacio.xml", res.stderr)
        # El bueno se escribe igual: un XML roto no puede tirar el lote entero.
        self.assertEqual(len(list(self.salida.glob("*.md"))), 1)


if __name__ == "__main__":
    unittest.main()
