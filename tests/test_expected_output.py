# -*- coding: utf-8 -*-
"""Test de contrato de tests/fixtures/expected-output/ (I4 del plan de auditoria).

`expected-output/` es la salida de referencia del Nivel 3 sobre el fixture. Antes
NINGUN test la consumia: eran 7 ficheros commiteados que ya contradecian 3
contratos distintos (layout, ficha de procesos ausente, alias de nombre tecnico).

Este test NO compara byte a byte — la salida de un LLM varia. Comprueba
INVARIANTES: que la referencia sigue siendo un ejemplo valido del contrato que la
propia skill exige. El invariante ancla es el gate real (`check_coverage.py
--mode rebuild`), que detecta por construccion los errores de layout.

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

# Documentos del nivel onboarding: existen en una ejecucion real, no en este
# fixture (que solo ilustra la capa 10-especificacion).
ONBOARDING_DOCS = {
    "00-resumen-ejecutivo.md", "01-funcional.md", "02-arquitectura.md",
    "03-modelo-datos.md", "04-seguridad-grupos.md", "05-integraciones-consumidas.md",
    "06-apis-expuestas.md", "07-batches.md", "09-valor-adicional.md",
    "INVENTARIO.md",
}

LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
HEADING_RE = re.compile(r"^#{1,6}\s+(.*)$")


def slug(texto: str) -> str:
    """Slugificacion estilo GitHub (suficiente para nuestras anclas)."""
    s = texto.strip().lower()
    s = re.sub(r"[`*_]", "", s)
    s = re.sub(r"[^\w\s-]", "", s, flags=re.UNICODE)
    return re.sub(r"\s+", "-", s).strip("-")


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

    # --- 1. INVARIANTE ANCLA -------------------------------------------------

    def test_pasa_el_gate_de_rebuild(self):
        """Si `pantallas/` volviera a colgar de la raiz, in_spec_dir daria False
        y las interfaces saldrian en missing: este test lo caza solo."""
        proc = subprocess.run(
            [sys.executable, str(COVERAGE), str(self.doc), "--mode", "rebuild"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_pasa_el_gate_de_onboarding(self):
        proc = subprocess.run(
            [sys.executable, str(COVERAGE), str(self.doc), "--mode", "onboarding"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    # --- 2. Layout -----------------------------------------------------------

    def test_layout_de_la_spec(self):
        spec = self.doc / "10-especificacion"
        self.assertTrue((spec / "pantallas").is_dir())
        self.assertTrue((spec / "procesos").is_dir())
        # Nada de eso puede colgar de la raiz (el bug original).
        self.assertFalse((self.doc / "pantallas").exists())
        self.assertFalse((self.doc / "procesos").exists())

    # --- 3. Integridad de enlaces --------------------------------------------

    def test_enlaces_relativos_resuelven(self):
        """`expected-output` solo contiene la capa 10-especificacion, asi que un
        enlace a los documentos 00-09 no puede resolverse aqui — pero en una
        ejecucion real si existe. Esos se validan contra el contrato de nombres
        (asi un typo como `03-modelo-dato.md` sigue cayendo); el resto tiene que
        existir en disco."""
        rotos = []
        for rel, texto in self.docs.items():
            base = (self.doc / rel).parent
            for destino in LINK_RE.findall(texto):
                if destino.startswith(("http://", "https://", "#", "mailto:")):
                    continue
                ruta = destino.split("#")[0]
                nombre = Path(ruta).name
                if nombre in ONBOARDING_DOCS:
                    continue
                if not (base / ruta).resolve().exists():
                    rotos.append(f"{rel} -> {destino}")
        self.assertEqual(rotos, [], "Enlaces rotos:\n" + "\n".join(rotos))

    # --- 4. Integridad de anclas ---------------------------------------------

    def test_anclas_internas_existen(self):
        anclas = {
            rel: {slug(m.group(1)) for m in (HEADING_RE.match(l) for l in t.splitlines()) if m}
            for rel, t in self.docs.items()
        }
        rotas = []
        for rel, texto in self.docs.items():
            base = (self.doc / rel).parent
            for destino in LINK_RE.findall(texto):
                if "#" not in destino or destino.startswith(("http", "mailto:")):
                    continue
                ruta, frag = destino.split("#", 1)
                objetivo = rel if not ruta else (
                    (base / ruta).resolve().relative_to(self.doc.resolve()).as_posix()
                    if (base / ruta).resolve().exists() else None
                )
                if objetivo in anclas and slug(frag) not in anclas[objetivo]:
                    rotas.append(f"{rel} -> {destino}")
        self.assertEqual(rotas, [], "Anclas rotas:\n" + "\n".join(rotas))

    # --- 5. Cobertura cruzada con el inventario ------------------------------

    def test_una_ficha_por_interfaz(self):
        fichas = {
            p.stem for p in (self.doc / "10-especificacion" / "pantallas").glob("*.md")
            if p.stem != "indice"
        }
        self.assertEqual(fichas, self.names_of("interface"))

    def test_una_ficha_de_nodos_por_process_model(self):
        fichas = {
            p.stem.replace("-nodos", "")
            for p in (self.doc / "10-especificacion" / "procesos").glob("*-nodos.md")
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

    # --- 6. Trazabilidad <-> inventario --------------------------------------

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

    # --- 7. Alias prohibidos (M8 en forma generica) --------------------------

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
                    contenido = m.group(1)
                    if contenido == stem:  # entre backticks y a secas
                        malos.append(f"{rel}: `{stem}` deberia ser `{real}`")
        self.assertEqual(malos, [], "\n".join(malos))

    # --- 8. Plantilla e higiene ---------------------------------------------

    def test_fichas_de_pantalla_siguen_la_plantilla(self):
        obligatorias = ("## Entradas", "## Componentes", "## Acciones",
                        "## Criterios de reconstrucción")
        for p in (self.doc / "10-especificacion" / "pantallas").glob("*.md"):
            if p.stem == "indice":
                continue
            texto = p.read_text(encoding="utf-8")
            for seccion in obligatorias:
                self.assertIn(seccion, texto, f"{p.name} sin '{seccion}'")
            criterios = re.search(
                r"## Criterios de reconstrucción.*?(?=\n## |\Z)", texto, re.S
            )
            self.assertIsNotNone(criterios, p.name)
            self.assertIn("- [ ]", criterios.group(0), f"{p.name} sin criterios verificables")

    def test_sin_placeholders_sin_rellenar(self):
        prohibidos = ("{{", "<TODO>", "lorem ipsum")
        malos = [
            f"{rel}: {t}"
            for rel, texto in self.docs.items()
            for t in prohibidos
            if t in texto
        ]
        self.assertEqual(malos, [], "\n".join(malos))


if __name__ == "__main__":
    unittest.main()
