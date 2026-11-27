"""Convierte la respuesta de texto de un comando MML Huawei en un diccionario.

Formato de entrada (ejemplo recortado de LST SUB en el UDM):

    +++    USCDB        2026-11-27 11:59:38
    PGW    #000002
    %%  LST SUB: ISDN="595...";%%
    RETCODE = 0 SUCCESS0001:Operation is successful

                              IMSI = ...
    "Basic Service"
                        Telephony (TS11)
                       DefaultCall = Telephony (TS11)
    "EPS Data"
                            CNTXID = 1
                          APNTPLID = 1
                            CNTXID = 2
                          APNTPLID = 0

    Total count = 50
    There is together 1 report
    ---    END

Reglas de conversión:
  - Los "clave = valor" antes de la primera sección van a 'datos'.
  - Cada línea entre comillas abre una sección.
  - Las líneas sin '=' dentro de una sección son ítems de una lista ('items').
  - Si una clave se repite dentro de la sección, empieza un grupo nuevo y los
    grupos se juntan en una lista ('grupos'). Las claves que no son del grupo
    quedan sueltas en la sección.
  - Una sección que solo tiene ítems queda como lista; una que solo tiene
    grupos queda como lista de grupos; una sección vacía queda como True.
  - Todos los valores quedan como texto (el IMSI y el ISDN no son números).
"""

import re

CABECERA = re.compile(r"^\+\+\+\s+(\S+)\s+(.*\S)\s*$")
COMANDO = re.compile(r"^%%\s*(.*?)\s*%%\s*$")
RETCODE = re.compile(r"^RETCODE\s*=\s*(\d+)\s*(.*)$")
SECCION = re.compile(r'^"(.+)"$')
CLAVE_VALOR = re.compile(r"^(.+?)\s+=\s+(.*)$")
TOTAL = re.compile(r"^Total count\s*=\s*(\d+)")
FIN = re.compile(r"^(---\s+END|There is together)")


class _Seccion:
    def __init__(self):
        self.valores = {}
        self.items = []
        self.grupos = None
        self._grupo_actual = None
        self._clave_grupo = None
        self._claves_grupo = set()
        self._cortado = False  # hubo una línea en blanco después del último grupo

    def blanco(self):
        if self.grupos is not None:
            self._cortado = True

    def item(self, texto):
        self.items.append(texto)

    def clave_valor(self, clave, valor):
        if self.grupos is not None and clave == self._clave_grupo:
            self._grupo_actual = {clave: valor}
            self.grupos.append(self._grupo_actual)
            self._cortado = False
        elif (self.grupos is not None and not self._cortado
              and clave in self._claves_grupo and clave not in self._grupo_actual):
            self._grupo_actual[clave] = valor
        elif self.grupos is None and clave in self.valores:
            # Primera repetición: lo que vino desde la primera aparición de la
            # clave pasa a ser el primer grupo.
            claves = list(self.valores)
            primero = {k: self.valores.pop(k) for k in claves[claves.index(clave):]}
            self.grupos = [primero]
            self._clave_grupo = clave
            self._claves_grupo = set(primero)
            self._grupo_actual = {clave: valor}
            self.grupos.append(self._grupo_actual)
        else:
            self.valores[clave] = valor

    def resultado(self):
        if not self.valores and not self.items and not self.grupos:
            return True
        if self.items and not self.valores and not self.grupos:
            return self.items
        if self.grupos and not self.valores and not self.items:
            return self.grupos
        salida = dict(self.valores)
        if self.items:
            salida["items"] = self.items
        if self.grupos:
            salida["grupos"] = self.grupos
        return salida


def parsear(texto):
    """Devuelve un diccionario con equipo, fecha, comando, retcode, ok,
    mensaje, total y datos. Si no hay RETCODE, ok es False."""
    salida = {"equipo": None, "fecha": None, "comando": None,
              "retcode": None, "ok": False, "mensaje": None,
              "total": None, "datos": {}}
    raiz = _Seccion()
    secciones = {}
    actual = raiz
    en_cuerpo = False

    for linea in texto.splitlines():
        limpia = linea.strip()

        if not en_cuerpo:
            if m := CABECERA.match(limpia):
                salida["equipo"], salida["fecha"] = m.group(1), m.group(2)
            elif m := COMANDO.match(limpia):
                salida["comando"] = m.group(1)
            elif m := RETCODE.match(limpia):
                salida["retcode"] = int(m.group(1))
                salida["mensaje"] = m.group(2).strip()
                salida["ok"] = salida["retcode"] == 0
                en_cuerpo = True
            continue

        if FIN.match(limpia):
            break
        if m := TOTAL.match(limpia):
            salida["total"] = int(m.group(1))
            continue
        if not limpia:
            actual.blanco()
            continue
        if m := SECCION.match(limpia):
            nombre = m.group(1)
            actual = secciones.setdefault(nombre, _Seccion())
            continue
        if m := CLAVE_VALOR.match(limpia):
            actual.clave_valor(m.group(1).strip(), m.group(2).strip())
        else:
            actual.item(limpia)

    datos = raiz.resultado()
    datos = dict(datos) if isinstance(datos, dict) else ({} if datos is True else {"items": datos})
    for nombre, seccion in secciones.items():
        datos[nombre] = seccion.resultado()
    salida["datos"] = datos
    return salida
