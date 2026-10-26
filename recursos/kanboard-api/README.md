# Kanboard: API JSON-RPC

Material de apoyo para automatizar Kanboard (crear o editar tareas, leer comentarios, armar reportes) desde scripts o desde Claude Code.

| Archivo | Para qué |
|---|---|
| [`KANBOARD_API.md`](KANBOARD_API.md) | Referencia: cómo autenticarse, helper en Python, métodos más usados y errores conocidos. Se puede usar como `CLAUDE.md` en otro proyecto |
| [`Kanboard_API.postman_collection.json`](Kanboard_API.postman_collection.json) | Colección Postman (16 solicitudes) para probar accesos. Se importa en Postman y se completan las variables `kb_base_url`, `kb_user` y `kb_token` |

> **Advertencia:** ninguno de los dos archivos contiene tokens. Cargarlos solo en variables de entorno o en un Environment de Postman, nunca en el repositorio.

Problemas conocidos: ver TRB-019 en [`docs/07_Troubleshooting.md`](../../docs/07_Troubleshooting.md#trb-019--la-api-json-rpc-de-kanboard-devuelve-401-con-un-token-de-usuario). La ficha del componente está en [`docs/03_Componentes.md`](../../docs/03_Componentes.md#kanboard-gestión-de-tareas).
