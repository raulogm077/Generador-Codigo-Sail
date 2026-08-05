# Tests del plugin appian-toolkit

## `fixtures/mini-export/` — export Appian sintético

Export mínimo en formato *Haul* real (**18 objetos, 18 ficheros**) usado por todos los tests
de la skill `appian-reverse-engineering`. **100% sintético**: nombres `DEMO_*`, UUIDs
`00000000-0000-0000-0000-0000000000NN`. Cero datos reales.

Grafo resultante: **18 nodos · 14 aristas · 7 huérfanos** (los huérfanos son entry points
legítimos: application, site, web API, batch…).

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
| Record Type + CDT + Data Store | `recordType/…`, `datatype/…`, `dataStore/…` | el data store se inventaría desde la Task 3 (`test_detail.py::test_datastore_inventoried`) |
| Constant `DEMO_CONS_ENTITY_SOLICITUD` | `content/…` | entidad de data store: sin ella, `a!queryEntity`/`a!writeToDataStoreEntity` no resolverían contra nada y no habría arista |
| PM `DEMO_PM_ReintentarEnvios` | `processModel/…` | batch nocturno **con prefijo de namespace a propósito** (regresión de M6). Hospeda 5 patrones sin cobertura previa: `a!queryEntity`, `a!writeToDataStoreEntity`, `a!writeRecords`, `<a:processModelUuid>` (subproceso) y `a!isUserMemberOfGroup` |
| Site `DEMO_SITE_Solicitudes` | `site/…` | 2 páginas (RECORD_LIST + INTERFACE). `siteHaul` no tenía cobertura y `site` es un tipo requerido en modo rebuild |

> ⚠️ Al tocar el PM namespaced: el `xmlns:a` **debe** estar declarado en la raíz o
> `ET.parse` falla, `safe_parse` devuelve `None` y el objeto desaparece del inventario
> sin error visible. `test_pm_con_namespace_se_parsea` asserta `parseErrors == 0`.

Regenerable de forma determinista (el generador vive fuera del repo; el fixture es la fuente de verdad).

## Ejecutar los tests

```bash
python -m unittest discover tests -v
```

(Compatible también con `pytest tests/` si está instalado. Solo stdlib.)

Plan al que sirven: `docs/plans/2026-08-04-reverse-engineering-rebuild-spec.md`.
