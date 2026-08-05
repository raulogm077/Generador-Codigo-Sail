# -*- coding: utf-8 -*-
"""Tests de validate_mermaid.py — Tipos A/B/C (Task 5 del plan rebuild-spec).

Corre con:  python -m unittest tests/test_mermaid.py -v
(y también con pytest si está disponible).
"""
import importlib.util
import unittest
from pathlib import Path

SCRIPT = (
    Path(__file__).parents[1]
    / "skills" / "appian-reverse-engineering" / "scripts" / "validate_mermaid.py"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("validate_mermaid", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


VM = _load_module()

# --- Fixtures sintéticos (cero datos reales: solo DEMO_*) ---------------------

ER_3_ENTITIES = '''erDiagram
  DEMO_SOLICITUD ||--o{ DEMO_DOCUMENTO : "contiene"
  DEMO_SOLICITUD }o--|| DEMO_CLIENTE : "pertenece a"
  DEMO_SOLICITUD {
    string id PK
    string idCliente FK
    date fechaAlta
  }
  DEMO_CLIENTE {
    string id PK
    string nombre
  }
  DEMO_DOCUMENTO {
    string id PK
    string idSolicitud FK
  }
'''

# Ejemplo literal de lanes de references/mermaid-rules.md (bloque "Lanes
# (actores)" del Tipo C), envuelto en la cabecera obligatoria del Tipo C
# ('flowchart LR') para formar un diagrama completo.
LANES_LITERAL = '''subgraph LO["👥 Operator"]
  Start((Inicio)):::startNode
  T1[👤 Rellenar formulario]:::userTask
end
subgraph LA["👥 Approver"]
  T2[👤 Aprobar]:::userTask
end
subgraph LS["⚙️ Sistema"]
  T3[🔌 Notificar SAP]:::serviceTask
  End(((Fin))):::endNode
end
'''

TYPE_C_DIAGRAM = "flowchart LR\n" + LANES_LITERAL


def _type_a_31_nodes() -> str:
    """Flowchart Tipo A con 31 nodos (N1..N31): debe seguir rechazándose."""
    lines = ["flowchart TD"]
    for i in range(1, 31):
        lines.append('  N{0}["Paso {0}"] --> N{1}["Paso {1}"]'.format(i, i + 1))
    return "\n".join(lines)


class TestMermaidValidator(unittest.TestCase):

    # --- Tipo B: erDiagram ---------------------------------------------------

    def test_er_diagram_accepted(self):
        clean, _warns = VM.sanitize(ER_3_ENTITIES)
        self.assertEqual(clean.strip().splitlines()[0].strip(), "erDiagram")
        # Pasa sin reescritura destructiva: relaciones canónicas intactas.
        self.assertIn('DEMO_SOLICITUD ||--o{ DEMO_DOCUMENTO : "contiene"', clean)
        self.assertIn('DEMO_SOLICITUD }o--|| DEMO_CLIENTE : "pertenece a"', clean)

    def test_er_bad_relation_rejected(self):
        bad = 'erDiagram\n  DEMO_A =>> DEMO_B : "x"\n'
        with self.assertRaises(ValueError):
            VM.sanitize(bad)

    # --- Tipo C: flowchart con subgraph (lanes) ------------------------------

    def test_subgraph_lanes_accepted(self):
        clean, _warns = VM.sanitize(TYPE_C_DIAGRAM)
        self.assertTrue(clean.strip().startswith("flowchart LR"))
        # Los lanes sobreviven tal cual (pass-through, no se sanean como Tipo A).
        self.assertIn('subgraph LO["👥 Operator"]', clean)
        self.assertIn('subgraph LA["👥 Approver"]', clean)
        self.assertIn('subgraph LS["⚙️ Sistema"]', clean)
        self.assertIn("End(((Fin))):::endNode", clean)

    def test_type_c_nodo_huerfano_rechazado(self):
        """Regresion (auditoria B3): el Tipo C era pass-through — aceptaba
        cualquier basura mientras los subgraph estuvieran emparejados."""
        diagrama = "\n".join([
            "flowchart TD",
            "  subgraph Solicitante",
            "    A[Enviar] --> B[Revisar]",
            "  end",
            "  ESTO ES SINTAXIS INVALIDA ~~~> ??? |||",
        ])
        with self.assertRaises(ValueError):
            VM.sanitize(diagrama)

    def test_type_c_supera_tope_de_nodos_rechazado(self):
        """El Tipo C tiene tope documentado (presentation-rules: 25 nodos)."""
        lineas = ["flowchart TD", "  subgraph Lane"]
        for i in range(40):
            lineas.append(f"    N{i}[Paso {i}] --> N{i + 1}[Paso {i + 1}]")
        lineas.append("  end")
        with self.assertRaises(ValueError):
            VM.sanitize("\n".join(lineas))

    def test_subgraph_unbalanced_rejected(self):
        bad = (
            "flowchart LR\n"
            'subgraph L1["Lane sin cerrar"]\n'
            "  Start((Inicio)):::startNode\n"
        )
        with self.assertRaises(ValueError):
            VM.sanitize(bad)

    # --- Tipo A: sin cambios -------------------------------------------------

    def test_type_a_unchanged(self):
        # 31 nodos > MAX_NODES=30 → sigue rechazándose (no relajar el Tipo A).
        with self.assertRaises(ValueError):
            VM.sanitize(_type_a_31_nodes())


if __name__ == "__main__":
    unittest.main()
