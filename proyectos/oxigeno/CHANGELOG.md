# CHANGELOG — Oxígeno

## [0.1.0] — 2026-11-27

### Agregado
- `mml.py`: cliente MML con login, logout y lectura hasta `---    END`. Solo acepta comandos `LST`, `DSP` y `GET`.
- `respuesta.py`: convierte la respuesta MML en un diccionario. Maneja secciones, ítems, grupos repetidos y errores.
- `consulta.py`: consulta por consola a UDM y UPCF, con salida JSON o cruda. Las credenciales van por variables de entorno o se piden por teclado.
- 14 pruebas sin red real: parser, validación de números y cliente contra un equipo simulado.

### Verificado en el equipo real (a mano, desde `fdo-oss1`)
- Login del usuario `lared` en el UDM `10.148.48.88`: `RETCODE = 0`.
- `LST SUB` de una línea: su respuesta, con los datos reemplazados, es la que usan las pruebas.
