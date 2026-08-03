# Reglas de presentación

> Reglas obligatorias para la **distribución y legibilidad** de cada entregable. Léelas antes de escribir cualquier `.md` de `_doc_generada/`. El objetivo no es generar documentos densos, sino documentos que se **lean en cascada** según el interés del lector.

---

## Regla 1: principio de cascada (TL;DR → vista → detalle)

Todo entregable se estructura en **tres niveles de profundidad**, en este orden estricto:

| Nivel | Para quién | Qué contiene | Longitud máxima |
|---|---|---|---|
| **TL;DR** (arriba del todo) | Lector que solo quiere saber qué hay aquí | 3-5 líneas en prosa o bullets cortos | ≤ 5 líneas |
| **Vista** (después del TL;DR) | Lector que quiere el panorama | Diagrama principal + tabla resumen 1 fila por elemento | ≤ ½ pantalla |
| **Detalle** (al pie) | Lector que necesita la ficha técnica | Subsecciones por elemento con todos los datos | sin límite |

**Prohibido**: empezar un documento con una tabla de 50 filas. Si lo necesitas, ponla en la sección Detalle al final, no al principio.

**Patrón canónico al inicio de cada `.md`:**

```markdown
# <Título>

> **TL;DR**: <una frase sobre qué hace este documento>.
> Contenido: <N elementos / N hallazgos>. <Riesgo principal o ninguno>.
> <Recomendación de lectura: "Leer la Vista; bajar al Detalle solo si X.">

## Vista

[Diagrama]

[Tabla resumen: 1 fila por elemento, máximo 10 columnas, columnas escaneables]

## Detalle

### <Elemento 1>
...
```

---

## Regla 2: diagrama antes que tabla, tabla antes que prosa

El lector procesa información visual antes que tabular antes que prosaica. En cada sección:

1. Si hay relación entre elementos, **diagrama** primero.
2. Si hay comparación entre N elementos, **tabla** después.
3. Si hay matiz / contexto, **prosa breve** después.

Ejemplos:

- **Arquitectura**: diagrama (objetos + relaciones) → tabla por capa (1 fila por objeto) → notas.
- **Modelo de datos**: ER diagram → tabla por record/CDT → notas.
- **Seguridad**: árbol de grupos → matriz objeto×grupo → reglas en SAIL.
- **Procesos**: BPMN diagram → tabla 1 fila por nodo → ficha por nodo.

---

## Regla 3: una idea por tabla, una idea por diagrama

Si una tabla necesita 12+ columnas, la dividiste mal. Si un diagrama necesita 30+ nodos, lo dividiste mal.

**Límites duros:**

| Elemento | Límite |
|---|---|
| Columnas por tabla | ≤ 8 |
| Filas por tabla en sección "Vista" (resumen) | ≤ 15 |
| Nodos por diagrama Tipo A (flowchart) | ≤ 30 |
| Entidades por diagrama Tipo B (erDiagram) | sin techo, criterio de legibilidad — ver `references/mermaid-rules.md` Tipo B |
| Nodos por diagrama Tipo C (BPMN-styled) | ≤ 25 |

Si excedes, particiona por subdominio / lane / tipo. Cada partición es un sub-diagrama / sub-tabla con título descriptivo. El documento gana un **índice de sub-vistas** al inicio.

---

## Regla 4: tablas escaneables

Las tablas se leen verticalmente columna a columna. Para que sean escaneables:

- **Columna 1 es siempre el identificador** del elemento (nombre técnico).
- **Columnas con respuesta corta** (Sí/No, valor numérico, etiqueta de una palabra) van pegadas a la izquierda.
- **Columnas con respuesta larga** (descripción, callers, notas) van a la derecha.
- **Estados** con emoji-color en una columna corta (✅/🔵/🟡/🔴).
- **Nunca** texto de >100 caracteres dentro de una celda. Si es necesario, ese campo va en la ficha de Detalle, no en la tabla.

Ejemplo correcto:

| Process Model | Trigger | Lanes | Pools externos | Críticos | Diagrama |
|---|---|---|---|---|---|
| `PM_Gestion` | manual | 2 | 1 (SAP) | 🔴 | [ver](./PM_Gestion.svg) |
| `PM_Batch` | timer | 0 | 0 | 🟡 | [ver](./PM_Batch.svg) |

Ejemplo **incorrecto** (no escaneable):

| Process Model | Descripción detallada | Quién lo llama desde el frontend y backend, incluyendo procesos hermanos | ... |

---

## Regla 5: fichas de Detalle uniformes

Cada ficha de Detalle (sección `### <Elemento>` en el bloque Detalle) sigue **siempre** esta estructura:

```markdown
### `<nombre_tecnico>` — <nombre_visible>

**TL;DR de la ficha** (1 línea): qué es y para qué sirve.

| Campo | Valor |
|---|---|
| ... ficha técnica con 5-10 campos clave ... |

**Detalle / Notas relevantes** (si aplica, 3-5 líneas):
- ...

**Evidencia**: `<ruta_xml>#<fragmento>` · **Estado**: ✅/🔵/🟡/🔴
```

No mezcles tabla de ficha con prosa larga en medio. La tabla compacta los datos; la prosa va en "Detalle / Notas" claramente separado.

---

## Regla 6: índice navegable cuando haya >5 fichas de Detalle

Si la sección Detalle de un documento tiene más de 5 fichas, añade un **índice navegable** al principio de la sección con anclas markdown:

```markdown
## Detalle

Saltar a:
- [`PM_GestionExpedientes`](#pm_gestionexpedientes--gesti%C3%B3n-de-expedientes)
- [`PM_NotificarCliente`](#pm_notificarcliente)
- [`PM_ArchivarExpediente`](#pm_archivarexpediente)
- ... (12 más)
```

Los visualizadores Markdown (GitHub, VSCode, Obsidian, IntelliJ) generan anclas automáticamente desde los `### <título>`. Comprobar que los `#` en la URL coinciden con la versión lowercased + dashed del título.

---

## Regla 7: emojis de estado consistentes

Toda la documentación usa esta paleta de 4 estados, **siempre estos emojis, siempre con este significado**:

| Emoji | Significado |
|---|---|
| ✅ | Confirmado por evidencia explícita en el export |
| 🔵 | Inferido razonablemente (evidencia indirecta) |
| 🟡 | Pendiente de validación con responsable funcional/técnico |
| 🔴 | Riesgo detectado / anti-patrón / requiere atención |

No añadas otros emojis de estado (⚠️, ❗, ✔️, ☑️, etc.). La paleta de 4 es suficiente y evita ruido.

Los emojis **temáticos** sí están permitidos en etiquetas de diagramas Tipo C BPMN (👤 user task, 🔌 integración, 💾 datastore, etc.) — son parte de la convención de notación.

---

## Regla 8: enlaces internos, no copia

Cada hallazgo se documenta **una vez** en su documento canónico, y se referencia desde otros con enlace Markdown:

```markdown
La Integration `INT_SAP_Crear` es llamada por `PM_GestionExpedientes`.
Detalle en [05-integraciones-consumidas.md#int_sap_crear](./05-integraciones-consumidas.md#int_sap_crear--sap-crear-expediente).
```

**Prohibido**: duplicar la ficha técnica de un objeto en dos documentos. Si se referencia desde otro, enlace al original.

**Excepción**: el `00-resumen-ejecutivo.md` sí menciona objetos clave brevemente, pero siempre con enlace al documento de detalle.

---

## Regla 9: longitud máxima por documento

Cada entregable tiene un objetivo de longitud razonable. Si excede el doble, está mal estructurado.

| Entregable | Objetivo | Máximo razonable |
|---|---|---|
| `00-resumen-ejecutivo.md` | 1-2 pantallas | 3 pantallas |
| `01-funcional.md` | 3-5 pantallas | 10 pantallas (procesos = casos de uso × pasos) |
| `02-arquitectura.md` | 2-3 pantallas | 5 pantallas |
| `03-modelo-datos.md` | depende del nº records/CDTs | 1 pantalla por record/CDT en Detalle |
| `04-seguridad-grupos.md` | 2-3 pantallas | 5 pantallas |
| `05-integraciones-consumidas.md` | 1 pantalla por integración + resumen | sin límite |
| `06-apis-expuestas.md` | 1 pantalla por web API + resumen | sin límite |
| `07-batches.md` | 1 pantalla por batch + resumen | 5 pantallas |
| `08-procesos-bpmn/<PM>.md` | 1 pantalla (TL;DR + diagrama + tabla) | 3 pantallas |
| `08-procesos-bpmn/indice.md` | 1-2 pantallas | 3 pantallas |
| `09-valor-adicional.md` | depende de los hallazgos | sin límite, pero con índice |
| `INVENTARIO.md` | 1 tabla por categoría | sin límite |

"1 pantalla" ≈ 50 líneas Markdown ≈ unas 1000 palabras visibles.

---

## Regla 10: bloques de "Resumen rápido" al final de cada documento

Cada `.md` cierra con una sección `## Resumen rápido` (≤ 10 líneas, bullets cortos) que enumera los hallazgos clave **del documento**, para que el lector que ojea cierre con un mental model claro.

Ejemplo en `05-integraciones-consumidas.md`:

```markdown
## Resumen rápido

- Total Integrations: 12 · Total Connected Systems: 4.
- Sistemas externos: SAP ERP, Salesforce, Microsoft Graph, custom REST.
- 3 integraciones sin manejo de error explícito 🔴.
- 1 integración con timeout muy alto (60s) 🟡.
- 2 integraciones con secretos detectados y enmascarados ✅.
- Top caller: `PM_GestionExpedientes` (4 integraciones).
```

Es el equivalente al TL;DR pero al pie, ya con cifras concretas tras leer el documento.

---

## Checklist antes de cerrar cada documento

Antes de escribir el `.md` a disco, verifica:

- [ ] Tiene **TL;DR** al inicio (≤ 5 líneas).
- [ ] Tiene **Vista** con diagrama y tabla resumen escaneables.
- [ ] Tiene **Detalle** al pie con fichas uniformes.
- [ ] Tiene **Resumen rápido** al final con cifras concretas.
- [ ] Ninguna tabla excede 8 columnas o 15 filas en la Vista.
- [ ] Ningún diagrama excede el límite por tipo (Tipo A 30, B 12, C 25).
- [ ] Si hay >5 fichas de Detalle, añadir índice navegable.
- [ ] Emojis de estado de la paleta de 4 (✅/🔵/🟡/🔴).
- [ ] Cero secciones vacías. Si no hay contenido para una sección, omitirla.
- [ ] Cero placeholders sin rellenar (`<TODO>`, `xxx`, `lorem`).
- [ ] Enlaces a otros documentos en lugar de duplicar fichas.
- [ ] Cada ficha de Detalle tiene **evidencia** (ruta + fragmento).
