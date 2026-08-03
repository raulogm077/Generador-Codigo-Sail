# Principios de ejecución y reglas de presentación

Documento de **lectura obligatoria** antes de la Fase 4 (generación de entregables) y antes de invocar cualquier subagente. Concentra los criterios no negociables que aplican a TODOS los entregables y a TODOS los agentes.

---

## 1. Principios de ejecución (no negociables)

Aplican a cada `.md`, cada diagrama, cada celda de tabla.

1. **No inventar.** Si un dato no aparece en los artefactos, márcalo `⚠️ no determinado` y explica por qué. Nunca completes con suposiciones plausibles.

2. **Etiqueta cada afirmación con su estado**:
   - ✅ **Confirmado** por artefactos (con evidencia: ruta + fragmento).
   - 🔵 **Inferido** razonablemente (explica la evidencia parcial).
   - 🟡 **Pendiente** de validación con responsable funcional/técnico.
   - 🔴 **Riesgo** detectado.

3. **Trazabilidad obligatoria**: cada afirmación enlaza al archivo XML/XSD del que se extrajo (ruta relativa al export). Evidencia mínima: `<ruta>#<fragmento>` o `<ruta>:<línea>` + nivel de confianza.

4. **Cero relleno**: si una sección no tiene contenido real, **omítela**. Nunca dejes `<TODO>`, `<placeholder>`, `xxx`, `lorem ipsum`, "TBD" o equivalentes.

5. **Cero duplicación**: cada hallazgo se documenta una sola vez; se referencia con anclas Markdown.

6. **Nombres reales** (técnico + visible) en cada referencia, nunca placeholders.

7. **Conocimiento accionable > listados**. Cualquier objeto listado debe estar conectado a una funcionalidad y a una recomendación de uso/mantenimiento.

8. **Seguridad por defecto.** Detecta y enmascara secretos, tokens, passwords, URLs con credenciales embebidas, claves API antes de escribir nada. Documéntalos como riesgo (sin exponer el valor). Ver `references/security-rules.md`.

9. **Diagramas robustos.** Mermaid debe pasar las reglas de `references/mermaid-rules.md`. BPMN debe seguir el mapeo de `references/bpmn-mapping.md`. Si no se pueden sanear/renderizar, sustituye por tabla equivalente.

10. **Idioma**: español neutro técnico salvo que el usuario pida otro.

---

## 2. Reglas de presentación (cómo distribuir la información)

La documentación es **inservible** si no se puede leer fácilmente. Aplica a **cada** entregable.

### 2.1 Estructura uniforme de cada documento

Todos los `.md` siguen la misma jerarquía para que sean **escaneables**:

1. **🎯 TL;DR** — Resumen ejecutivo en 2-4 frases al inicio. Sin tablas, sin diagramas. Lo que verá quien solo lea las primeras líneas.
2. **📊 Volumen / cifras clave** — Tabla pequeña (≤ 8 filas) con los números que sitúan el documento.
3. **🗺️ Vista global** (si aplica) — Un único diagrama o tabla resumen que permite navegar al detalle.
4. **📋 Catálogo en tabla resumen** — **Antes** del detalle individual, una tabla escaneable con una fila por objeto: nombre, atributos clave (≤ 6 columnas), estado, link a su detalle.
5. **Detalle por objeto** — Subsecciones con estructura **idéntica** (mismos campos en el mismo orden) para todas las entradas del mismo tipo. Convierte el detalle en algo escaneable, no en prosa libre.
6. **🔍 Hallazgos** — Solo si los hay. Lista corta, accionable, con severidad (🔴/🟡/✅) y evidencia.

### 2.2 Reglas duras de presentación

- **Una idea por celda.** Si una celda de tabla excede 80 caracteres, divide en columnas o saca a una subsección.
- **Tablas resumen antes que detalle.** Nadie lee una pared de fichas. La tabla resumen permite encontrar el objeto, el detalle responde la pregunta concreta.
- **Diagramas con TL;DR adyacente.** Antes o después de cada diagrama, una frase que explique qué se está viendo y qué hallazgo esperar.
- **Iconos como pistas visuales.** Usa emojis consistentes en cabeceras: 🎯 TL;DR · 📊 Volumen · 🗺️ Mapa · 📋 Catálogo · 🔍 Hallazgos · ⚠️ Riesgos · 👥 Actores · 🔌 Integraciones · 💾 Datos · 📐 BPMN profesional · 🖼 Preview. Sin abusar — uno por sección, no más.
- **Status labels uniformes en todo el documento**: ✅ Confirmado · 🔵 Inferido · 🟡 Pendiente · 🔴 Riesgo. Nunca mezcles con otras (✓/✗/⚡/etc).
- **Detalles colapsables**: si el detalle por entrada es largo y repetitivo (CDTs con muchos campos, process models con muchos nodos), considera presentar en tabla compacta con columna "ver detalle" que enlaza al `.md` hermano.

### 2.3 Límites de tamaño de diagramas (criterio: legibilidad, no número arbitrario)

- `flowchart` Tipo A: ≤ 30 nodos.
- `erDiagram` Tipo B: **sin techo absoluto**. Los modelos de datos en proyectos Appian pueden ser muy grandes; truncarlos es peor que mostrarlos. Aplica criterio de legibilidad:
  - Hasta ~15 entidades: un único diagrama global está bien.
  - Entre ~15-30 entidades: global resumido + diagramas por subdominio.
  - >30 entidades: obligatorio siempre por subdominios.
- `flowchart` Tipo C (BPMN preview): ≤ 25 nodos. Si excede, partir en sub-procesos/call activities.

---

## 3. Reglas específicas para procesos (carpeta `08-procesos-bpmn/`)

Cada process model produce **3 ficheros** en lugar de uno:

- `<PM>.bpmn` — **BPMN 2.0 XML profesional** abrible en Camunda Modeler, draw.io, bpmn.io demo, Signavio. Es la **fuente de verdad** para BPMN auténtico (lanes/pools, iconos OMG, message flows, boundary events).
- `<PM>.mmd` — **Mermaid Tipo C** estilizado con shapes BPMN, iconos emoji, colores estándar y lanes como `subgraph`. Es la vista preliminar embebida en el Markdown.
- `<PM>.svg` — render del `.mmd` con `mmdc` si está disponible. Si no, el `.mmd` queda embebido en `<PM>.md` y GitHub/VSCode lo renderizan on-the-fly.
- `<PM>.md` — Documento siguiendo `assets/markdown-templates/08-procesos-bpmn/pm-template.md`: TL;DR, diagrama, paso a paso funcional, integraciones tocadas, asignación de tareas, manejo de excepciones, hallazgos.

`indice.md` es una tabla escaneable con una fila por PM y enlaces a los 3 ficheros. **No** apiles el detalle de cada PM en el índice — el índice es navegación, los `<PM>.md` son contenido.

---

## 4. Reglas específicas para modelo de datos (`03-modelo-datos.md`)

- **Cobertura del 100%**: el catálogo (tablas) **siempre** incluye todos los records y CDTs del export, sin excepción. Los modelos grandes no se truncan: se particionan visualmente.
- **Estrategia de diagramas según tamaño** (guía de legibilidad, no techo arbitrario):
  - Hasta ~15 entidades: un único `erDiagram` global (`diagrams/modelo-datos.svg`).
  - Entre ~15 y ~30 entidades: diagrama global resumido con entidades clave + relaciones principales, **más** diagramas de detalle por subdominio.
  - Más de ~30 entidades: obligatorio siempre partir en sub-diagramas por subdominio funcional (`diagrams/modelo-datos-{{subdominio}}.svg`). Añadir un "mapa de subdominios" como índice navegable.
- **Criterio de subdominio**: agrupar entidades que se referencian entre sí o que comparten contexto funcional. Cada subdominio suele tener 8-15 entidades.
- Cada Record Type tiene su **ficha estructurada** con los mismos campos en el mismo orden — escaneable por columnas, no por prosa libre.

---

## 5. Regla de oro de generación de salida

- **Cada celda/campo** debe tener: valor real **o** marcador explícito de pendiente con motivo. Nunca `<TODO>`, `<placeholder>`, `xxx`, `lorem ipsum`.
- Si una sección no tiene evidencia, escribe: *"No se ha encontrado evidencia suficiente en los artefactos analizados. Pendiente de validación con [rol sugerido]."* — esto es información útil, no un fallo.
- Estructura de evidencia: `Evidencia: <ruta>#<fragmento o línea> — Confianza: alta/media/baja`.
- Etiquetas de estado consistentes en toda la salida: ✅ Confirmado · 🔵 Inferido · 🟡 Pendiente · 🔴 Riesgo.
- Enlaces internos entre documentos con anclas Markdown (`[ver §3.2 Records](./03-modelo-datos.md#records)`) para no duplicar.
