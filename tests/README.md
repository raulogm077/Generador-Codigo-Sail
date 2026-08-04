# Tests del plugin appian-toolkit

## `fixtures/mini-export/` — export Appian sintético

Export mínimo en formato *Haul* real (13 objetos, 15 ficheros) usado por todos los tests
de la skill `appian-reverse-engineering`. **100% sintético**: nombres `DEMO_*`, UUIDs
`00000000-0000-0000-0000-0000000000NN`. Cero datos reales.

| Objeto | Fichero | Papel en los tests |
|---|---|---|
| Application `DEMO App Solicitudes` | `application/DEMO_App.xml` | raíz del export |
| Interface `DEMO_IFC_SolicitudForm` | `content/…Form.xml` | 4 componentes, `showWhen: ri!importe > 1000`, llama a `rule!DEMO_VAL_ValidarImporte` y `rule!DEMO_IFC_SolicitudList` |
| Interface `DEMO_IFC_SolicitudList` | `content/…List.xml` | **caso del bug del grafo**: solo es llamada como `rule!…` desde otra interfaz — no debe salir huérfana |
| Rule `DEMO_QR_GetSolicitudes` | `content/…` | `a!queryRecordType` con URN del record type |
| Rule `DEMO_VAL_ValidarImporte` | `content/…` | **1 solo caller** — debe sobrevivir al catálogo del Nivel 3 |
| Decision `DEMO_DEC_NivelAprobacion` | `content/…` | 3 filas importe→nivel |
| Constant `DEMO_CONS_ESTADOS` | `content/…` | dominio `BORRADOR;ENVIADO;APROBADO;RECHAZADO` (máquina de estados) |
| Integration + CS + Web API | `content/…`, `connectedSystem/…` | borde de la app |
| PM `DEMO_PM_AprobarSolicitud` | `processModel/…` | 7 nodos, 3 process variables, gateway por importe |
| Record Type + CDT + Data Store | `recordType/…`, `datatype/…`, `dataStore/…` | el data store NO lo inventaría el parser actual (lo habilita la Task 3 del plan) |

Regenerable de forma determinista (el generador vive fuera del repo; el fixture es la fuente de verdad).

## Ejecutar los tests

```bash
python -m unittest discover tests -v
```

(Compatible también con `pytest tests/` si está instalado. Solo stdlib.)

Plan al que sirven: `docs/plans/2026-08-04-reverse-engineering-rebuild-spec.md`.
