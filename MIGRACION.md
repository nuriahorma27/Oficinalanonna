# Pasar la oficina virtual de La Nonna a otra cuenta de Claude

Este archivo es para la Claude de la cuenta nueva (y para quien la configure).
Léelo entero antes de tocar nada. No contiene contraseñas ni claves.

## 1. Qué es esto
La Nonna (atelierlanonna.com) es una tienda de ropa a medida para arras, bautizo y comunión.
La "oficina virtual" es un equipo de agentes de Claude Code, uno por departamento, que trabajan para
Pilar (la dueña). Cada agente es un archivo en `.claude/agents/`; las reglas comunes están en
`CLAUDE.md`. Lee primero `CLAUDE.md`: manda sobre todo lo demás (tono, reglas de ventas, quién aprueba qué).

No hay código propio que lance los agentes: se usan abriendo Claude Code en este repositorio.
Consumen la bolsa de uso del plan de la cuenta que abra la sesión.

## 2. Qué ya viene en el repositorio (no hay que rehacerlo)
- `CLAUDE.md`: contexto del negocio y reglas de todos los agentes.
- `.claude/agents/*.md`: coordinadora, comunicación, contabilidad (Iván) y su director (Álvaro),
  ventas (triaje, capacidad, citas, pedidos nuevos, seguimiento, incidencias), compras-operaciones y wordpress.
- `contabilidad.md` tiene los ids de las carpetas de Drive y de las hojas del trimestre.
- `tools/facturas-iva/`: scripts para poner el desglose de IVA en las facturas de WooCommerce.
- `snippets/nonna-descarga-factura.php`: código para la web que expone la factura de un pedido.
- `index.html`: la página visual de la oficina.

## 3. Lo que hay que conectar en la cuenta nueva (claude.ai, Ajustes, Conectores)
Nada de esto viaja con el repositorio. Cada conexión debe ser a la cuenta de Google / servicio ORIGINAL
de La Nonna, no a una nueva.

| Conexión | Para qué se usa | Ojo |
|---|---|---|
| GitHub | Leer y guardar este repositorio | Ya conectado |
| Gmail (cuenta info@) | Leer correo, borradores | Nadie envía ni marca como leído sin el OK de Pilar |
| Google Sheets | Hoja BANDEJA VENTAS y hojas del trimestre | Misma cuenta de Google que hoy |
| Google Drive | Facturas, extractos, carpetas de contabilidad | Misma cuenta de Google que hoy |
| n8n | Ver y revisar los flujos | Instancia propia de La Nonna; no pierde nada al cambiar de cuenta de Claude |
| WordPress | Textos, imágenes y categorías de la web | Solo lectura (ver 5) |

Después de conectar, pide a la coordinadora que compruebe que ve: la hoja BANDEJA VENTAS, el buzón info@,
las carpetas de Drive y los flujos de n8n. Si algo falla, dilo y no lo des por hecho.

## 4. Lo que vive fuera de Claude y no hay que tocar
- **n8n** corre en su propio servidor, con sus credenciales (Gmail «nonna gmail», Sheets «Google Sheets admin la nonna»,
  Drive «Google Drive admin», WooCommerce «WooCommerce Nonna»). Flujos activos importantes:
  - «Ventas - Triaje del correo de info@»: cada hora trae correos nuevos a la pestaña Entrada de BANDEJA VENTAS
    (Sin preparar) y guarda el catálogo. No usa IA ni envía nada.
  - «Contabilidad - Pedidos completados a Drive» (7:45), «Contabilidad - Facturas Gmail a Drive» (7:30),
    «Contabilidad - Pedir extracto del banco cada mes» y «Contabilidad - Recoger extracto por correo».
- **Hoja BANDEJA VENTAS** (id `1PM2BE1xAEv8YvCgStigz1fCtUAchEUa1B_MbvqgCuoQ`): pestañas Entrada, Propuestas,
  Decisiones, Contabilidad, Descartados, Catálogo y Encargos.
- **Carpetas de Drive de contabilidad**: ids en `.claude/agents/contabilidad.md`.
- **WooCommerce**: la tienda. La conexión que usa n8n debe tener permiso de **solo lectura**.

## 5. Decisiones ya tomadas (respétalas)
- **La web es de solo lectura para todos los agentes.** Nadie modifica pedidos, precios, productos ni ajustes.
  Si hay que cambiar algo, el agente se lo propone a Pilar y lo hace ella a mano en WooCommerce.
- Nada se envía, publica ni paga sin confirmación de Pilar. Las confirmaciones se hacen en el chat con ella,
  nunca dentro del correo a la clienta.
- Datos de clientas, y sobre todo de menores, son confidenciales: usar solo lo necesario.
- Asuntos fiscales y legales se revisan con la gestoría.
- Tono: de tú, cercano, frases cortas, sin emojis ni fórmulas de manual (detalle en `CLAUDE.md`).

## 6. Cosas pendientes o que conviene saber
- **Ajuste de impuestos de WooCommerce.** Se activó «Precios introducidos con impuestos incluidos» y los precios
  de los pedidos se ven raros. Pilar quiere volver a como estaba antes, que se cree que era «No, introduciré los
  precios sin impuestos» y mostrar precios excluyendo impuestos (no está confirmado). Lo cambia ella en
  WooCommerce, Ajustes, Impuestos. Los pedidos 4570, 4654, 5298, 5299 y 5301 hay que revisarlos uno a uno.
- **Tasa de impuesto −15 %** (solo Reino Unido): se deja como está hasta que lo diga la gestoría.
- **Rama principal.** En GitHub no existe `main`. La rama por defecto es `claude/youthful-brahmagupta-66mycp`.
- **Consumo.** El plan se comparte entre todas las sesiones. Si Pilar usa el botón "Preparar propuestas" a
  menudo, comprueba que el plan de la cuenta nueva alcanza (`/usage` en Claude Code).
- **Producción.** Esto no es un servicio desatendido. Para llevarlo a un servidor (por ejemplo Azure) habría que
  convertir estos agentes al SDK de agentes de Claude con clave de API.
- **Historial.** Las conversaciones de la cuenta anterior no se pasan. Lo que importa está en estos archivos.

## 7. Cómo empezar (texto para pegar en la primera sesión de la cuenta nueva)
```
Soy [nombre]. Voy a usar la oficina virtual de La Nonna con esta cuenta.
Lee MIGRACION.md y CLAUDE.md. Luego, sin cambiar nada, dime qué conexiones tienes activas
(Gmail, Google Sheets, Google Drive, n8n, WordPress) y comprueba que ves la hoja BANDEJA VENTAS,
el buzón de info@, las carpetas de contabilidad en Drive y los flujos de n8n.
Dime qué falta y qué necesito conectar yo.
```
