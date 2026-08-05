# -*- coding: utf-8 -*-
"""Tests de check_spec_layout.py — gate de estructura en runtime (C7 del plan).

Cada invariante se prueba en positivo Y en negativo: un gate que no puede
fallar no es un gate.

Corre con: python -m unittest tests.test_spec_layout -v
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
SCRIPT = ROOT / "skills" / "appian-reverse-engineering" / "scripts" / "check_spec_layout.py"

FICHA_OK = """# Pantalla: Alta (`DEMO_IFC_Form`)

## Entradas (rule inputs)
| ri! | Tipo |
| `importe` | Decimal |

## Componentes (en orden de aparición, TODOS)
| # | Componente |
| 1 | textField |

## Acciones (botones/links)
| Acción | Qué hace |
| Enviar | submit |

## Criterios de reconstrucción (verificables)
- [ ] Con importe > 1000 el campo Justificación es obligatorio.
"""


class SpecLayoutTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="speclayout_"))

    def make_doc(self, docs: dict) -> Path:
        doc = self.tmp / "_doc_generada"
        for rel, texto in docs.items():
            p = doc / rel
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

    # --- caso feliz ---

    def test_estructura_correcta_exit_0(self):
        proc = self.run_gate(self.make_doc(self.base_docs()))
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
        docs = self.base_docs()
        docs["10-especificacion/navegacion.md"] = (
            "# Nav\n\n## site!DEMO_S\nVer [ficha](pantallas/NO_EXISTE.md).\n"
        )
        proc = self.run_gate(self.make_doc(docs))
        self.assertEqual(proc.returncode, 1)
        self.assertIn("enlace roto", proc.stdout)

    def test_enlace_a_documento_de_onboarding_se_tolera(self):
        """La spec puede entregarse sin los documentos 00-09 al lado."""
        docs = self.base_docs()
        docs["10-especificacion/navegacion.md"] = (
            "# Nav\n\n## site!DEMO_S\nVer [datos](../03-modelo-datos.md).\n"
        )
        proc = self.run_gate(self.make_doc(docs))
        self.assertEqual(proc.returncode, 0, proc.stdout)

    # --- 3. anclas ---

    def test_ancla_rota_exit_1(self):
        docs = self.base_docs()
        docs["10-especificacion/navegacion.md"] = (
            "# Nav\n\n## site!DEMO_S\nVer [regla](reglas-catalogo.md#rulenoexiste).\n"
        )
        proc = self.run_gate(self.make_doc(docs))
        self.assertEqual(proc.returncode, 1)
        self.assertIn("ancla rota", proc.stdout)

    def test_ancla_valida_no_falla(self):
        docs = self.base_docs()
        docs["10-especificacion/navegacion.md"] = (
            "# Nav\n\n## site!DEMO_S\nVer [regla](reglas-catalogo.md#ruledemo_r).\n"
        )
        proc = self.run_gate(self.make_doc(docs))
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

    def test_ficha_sin_criterios_verificables_exit_1(self):
        docs = self.base_docs()
        docs["10-especificacion/pantallas/DEMO_IFC_Form.md"] = FICHA_OK.replace(
            "- [ ] Con importe > 1000 el campo Justificación es obligatorio.",
            "La pantalla se comporta como se espera.",
        )
        proc = self.run_gate(self.make_doc(docs))
        self.assertEqual(proc.returncode, 1)
        self.assertIn("criterios de reconstruccion", proc.stdout)

    # --- 5. higiene ---

    def test_placeholder_sin_rellenar_exit_1(self):
        docs = self.base_docs()
        docs["10-especificacion/reglas-catalogo.md"] += "\n### rule!{{nombre}}\n"
        proc = self.run_gate(self.make_doc(docs))
        self.assertEqual(proc.returncode, 1)
        self.assertIn("placeholder", proc.stdout)

    # --- uso ---

    def test_ruta_inexistente_exit_2(self):
        proc = self.run_gate(self.tmp / "no" / "existe")
        self.assertEqual(proc.returncode, 2)


if __name__ == "__main__":
    unittest.main()
