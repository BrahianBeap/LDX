# Oxígeno: consultas a UDM/UPCF Huawei con salida JSON

> **Fecha de inicio:** 2026-11-27
> **Estado:** 🟡 v0.1.0, prototipo de consola. Probado contra un equipo simulado y contra una respuesta real guardada (con los datos del abonado reemplazados). Probado contra el UDM real (`udm-car`, `LST SUB`) desde `fdo-oss1`.

## Objetivo

Reemplazar el backend viejo de Oxígeno (Python 2, de Néstor Cardozo) por una librería en Python 3 que consulta los equipos Huawei por **MML** y devuelve **JSON**. Sobre esa librería se van a montar después la API y la web.

✅ El HSS se migra al **UDM** y el UPCC al **UPCF** (confirmado por Néstor Cardozo el 2026-11-27). El código viejo apunta a las IP anteriores (`192.168.201.x`, `192.168.202.20`). Este prototipo usa las nuevas.

## Qué es MML

MML es el protocolo de texto de los equipos Huawei:
1. Se abre un TCP al puerto 7776.
2. Se manda `LGI` (login).
3. Se mandan comandos terminados en `;`.
4. Se cierra con `LGO`.

Cada respuesta termina en una línea `---    END` y trae un `RETCODE`: `0` es éxito, cualquier otro valor es error.

```
LGI: HLRSN=1, OPNAME="lared", PWD="...";      ← login (en el UDM lleva HLRSN=1)
LST SUB: ISDN="595981123456";                 ← consulta
LGO:;                                         ← logout
```

## Equipos

| Nombre | Equipo | IP:puerto |
|---|---|---|
| `udm-car` | UDM master (CAR) | `10.148.48.88:7776` |
| `udm-fra` | UDM redundancia (FRA) | `10.148.37.88:7776` |
| `upcf-car` | UPCF master (CAR) | `10.148.50.89:7776` |
| `upcf-fra` | UPCF redundancia (FRA) | `10.148.39.89:7776` |

Desde el cluster, solo se llega a estos equipos por la red de gestión de Fernando. Desde un contenedor de `OVN_1` hacen falta dos cosas: una regla en `ACL-OVN-1` y rutas vía `FDO-GW-OAM`. Ver la [bitácora de alcance](../../laboratorio/2026-11-27_alcance-oxigeno-huawei/README.md).

## Uso

Requiere Python 3.8 o superior. No usa librerías externas.

```bash
cd src
export OXI_PASS_UDM      # opcional: si no está, la pide por teclado
python3 -m oxigeno.consulta --equipo udm-car --msisdn 981123456
python3 -m oxigeno.consulta --equipo udm-car --msisdn 981123456 --consulta dynsub
python3 -m oxigeno.consulta --equipo upcf-car --msisdn 981123456 --consulta psrv
python3 -m oxigeno.consulta --equipo udm-car --msisdn 981123456 --crudo   # respuesta sin convertir
```

| Opción | Descripción |
|---|---|
| `--equipo` | `udm-car`, `udm-fra`, `upcf-car` o `upcf-fra` |
| `--msisdn` | Número de línea: `981123456`, `0981123456`, `595981123456` o `+595 981 123 456`. Se rechaza si trae otros caracteres |
| `--consulta` | UDM: `sub` (por defecto) o `dynsub`. UPCF: `psrv` (por defecto) o `pquota`. Las plantillas salen del código viejo |
| `--crudo` | Imprime la respuesta del equipo tal cual, para ver campos nuevos o depurar el parser |
| `--timeout` | Segundos de espera por respuesta. Por defecto 15 |

**Código de salida:** `0` si la consulta dio OK, `1` si hubo un error de conexión o de login, `2` si el equipo respondió con un `RETCODE` distinto de 0.

### Variables de entorno

| Variable | Uso | Por defecto |
|---|---|---|
| `OXI_USUARIO` | Usuario MML | `lared` |
| `OXI_PASS_UDM` | Contraseña para los UDM | Se pide por teclado |
| `OXI_PASS_UPCF` | Contraseña para los UPCF | Se pide por teclado |

## Formato del JSON

```json
{
  "equipo": "USCDB", "fecha": "2026-11-27 11:59:38",
  "comando": "LST SUB: ISDN=\"595900000000\";",
  "retcode": 0, "ok": true, "mensaje": "SUCCESS0001:Operation is successful", "total": 50,
  "datos": {
    "IMSI": "744050000000000", "CardType": "USIM",
    "SABLOCK": true,
    "Basic Service": { "DefaultCall": "Telephony (TS11)", "items": ["Telephony (TS11)", "..."] },
    "ODB Data": { "ODBOC": "BOIC", "ODBROAM": "BROHPLMNC" },
    "GPRS Data": [ { "CNTXID": "1", "APNTPLID": "1" }, { "CNTXID": "2", "APNTPLID": "0" } ],
    "EPS Data": { "SMDP": "MSC", "RROption": "ALL_PLMNS", "grupos": [ { "CNTXID": "1", "APNTPLID": "1" } ] }
  },
  "consulta": { "equipo": "udm-car", "host": "10.148.48.88", "tipo": "sub" }
}
```

Reglas de conversión, implementadas en [`respuesta.py`](src/oxigeno/respuesta.py):
- Las líneas `"Nombre"` abren una sección.
- Las líneas sin `=` van a `items`.
- Si una clave se repite dentro de una sección, se arma una lista de `grupos`.
- Una sección que solo tiene ítems, o solo grupos, queda como lista. Una sección vacía queda como `true`.
- **Todos los valores quedan como texto**, porque el IMSI y el ISDN no son números.

## Seguridad

- **Solo lectura.** [`mml.py`](src/oxigeno/mml.py) rechaza todo comando que no sea `LST`, `DSP` o `GET` antes de mandarlo. El código viejo tenía funciones que modifican la red, y **a propósito no se migraron**:
  - `SND CANCELC`: desregistra la línea.
  - `ADD/RMV PSUB` y `ADD PSRV`: suscripciones y servicios en el PCRF.
  - `deactive pdpcontext`: corta la sesión de datos.
- **Sin credenciales en el código ni en git.** Van por variables de entorno o por teclado. Si el login falla, la contraseña no aparece en el error.
- **El número se valida antes de armar el comando**, para que no se pueda inyectar MML por `--msisdn`.
- 🔴 **Las credenciales del código viejo circularon en un `.rar` por Teams.** Hay que rotarlas antes de pasar a producción.
- 🔴 **El backend viejo expone `getLbs.py` en `10.150.31.80:8080` sin autenticación.** Devuelve la localización y el IMSI de cualquier línea. El reemplazo tiene que quedar detrás del login de la web.

## Pruebas

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

Son 16 pruebas, todas sin red real:
- El parser, contra las respuestas guardadas de `LST SUB` y `LST DYNSUB` (con IMSI y número reemplazados), un error de login y un abonado inexistente en el UPCF.
- La validación de números.
- El cliente contra un equipo MML simulado en `localhost`: login, lectura por partes, logout, login rechazado sin mostrar la contraseña y rechazo de comandos de escritura.

## Pendientes

- [x] Probar `consulta.py` contra el UDM real desde `fdo-oss1` (2026-11-27: `LST SUB` OK, JSON correcto).
- [x] Probar el login en el UPCF (2026-11-27: el mismo `LGI` con `HLRSN=1` funciona; el equipo también se identifica como `USCDB`).
- [ ] 🔴 `LST PSRV` en el UPCF devolvió `RETCODE = 12302 The subscriber does not exist` para una línea que sí existe en el UDM. Falta saber si la línea no tiene política PCC o si el UPCF espera otro formato de `USRIDENTIFIER` (sin `595`, o el IMSI). Consultar a Néstor.
- [ ] Confirmar con Néstor si siguen en uso el MNP y el MSC (puerto 6000), que no figuran en la lista de equipos nuevos.
- [x] `LST DYNSUB` real: trae claves largas partidas en dos líneas; el parser ya las une.
- [ ] Juntar respuestas reales exitosas de `LST PSRV` y `LST PQUOTA` para ajustar el parser.
- [ ] Contenedor en `fdo.1`, con regla en ACL y rutas (ver la bitácora de alcance).
- [ ] API y web.
