# Navegación: DEMO App Solicitudes

> Una ficha por CADA site del inventario (1 en esta aplicación). Las páginas enlazan a la
> ficha de pantalla correspondiente o al record type que listan.

## site!DEMO_SITE_Solicitudes

**URL stub**: `/demo-solicitudes` · **Visible para**: `DEMO_GRP_Aprobadores` · **Evidencia**: `site/DEMO_SITE_Solicitudes.xml`

### Páginas (en orden de aparición, TODAS)

| # | Página | Tipo | Objeto destino | → ficha | Visible para |
|---|---|---|---|---|---|
| 1 | Solicitudes | RECORD_LIST | `DEMO Solicitud` | listado del record type — ver [03-modelo-datos.md](../03-modelo-datos.md) | todos los del site |
| 2 | Nueva solicitud | INTERFACE | `DEMO_IFC_SolicitudForm` | [pantallas/DEMO_IFC_SolicitudForm.md](pantallas/DEMO_IFC_SolicitudForm.md) | todos los del site |

**Página de inicio**: `Solicitudes` (primera declarada; el export no marca una por defecto explícita — 🟡 confirmar con el equipo).

### Criterios de reconstrucción (verificables)

- [ ] Un usuario de `DEMO_GRP_Aprobadores` entra en `/demo-solicitudes` y ve exactamente 2 páginas, en este orden: Solicitudes, Nueva solicitud.
- [ ] Un usuario que no pertenece a `DEMO_GRP_Aprobadores` no ve el site.
- [ ] La página *Solicitudes* muestra el listado del record type `DEMO Solicitud`; *Nueva solicitud* abre el formulario de alta.
