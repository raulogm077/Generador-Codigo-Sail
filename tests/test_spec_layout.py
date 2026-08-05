# -*- coding: utf-8 -*-
"""Tests de check_spec_layout.py — gate de estructura en runtime (C7 del plan).

Cada invariante se prueba en positivo Y en negativo: un gate que no puede
fallar no es un gate.

Corre con: python -m unittest tests.test_spec_layout -v
"""
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
SCRIPT = ROOT / "skills" / "appian-reverse-engineering" / "scripts" / "check_spec_layout.py"

FICHA_OK = """# Pantalla: Alta (`DEMO_IFC_Form`)
**Tipo**: formulario · **Usada desde**: `DEMO_SITE_X`

## Entradas (rule inputs)
| ri! | Tipo |
|---|---|
| `importe` | Decimal |

## Variables locales relevantes
N/A — la pantalla no declara `a!localVariables`.

## Componentes (en orden de aparición, TODOS)
| # | Componente |
|---|---|
| 1 | textField |

## Acciones (botones/links)
| Acción | Qué hace |
|---|---|
| Enviar | submit |

## Reglas invocadas
N/A — la pantalla no invoca reglas.

## Estados de la pantalla
N/A — el render no cambia según el estado.

## Criterios de reconstrucción (verificables)
- [ ] Con importe > 1000 el campo Justificación es obligatorio.
"""


class SpecLayoutTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="speclayout_"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def make_doc(self, docs: dict, extra_raiz: dict | None = None) -> Path:
        """Crea `<tmp>/_doc_generada/...`; `extra_raiz` cuelga del contenedor."""
        doc = self.tmp / "_doc_generada"
        for rel, texto in docs.items():
            p = doc / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(texto, encoding="utf-8")
        for rel, texto in (extra_raiz or {}).items():
            p = self.tmp / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(texto, encoding="utf-8")
        return doc

    def run_gate(self, doc: Path, mode: str = "rebuild"):
        return subprocess.run(
            [sys.executable, str(SCRIPT), str(doc), "--mode", mode],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )

    def base_docs(self) -> dict:
        return {
            "10-especificacion/pantallas/DEMO_IFC_Form.md": FICHA_OK,
            "10-especificacion/reglas-catalogo.md": "# Catalogo\n\n## Expression rules\n\n### rule!DEMO_R\n",
        }

    def con_nav(self, cuerpo: str) -> dict:
        docs = self.base_docs()
        docs["10-especificacion/navegacion.md"] = f"# Nav\n\n## site!DEMO_S\n{cuerpo}\n"
        return docs

    # --- caso feliz ---

    def test_estructura_correcta_exit_0(self):
        proc = self.run_gate(self.make_doc(self.base_docs()))
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_acepta_la_carpeta_contenedora(self):
        """Pasar el export en vez de _doc_generada debe dar el MISMO veredicto.

        Con el orden de candidatos invertido, rglob encontraba los .md de dentro
        y se quedaba con el contenedor: 'falta 10-especificacion/' + todos los
        enlaces relativos rotos, sobre una salida perfectamente valida.
        """
        self.make_doc(self.base_docs())
        proc = self.run_gate(self.tmp)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    # --- 1. layout ---

    def test_pantallas_en_la_raiz_exit_1(self):
        docs = {"pantallas/DEMO_IFC_Form.md": FICHA_OK, "10-especificacion/x.md": "# X\n"}
        proc = self.run_gate(self.make_doc(docs))
        self.assertEqual(proc.returncode, 1)
        self.assertIn("cuelga de la raiz", proc.stdout)

    def test_sin_carpeta_de_spec_en_rebuild_exit_1(self):
        proc = self.run_gate(self.make_doc({"01-funcional.md": "# F\n"}))
        self.assertEqual(proc.returncode, 1)
        self.assertIn("10-especificacion", proc.stdout)

    def test_onboarding_no_exige_carpeta_de_spec(self):
        proc = self.run_gate(self.make_doc({"01-funcional.md": "# F\n"}), mode="onboarding")
        self.assertEqual(proc.returncode, 0, proc.stdout)

    # --- 2. enlaces ---

    def test_enlace_roto_exit_1(self):
        proc = self.run_gate(self.make_doc(self.con_nav("Ver [ficha](pantallas/NO_EXISTE.md).")))
        self.assertEqual(proc.returncode, 1)
        self.assertIn("enlace roto", proc.stdout)

    def test_enlace_a_documento_de_onboarding_ausente_se_tolera(self):
        """La spec puede entregarse sin los documentos 00-09 al lado."""
        proc = self.run_gate(self.make_doc(self.con_nav("Ver [datos](../03-modelo-datos.md).")))
        self.assertEqual(proc.returncode, 0, proc.stdout)

    def test_ruta_mal_construida_a_documento_presente_exit_1(self):
        """Si el documento SI esta en la salida, la ruta tiene que ser correcta.

        Antes bastaba con que el basename estuviera en ONBOARDING_DOCS para
        silenciar el enlace: el gate no podia detectar un `../` de menos hacia
        los 10 documentos que mas se enlazan.
        """
        docs = self.con_nav("Ver [datos](03-modelo-datos.md).")  # falta ../
        docs["03-modelo-datos.md"] = "# Modelo de datos\n"
        proc = self.run_gate(self.make_doc(docs))
        self.assertEqual(proc.returncode, 1)
        self.assertIn("enlace roto", proc.stdout)

    def test_enlace_fuera_del_arbol_exit_1_sin_traceback(self):
        """`../../fuera.md` reventaba con ValueError al calcular el ancla."""
        docs = self.con_nav("Ver [fuera](../../fuera.md#seccion).")
        proc = self.run_gate(self.make_doc(docs, extra_raiz={"fuera.md": "# Seccion\n"}))
        self.assertEqual(proc.returncode, 1)
        self.assertNotIn("Traceback", proc.stderr)
        self.assertIn("fuera del arbol", proc.stdout)

    def test_enlace_a_directorio_exit_1(self):
        proc = self.run_gate(self.make_doc(self.con_nav("Ver [la carpeta](pantallas).")))
        self.assertEqual(proc.returncode, 1)
        self.assertIn("directorio", proc.stdout)

    def test_formas_validas_de_commonmark_no_son_enlaces_rotos(self):
        """Titulo tras el destino, destino entre <> y %-encoding son estandar."""
        docs = self.con_nav(
            'Ver [a](pantallas/DEMO_IFC_Form.md "La ficha"), '
            "[b](<pantallas/DEMO_IFC_Form.md>) y "
            "[c](pantallas/DEMO%20espacio.md)."
        )
        docs["10-especificacion/pantallas/DEMO espacio.md"] = FICHA_OK
        proc = self.run_gate(self.make_doc(docs))
        self.assertEqual(proc.returncode, 0, proc.stdout)

    def test_enlaces_dentro_de_un_bloque_de_codigo_se_ignoran(self):
        docs = self.con_nav(
            "Formato de la tabla:\n\n```markdown\n| Ficha | [x](pantallas/{{nombre}}.md) |\n```\n"
        )
        proc = self.run_gate(self.make_doc(docs))
        self.assertEqual(proc.returncode, 0, proc.stdout)

    # --- 3. anclas ---

    def test_ancla_rota_exit_1(self):
        proc = self.run_gate(self.make_doc(
            self.con_nav("Ver [regla](reglas-catalogo.md#rulenoexiste).")))
        self.assertEqual(proc.returncode, 1)
        self.assertIn("ancla rota", proc.stdout)

    def test_ancla_valida_no_falla(self):
        proc = self.run_gate(self.make_doc(
            self.con_nav("Ver [regla](reglas-catalogo.md#ruledemo_r).")))
        self.assertEqual(proc.returncode, 0, proc.stdout)

    def test_ancla_de_titulo_con_emoji_no_es_falso_positivo(self):
        """Regresion de la 1a ejecucion real: `### 5.1 🔴 Las candidaturas` deja
        dos espacios al quitar el emoji, y GitHub genera DOS guiones. El gate
        los colapsaba y marcaba como rota toda ancla hacia un titulo con emoji
        — que en esta skill son casi todos, porque el contrato los exige."""
        docs = self.base_docs()
        docs["10-especificacion/hallazgos.md"] = (
            "# Hallazgos\n\n### 5.1 🔴 Las candidaturas quedan bloqueadas\nTexto.\n"
        )
        docs["10-especificacion/navegacion.md"] = (
            "# Nav\n\n## site!DEMO_S\n"
            "Ver [hallazgo](hallazgos.md#51--las-candidaturas-quedan-bloqueadas).\n"
        )
        proc = self.run_gate(self.make_doc(docs))
        self.assertEqual(proc.returncode, 0, proc.stdout)

    def test_enlace_al_principio_del_documento_no_es_ancla_rota(self):
        proc = self.run_gate(self.make_doc(self.con_nav("[Subir](#)")))
        self.assertEqual(proc.returncode, 0, proc.stdout)

    # --- 4. plantilla de pantalla ---

    def test_ficha_sin_seccion_obligatoria_exit_1(self):
        docs = self.base_docs()
        docs["10-especificacion/pantallas/DEMO_IFC_Form.md"] = FICHA_OK.replace(
            "## Acciones (botones/links)", "## Otra cosa"
        )
        proc = self.run_gate(self.make_doc(docs))
        self.assertEqual(proc.returncode, 1)
        self.assertIn("## Acciones", proc.stdout)

    def test_ficha_con_seccion_vacia_exit_1(self):
        """Cabecera sin cuerpo = seccion sin documentar; el contrato exige
        contenido o un 'N/A — {motivo}' explicito."""
        docs = self.base_docs()
        docs["10-especificacion/pantallas/DEMO_IFC_Form.md"] = FICHA_OK.replace(
            "## Reglas invocadas\nN/A — la pantalla no invoca reglas.",
            "## Reglas invocadas\n",
        )
        proc = self.run_gate(self.make_doc(docs))
        self.assertEqual(proc.returncode, 1)
        self.assertIn("esta vacia", proc.stdout)

    def test_ficha_en_subcarpeta_tambien_se_valida(self):
        """Con glob no recursivo, agrupar por modulo saltaba la validacion."""
        docs = self.base_docs()
        docs["10-especificacion/pantallas/modulo1/DEMO_IFC_B.md"] = "# Ficha vacia\nNada.\n"
        proc = self.run_gate(self.make_doc(docs))
        self.assertEqual(proc.returncode, 1)
        self.assertIn("DEMO_IFC_B.md", proc.stdout)

    def test_ficha_sin_criterios_verificables_exit_1(self):
        docs = self.base_docs()
        docs["10-especificacion/pantallas/DEMO_IFC_Form.md"] = FICHA_OK.replace(
            "- [ ] Con importe > 1000 el campo Justificación es obligatorio.",
            "La pantalla se comporta como se espera.",
        )
        proc = self.run_gate(self.make_doc(docs))
        self.assertEqual(proc.returncode, 1)
        self.assertIn("criterios de reconstruccion", proc.stdout)

    def test_criterio_ya_verificado_cuenta(self):
        docs = self.base_docs()
        docs["10-especificacion/pantallas/DEMO_IFC_Form.md"] = FICHA_OK.replace(
            "- [ ] Con", "- [x] Con"
        )
        proc = self.run_gate(self.make_doc(docs))
        self.assertEqual(proc.returncode, 0, proc.stdout)

    # --- 5. higiene ---

    def test_placeholder_sin_rellenar_exit_1(self):
        docs = self.base_docs()
        docs["10-especificacion/reglas-catalogo.md"] += "\n### rule!{{nombre}}\n"
        proc = self.run_gate(self.make_doc(docs))
        self.assertEqual(proc.returncode, 1)
        self.assertIn("placeholder", proc.stdout)

    def test_tbd_es_placeholder(self):
        docs = self.base_docs()
        docs["10-especificacion/reglas-catalogo.md"] += "\nMotivo: TBD\n"
        proc = self.run_gate(self.make_doc(docs))
        self.assertEqual(proc.returncode, 1)
        self.assertIn("TBD", proc.stdout)

    def test_placeholder_dentro_de_un_bloque_de_codigo_se_ignora(self):
        docs = self.base_docs()
        docs["10-especificacion/reglas-catalogo.md"] += (
            "\nPlantilla:\n\n```\n### rule!{{nombre}}\n```\n"
        )
        proc = self.run_gate(self.make_doc(docs))
        self.assertEqual(proc.returncode, 0, proc.stdout)

    # --- uso ---

    def test_ruta_inexistente_exit_2(self):
        proc = self.run_gate(self.tmp / "no" / "existe")
        self.assertEqual(proc.returncode, 2)


if __name__ == "__main__":
    unittest.main()
