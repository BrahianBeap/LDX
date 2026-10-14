# Consumo para planilla

GiB, dos decimales. Carpetas reutilizadas del 16/09/2026 09:25–09:28 -0300; bases y desglose complementario del mismo día 09:58–09:59 -0300. Totales **parciales del alcance medido y atribuido**: logs externos sin acceso y repositorios sin atribución quedan fuera de los totales por aplicación. No es una fotografía simultánea ni un promedio histórico.

| Aplicación | Código/carpetas | Adjuntos incluidos | Base principal | Respaldo BD | Total operativo | Total con respaldos | Observaciones |
|---|---:|---:|---:|---:|---:|---:|---|
| Infrawork | 38.24 | N/D | 1.79 | 1.71 | 40.03 | 47.85 | Incluye logs 0.01 GiB y contenido mixto Ejemplos_fileinput 37.85 GiB. Total con respaldos añade 6.10 GiB de archivos y 1.71 GiB de Infra_restore. |
| ADM-TECH | 6.68 | 6.62 | 0.05 | N/D | 6.74 | 6.74 | Mapeo confirmado. Base postgres con nombre habitual de mantenimiento. Sin respaldo BD informado; copias internas ya incluidas en carpeta. |
| VulnApp | 0.44 | 0.44 | 0.11 | N/D | 0.55 | 0.55 | RAM dedicada 151.41 MiB; CPU puntual 0.0%. Sin respaldo BD informado. |
| Repositorios compartidos pendientes | 591.26 | N/D | N/D | N/D | 591.26 | 591.26 | infrafilerun; separado de las aplicaciones. |
| Backups compartidos pendientes | 0.00 | N/D | N/D | N/D | 0.00 | 0.00 | Todo backup_pg atribuido a Infrawork; no duplicar. |

«Código/carpetas» es la carpeta completa, no código puro. Adjuntos y logs internos ya están incluidos y no se suman otra vez. N/D no equivale a cero. Los respaldos no informados y logs externos desconocidos no se han estimado; los totales solo suman componentes comprobados. Las copias internas permanecen en el total operativo porque la fórmula solicitada usa la carpeta completa.

Infrawork y ADM-TECH: CPU y RAM **N/D — servicio Apache compartido**. RSS compartido reutilizado: Apache 237.90 MiB, PostgreSQL 613.95 MiB y MariaDB 227.21 MiB. No se reparte entre aplicaciones ni bases.
