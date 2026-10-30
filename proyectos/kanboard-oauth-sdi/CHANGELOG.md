# CHANGELOG — plugin "OAuth2" (ingreso con AD)

## 1.0.1 — 2026-10-30

- Corrige el retorno de SDI: SDI agrega `?code=` a la URL registrada aunque ya tenga `?`, y Kanboard respondía "Action not implemented". `Plugin::fixSdiCallbackUrl()` separa el código antes de `Router::dispatch()`. Ver TRB-023 en `docs/07_Troubleshooting.md`.

## 1.0.0 — 2026-10-30

- Botón "Ingresar con usuario de AD" en el login, sin quitar el login local.
- Canje del código por el token con el formato de SDI (JSON, respuesta dentro de `data`), copiado de ADM-TECH.
- Vinculación por `mail` (`nombre.apellido@personal.com.py` → `username`). No crea usuarios.
- Validación del `state`, que tolera que SDI no lo devuelva.
