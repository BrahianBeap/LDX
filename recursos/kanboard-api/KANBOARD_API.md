# Trabajar con la API de Kanboard

Referencia para usar la API JSON-RPC de Kanboard (crear/editar tareas, leer comentarios, mover
columnas, generar reportes) desde Claude Code u otro script. Guardá este archivo como `CLAUDE.md`
en la raíz de tu proyecto, o linkealo desde tu `CLAUDE.md` existente, para que Claude lo tenga
como contexto automáticamente.

## Cómo funciona

Es **JSON-RPC 2.0**, no REST: un único endpoint, un solo verbo POST, y el campo `method` del JSON
decide qué acción se ejecuta.

- Endpoint: `https://TU-INSTANCIA-KANBOARD/jsonrpc.php`
- Auth: HTTP Basic. Hay dos tipos de token y cada uno se usa con un usuario distinto:
  - **Token personal** (tu perfil → API): usuario = **tu login** de Kanboard (ej. `elias.alfonzo`).
  - **Token de la aplicación** (Configuración → API, solo administradores): usuario = `jsonrpc`.
  Mezclarlos devuelve `401 Unauthorized` (ver TRB-019 en `docs/07_Troubleshooting.md`). **El token no es tu contraseña de login.**
- En este cluster, el endpoint publicado es `https://10.143.11.8/jsonrpc.php` (gateway de Franco), con certificado de la CA interna `AutoridadOSS`.
- Cada llamada: `{"jsonrpc": "2.0", "method": "<metodo>", "id": 1, "params": {...}}`
- La respuesta trae el resultado en `result`, o un `error` si algo falló.

> **Importante:** nunca hardcodees el token en el código ni lo subas a un repo. Usalo como
> variable de entorno (`KB_TOKEN`) y cada persona genera el suyo propio desde su perfil.

## Helper base (Python)

```python
import urllib.request, json, base64, ssl, os

KB_URL = "https://TU-INSTANCIA-KANBOARD/jsonrpc.php"
KB_USER = os.environ.get("KB_USER", "jsonrpc")  # tu login si usás token personal
KB_TOKEN = os.environ["KB_TOKEN"]  # exportar antes: export KB_TOKEN="tu-token"

def call(method, params=None):
    payload = json.dumps({
        "jsonrpc": "2.0", "method": method, "id": 1, "params": params or {}
    }).encode()
    req = urllib.request.Request(KB_URL, data=payload, headers={
        "Content-Type": "application/json",
        "Authorization": "Basic " + base64.b64encode(f"{KB_USER}:{KB_TOKEN}".encode()).decode()
    })
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE  # solo si tu instancia usa una CA interna no reconocida
    with urllib.request.urlopen(req, context=ctx) as resp:
        return json.loads(resp.read())["result"]
```

## Métodos más usados

**Crear una tarea**
```python
task_id = call("createTask", {
    "title": "Título de la tarea",
    "project_id": 1,
    "owner_id": 5,            # id del usuario asignado
    "description": "Detalle...",
    "color_id": "yellow"
})
```

**Editar una tarea** (no mueve de columna, ver `moveTaskPosition` abajo)
```python
call("updateTask", {"id": task_id, "description": "Nuevo detalle", "time_spent": 2})
```

**Ver las columnas de un proyecto** (para obtener `column_id` real antes de mover algo)
```python
columnas = call("getColumns", {"project_id": 1})
```

**Mover una tarea de columna**
```python
call("moveTaskPosition", {
    "project_id": 1, "task_id": task_id,
    "column_id": 7, "position": 1, "swimlane_id": 1
})
```

**Leer una tarea** (solo trae `description`, no comentarios)
```python
tarea = call("getTask", {"task_id": task_id})
```

**Leer los comentarios de una tarea** (llamada aparte, ver advertencia abajo)
```python
comentarios = call("getAllComments", {"task_id": task_id})
```

**Agregar un comentario**
```python
call("createComment", {"task_id": task_id, "user_id": 5, "content": "Avance..."})
```

**Buscar tareas**
```python
resultados = call("searchTasks", {"project_id": 1, "query": "texto a buscar"})
```

**Traer todo un tablero** (todas las columnas con sus tareas — útil para reportes)
```python
tablero = call("getBoard", {"project_id": 1})
```

**Cerrar / reabrir una tarea**
```python
call("closeTask", {"task_id": task_id})
call("openTask", {"task_id": task_id})
```

**Listar tus proyectos**
```python
proyectos = call("getMyProjects", {})
```

**Listar todas las tareas de un proyecto** (de un saque, sin ir tarea por tarea)
```python
tareas = call("getAllTasks", {"project_id": 1, "status_id": 1})  # status_id: 1=abiertas, 0=cerradas
```

**Ver los miembros/accesos de un proyecto**
```python
miembros = call("getProjectUsers", {"project_id": 1})
```

**Listar las categorías de un proyecto**
```python
categorias = call("getAllCategories", {"project_id": 1})
```

**Crear una categoría**
```python
cat_id = call("createCategory", {"project_id": 1, "name": "Nombre de la categoría"})
```

## Advertencias (ya las pisamos, evitalas)

| Problema | Causa | Solución |
|---|---|---|
| `createTask` devuelve `False` sin error visible | Pasar `date_started`/`date_due` como timestamp numérico | Omitir esos campos; usar `time_spent` en su lugar |
| La tarea cambia de descripción pero sigue en la misma columna | `updateTask` no mueve de columna | Usar `moveTaskPosition` por separado |
| Un reporte queda sin los avances reales cargados en comentarios | `getTask` no trae comentarios | Llamar siempre también `getAllComments` |

## Cómo pedírselo a Claude Code

Con este archivo como `CLAUDE.md` del proyecto (o linkeado desde el tuyo), alcanza con pedir cosas
como:

- "Creá una tarea en el proyecto 1 con título X, asignada a mí"
- "Traeme todas las tareas del proyecto 3 con sus comentarios y armame un resumen"
- "Mové la tarea 42 a la columna 'Hecho'"

Claude va a usar el patrón de este archivo sin necesidad de que se lo expliques de nuevo.
