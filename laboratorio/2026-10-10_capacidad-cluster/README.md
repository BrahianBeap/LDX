# Capacidad real del cluster, 3 sitios (2026-10-10)

## Objetivo

Antes de empezar a migrar otros sistemas al cluster, saber con precisión cuánta CPU, RAM y disco queda libre en cada sitio, y qué está corriendo hoy en cada uno (con su consumo real y su stack) — para elegir dónde alojar cada sistema nuevo con datos, no a ojo.

## Resultado

✅ Verificado en vivo contra los 3 miembros del cluster (`pfr.1`, `car.1`, `fdo.1`), desde una sola sesión SSH a `pfr-oss` — LXD enruta las consultas al servidor correcto sin necesidad de entrar a cada sitio por separado (ver el procedimiento reutilizable en [06_Operacion.md — Verificar la capacidad disponible del cluster](../../docs/06_Operacion.md#verificar-la-capacidad-disponible-del-cluster-cpu-ram-disco)).

| Sitio | CPU | RAM libre | Disco libre (pool ZFS) |
|---|---|---|---|
| Franco (`pfr.1`) | 12 hilos | 8.20 GiB de 16.00 GiB | 310.3 GiB de 315.9 GiB |
| Carpinelli (`car.1`) | 4 hilos | 4.68 GiB de 8.00 GiB | 376.0 GiB de 381.9 GiB |
| Fernando (`fdo.1`) | 4 hilos | 3.96 GiB de 8.00 GiB | 377.8 GiB de 381.7 GiB |

Reporte visual armado con estos datos: [Cuánto sobra en cada sitio, hoy](https://claude.ai/code/artifact/3ba1069b-65fe-4fad-a37f-ce40e53b4d46) (privado, solo accesible desde la cuenta del usuario).

## Hallazgos para la planificación

- **El disco no es una restricción en ningún sitio** — los 3 tienen entre 310 y 378 GiB libres. Carpinelli y Fernando tienen incluso más libre que Franco, que ya aloja los contenedores más pesados en disco (VulnApp NG, 20 GiB cada uno).
- **Franco tiene el triple de CPU** que Carpinelli o Fernando (12 hilos contra 4) — para un sistema nuevo con más carga de procesamiento, es el sitio con más margen real, aunque también el que más contenedores ya aloja.
- **RAM es el recurso más parejo entre sitios**, ninguno en estado crítico todavía: Fernando (50.5% usado) y Franco (48.8%) están a mitad de camino; Carpinelli (41.5%) es el que más aire tiene.
- 🟡 **3 contenedores ya mostraron uso de swap** dentro de su límite de 1 GiB (`CAR-GW-OAM`, `FDO-GW-SRV`, `FDO-WS-1`) — no es un problema activo, pero es señal de que ese límite les queda justo. Antes de sumarles más carga al mismo sitio, conviene subirles el techo.
- 🔴 Kanboard (`PFR-KANBOARD-TEST`) sigue siendo el único contenedor sin `limits.memory` — ya registrado como pendiente en su ficha de [03_Componentes.md](../../docs/03_Componentes.md#kanboard-gestión-de-tareas).

Detalle completo, comando por comando, en [`bitacora.md`](bitacora.md).
