"""Consulta de solo lectura a los equipos Huawei de Oxígeno, con salida en JSON.

Ejemplos:
    python3 -m oxigeno.consulta --equipo udm-car --msisdn 981123456
    python3 -m oxigeno.consulta --equipo udm-car --msisdn 981123456 --consulta dynsub
    python3 -m oxigeno.consulta --equipo upcf-car --msisdn 981123456 --consulta psrv --crudo

Credenciales (nunca en el código ni en git):
    OXI_USUARIO          usuario MML (por defecto: lared)
    OXI_PASS_UDM         contraseña para los UDM
    OXI_PASS_UPCF        contraseña para los UPCF
Si la variable no está, la contraseña se pide por teclado sin mostrarla.
"""

import argparse
import getpass
import json
import os
import re
import sys

from .mml import MmlClient, MmlError
from .respuesta import parsear

EQUIPOS = {
    "udm-car":  {"host": "10.148.48.88", "tipo": "udm"},
    "udm-fra":  {"host": "10.148.37.88", "tipo": "udm"},
    "upcf-car": {"host": "10.148.50.89", "tipo": "upcf"},
    "upcf-fra": {"host": "10.148.39.89", "tipo": "upcf"},
}

# Plantillas tomadas del backend viejo (hss.py y upcc.py). Todas son de lectura.
CONSULTAS = {
    "udm": {
        "sub":    'LST SUB: ISDN="{isdn}";',
        "dynsub": 'LST DYNSUB: ISDN="{isdn}", CONTENT=ALL;',
    },
    "upcf": {
        "psrv":   'LST PSRV: USRIDENTIFIER="{isdn}";',
        "pquota": 'LST PQUOTA: USRIDENTIFIER="{isdn}", REALTIMEFLAG=True;',
    },
}
CONSULTA_DEFECTO = {"udm": "sub", "upcf": "psrv"}


def normalizar_msisdn(texto):
    """Acepta 0981123456, 981123456, 595981123456 o +595 981 123 456 y
    devuelve 595981123456. Rechaza cualquier otra cosa, incluso un número
    válido con caracteres de más (no los limpia en silencio)."""
    if not re.fullmatch(r"\+?[\d\s\-()]+", texto or ""):
        raise ValueError(f"Número no válido: {texto!r} (solo dígitos, espacios, + y -)")
    digitos = re.sub(r"\D", "", texto)
    if digitos.startswith("595"):
        digitos = digitos[3:]
    digitos = digitos.lstrip("0")
    if not re.fullmatch(r"9\d{8}", digitos):
        raise ValueError(f"Número no válido: {texto!r} (se esperan 9 dígitos que empiecen con 9)")
    return "595" + digitos


def obtener_password(tipo):
    variable = f"OXI_PASS_{tipo.upper()}"
    valor = os.environ.get(variable)
    if valor:
        return valor
    return getpass.getpass(f"Contraseña MML para {tipo.upper()} ({variable} no está definida): ")


def main(argv=None):
    p = argparse.ArgumentParser(description="Consulta de solo lectura a UDM/UPCF Huawei, salida JSON")
    p.add_argument("--equipo", required=True, choices=sorted(EQUIPOS))
    p.add_argument("--msisdn", required=True, help="Número de línea, ej. 981123456")
    p.add_argument("--consulta", help="Tipo de consulta. UDM: sub, dynsub. UPCF: psrv, pquota")
    p.add_argument("--crudo", action="store_true", help="Imprime la respuesta del equipo sin convertir")
    p.add_argument("--timeout", type=float, default=15.0)
    args = p.parse_args(argv)

    equipo = EQUIPOS[args.equipo]
    tipo = equipo["tipo"]
    consulta = args.consulta or CONSULTA_DEFECTO[tipo]
    if consulta not in CONSULTAS[tipo]:
        p.error(f"La consulta '{consulta}' no existe para {tipo.upper()}. Opciones: {', '.join(CONSULTAS[tipo])}")

    try:
        isdn = normalizar_msisdn(args.msisdn)
    except ValueError as e:
        p.error(str(e))

    usuario = os.environ.get("OXI_USUARIO", "lared")
    password = obtener_password(tipo)
    comando = CONSULTAS[tipo][consulta].format(isdn=isdn)

    try:
        with MmlClient(equipo["host"], timeout=args.timeout) as cliente:
            cliente.login(usuario, password)
            texto = cliente.consultar(comando)
    except MmlError as e:
        print(json.dumps({"ok": False, "error": str(e), "retcode": e.retcode},
                         ensure_ascii=False, indent=2))
        return 1

    if args.crudo:
        print(texto)
        return 0
    resultado = parsear(texto)
    resultado["consulta"] = {"equipo": args.equipo, "host": equipo["host"], "tipo": consulta}
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
    return 0 if resultado["ok"] else 2


if __name__ == "__main__":
    sys.exit(main())
