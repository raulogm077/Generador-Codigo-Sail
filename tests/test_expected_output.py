# -*- coding: utf-8 -*-
"""Test de contrato de tests/fixtures/expected-output/ (I4 del plan de auditoria).

`expected-output/` es la salida de referencia del Nivel 3 sobre el fixture. Antes
NINGUN test la consumia: eran 7 ficheros commiteados que ya contradecian 3
contratos distintos (layout, ficha de procesos ausente, alias de nombre tecnico).

Este test NO compara byte a byte — la salida de un LLM varia. Comprueba
INVARIANTES: que la referencia sigue siendo un ejemplo valido del contrato que la
propia skill exige. Los invariantes ancla son los DOS gates reales
(`check_coverage.py` y `check_spec_layout.py`), que se ejecutan tal cual: enlaces,
anclas, layout y plantilla NO se revalidan aqui con una copia de su logica —
esa copia ya diverjo una vez (la lista de placeholders del gate y la del test
dejaron de coincidir en silencio).

Corre con: python -m unittest tests.test_expected_output -v
"""
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "mini-export"
EXPECTED = ROOT / "tests" / "fixtures" / "expected-output"
SCRIPTS = ROOT / "skills" / "appian-reverse-engineering" / "scripts"
PARSER = SCRIPTS / "parse_export.py"
COVERAGE = SCRIPTS / "check_coverage.py"
SPEC_LAYOUT = SCRIPTS / "check_spec_layout.py"


class TestExpectedOutput(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="expout_"))
        cls.doc = cls.tmp / "_doc_generada"
        shutil.copytree(EXPECTED, cls.doc)
        inter = cls.doc / "_intermedio"
        inter.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            [sys.executable, str(PARSER), "--all", str(FIXTURE), "--out-dir", str(inter)],
            check=True, capture_output=True,
        )
        cls.inventory = json.loads((inter / "inventory.json").read_text(encoding="utf-8"))
        cls.graph = json.loads((inter / "graph.json").read_text(encoding="utf-8"))
        cls.objects = [
            o
            for lst in cls.inventory["objects"].values()
            if isinstance(lst, list)
            for o in lst
            if isinstance(o, dict) and o.get("type") and o.get("name")
        ]
        cls.docs = {
            p.relative_to(cls.doc).as_posix(): p.read_text(encoding="utf-8")
            for p in cls.doc.rglob("*.md")
        }

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def names_of(self, obj_type):
        return {o["name"] for o in self.objects if o["type"] == obj_type}

    def run_gate(self, script, mode):
        return subprocess.run(
            [sys.executable, str(script), str(self.doc), "--mode", mode],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )

    # --- 1. INVARIANTES ANCLA: los gates reales, sin reimplementarlos --------

    def test_pasa_el_gate_de_cobertura_rebuild(self):
        """Si `pantallas/` volviera a colgar de la raiz, in_spec_dir daria False
        y las interfaces saldrian en missing: este test lo caza solo."""
        proc = self.run_gate(COVERAGE, "rebuild")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_pasa_el_gate_de_cobertura_onboarding(self):
        """La capa 10-especificacion cubre por si sola los 7 tipos requeridos por
        el modo onboarding — SIN contar trazabilidad.md, que como catalogo de
        todos los objetos hacia este test trivialmente verde."""
        proc = self.run_gate(COVERAGE, "onboarding")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_pasa_el_gate_de_estructura(self):
        """SKILL.md declara este gate 'validacion final, siempre'; la salida de
        referencia tiene que ser la primera en cumplirlo. Cubre layout, enlaces,
        anclas, secciones de plantilla e higiene."""
        proc = self.run_gate(SPEC_LAYOUT, "rebuild")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    # --- 2. Layout -----------------------------------------------------------

    def test_layout_de_la_spec(self):
        spec = self.doc / "10-especificacion"
        self.assertTrue((spec / "pantallas").is_dir())
        self.assertTrue((spec / "procesos").is_dir())
        # Nada de eso puede colgar de la raiz (el bug original).
        self.assertFalse((self.doc / "pantallas").exists())
        self.assertFalse((self.doc / "procesos").exists())

    # --- 3. Cobertura cruzada con el inventario ------------------------------

    def test_una_ficha_por_interfaz(self):
        fichas = {
            p.stem for p in (self.doc / "10-especificacion" / "pantallas").rglob("*.md")
            if p.stem != "indice"
        }
        self.assertEqual(fichas, self.names_of("interface"))

    def test_una_ficha_de_nodos_por_process_model(self):
        fichas = {
            p.stem.replace("-nodos", "")
            for p in (self.doc / "10-especificacion" / "procesos").rglob("*-nodos.md")
        }
        self.assertEqual(fichas, self.names_of("processModel"))

    def test_catalogo_cubre_reglas_decisions_y_constants(self):
        catalogo = self.docs["10-especificacion/reglas-catalogo.md"]
        for name in self.names_of("expressionRule"):
            self.assertIn(f"### rule!{name}", catalogo)
        for name in self.names_of("decision"):
            self.assertIn(f"### decision!{name}", catalogo)
        for name in self.names_of("constant"):
            self.assertIn(f"### cons!{name}", catalogo)

    def test_navegacion_cubre_los_sites(self):
        nav = self.docs["10-especificacion/navegacion.md"]
        for name in self.names_of("site"):
            self.assertIn(f"## site!{name}", nav)

    # --- 4. Trazabilidad <-> inventario --------------------------------------

    def test_trazabilidad_cubre_todo_el_inventario(self):
        texto = self.docs["10-especificacion/trazabilidad.md"]
        filas = [l for l in texto.splitlines() if l.startswith("| `")]
        citados = {l.split("`")[1] for l in filas}
        esperados = {o["name"] for o in self.objects}
        self.assertEqual(citados, esperados)
        n = len(esperados)
        self.assertIn(f"{n}/{n}", texto)

    def test_toda_fila_de_trazabilidad_tiene_estado_valido(self):
        malas = []
        for linea in self.docs["10-especificacion/trazabilidad.md"].splitlines():
            if not linea.startswith("| `"):
                continue
            if "DOCUMENTADO" in linea:
                continue
            m = re.search(r"DESCARTADO\s*:\s*([^|]*)", linea)
            if not (m and m.group(1).strip(" -—–\t")):
                malas.append(linea)
        self.assertEqual(malas, [], "Filas sin estado valido:\n" + "\n".join(malas))

    def test_estado_valido_rechaza_un_descartado_sin_motivo(self):
        """La referencia no tiene ni una fila DESCARTADO, asi que el test de
        arriba nunca llega a evaluar su rama: sin esto, la validacion del motivo
        seria codigo muerto y podria romperse sin que nadie se enterase."""
        mala = "| `DEMO_X` (interface) | — | — | — | DESCARTADO: |"
        m = re.search(r"DESCARTADO\s*:\s*([^|]*)", mala)
        self.assertFalse(bool(m and m.group(1).strip(" -—–\t")))
        buena = "| `DEMO_X` (interface) | — | — | — | DESCARTADO: 0 callers |"
        m = re.search(r"DESCARTADO\s*:\s*([^|]*)", buena)
        self.assertTrue(bool(m and m.group(1).strip(" -—–\t")))

    # --- 5. La referencia no puede afirmar lo que el grafo desmiente ---------

    def test_los_callers_declarados_existen_como_arista(self):
        """La ficha de `DEMO_CONS_ESTADOS` declaraba dos callers que no existen:
        ningun objeto del fixture la referencia y `graph.json` la lista, con
        razon, como huerfana. La salida de referencia no puede contradecir al
        grafo del mismo fixture."""
        aristas = {(e["from"], e["to"]) for e in self.graph["edges"]}
        nombres = {o["name"] for o in self.objects}
        texto = self.docs["10-especificacion/reglas-catalogo.md"]
        actual = None
        malos = []
        for linea in texto.splitlines():
            m = re.match(r"^#{2,4}\s+(?:rule|cons|decision)!(\S+)", linea.strip())
            if m:
                actual = m.group(1)
                continue
            if actual is None or "**Callers**" not in linea:
                continue
            segmento = linea.split("**Callers**")[1].split("·")[0]
            for caller in re.findall(r"`([^`]+)`", segmento):
                if caller in nombres and (caller, actual) not in aristas:
                    malos.append(f"{actual}: declara caller `{caller}` sin arista en graph.json")
        self.assertEqual(malos, [], "\n".join(malos))

    # --- 6. Alias prohibidos (M8 en forma generica) --------------------------

    def test_no_se_cita_el_stem_del_fichero_como_nombre_de_objeto(self):
        """`DEMO_RT_Solicitud` es el nombre del FICHERO; el objeto se llama
        `DEMO Solicitud`. Citar el stem entrecomillado induce a error y no casa
        con el inventario."""
        alias = {
            Path(o["path"]).stem: o["name"]
            for o in self.objects
            if Path(o["path"]).stem != o["name"]
        }
        malos = []
        for rel, texto in self.docs.items():
            for stem, real in alias.items():
                for m in re.finditer(r"`([^`]+)`", texto):
                    if m.group(1) == stem:  # entre backticks y a secas
                        malos.append(f"{rel}: `{stem}` deberia ser `{real}`")
        self.assertEqual(malos, [], "\n".join(malos))


if __name__ == "__main__":
    unittest.main()
