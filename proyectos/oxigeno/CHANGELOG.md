# CHANGELOG — Oxígeno

## [0.1.1] — 2026-11-27

### Corregido
- `respuesta.py`: une las claves largas que el equipo parte en dos líneas (la clave en una línea y `= valor` en la siguiente), como en `LST DYNSUB`. Antes quedaban como ítems sueltos.

### Agregado
- Fixtures reales con datos reemplazados: `LST DYNSUB` del UDM y `LST PSRV` del UPCF con `RETCODE = 12302`. Ahora son 16 pruebas.

### Verificado en el equipo real
- Login `lared` en el UPCF `10.148.50.89`: OK con el mismo `LGI` que el UDM.
- `LST DYNSUB` en el UDM: OK.
- 🔴 `LST PSRV` en el UPCF: `12302 The subscriber does not exist` para una línea que existe en el UDM. Pendiente de aclarar con Néstor.

## [0.1.0] — 2026-11-27

### Agregado
- `mml.py`: cliente MML con login, logout y lectura hasta `---    END`. Solo acepta comandos `LST`, `DSP` y `GET`.
- `respuesta.py`: convierte la respuesta MML en un diccionario. Maneja secciones, ítems, grupos repetidos y errores.
- `consulta.py`: consulta por consola a UDM y UPCF, con salida JSON o cruda. Las credenciales van por variables de entorno o se piden por teclado.
- 14 pruebas sin red real: parser, validación de números y cliente contra un equipo simulado.

### Verificado en el equipo real (a mano, desde `fdo-oss1`)
- Login del usuario `lared` en el UDM `10.148.48.88`: `RETCODE = 0`.
- `LST SUB` de una línea: su respuesta, con los datos reemplazados, es la que usan las pruebas.
- `consulta.py --equipo udm-car`: login, consulta, JSON y logout OK contra el UDM real.
