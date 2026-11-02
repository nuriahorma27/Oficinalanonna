# 🧵 Oficina virtual · La Nonna

Equipo de agentes de Claude para La Nonna (ropa a medida de arras, bautizo y comunión).

- `.claude/agents/` → un agente por departamento + coordinadora.
- `CLAUDE.md` → contexto del negocio y reglas que comparten todos los agentes.
- `index.html` → vista visual de la oficina (abre el archivo en el navegador): elige un departamento, mira qué hace y copia ejemplos de petición.

## Uso
Abre el repo con Claude Code y escribe, por ejemplo:

```
@coordinadora ha entrado un pedido de comunión para el 18 de mayo
@comunicacion calendario de Instagram para noviembre
@contabilidad resumen de cobros pendientes
```

## Siguientes pasos posibles
- Conectar Gmail / Google Drive para que los agentes lean y preparen borradores reales.
- Añadir más departamentos (p. ej. e-commerce, marketing de pago).
- Hacer la parte visual interactiva con chat real (requiere API de Claude).
