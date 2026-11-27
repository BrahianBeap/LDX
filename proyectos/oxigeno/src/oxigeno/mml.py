"""Cliente MML para equipos Huawei (UDM/USCDB, UPCF) sobre TCP.

El protocolo es texto plano: se abre un socket TCP, se manda un comando
terminado en ';' y el equipo responde un bloque que termina en una línea
'---    END'. La sesión empieza con LGI (login) y termina con LGO (logout).

Este cliente solo permite comandos de lectura (LST, DSP, GET). Cualquier otro
comando se rechaza antes de llegar al equipo, porque varios comandos MML
modifican abonados reales (ADD, RMV, MOD, SND, ...).
"""

import re
import socket

PUERTO_MML = 7776
FIN_RESPUESTA = re.compile(rb"^---\s+END\s*$", re.MULTILINE)
RETCODE = re.compile(r"RETCODE\s*=\s*(\d+)\s*(.*)")
COMANDO_LECTURA = re.compile(r"^\s*(LST|DSP|GET)\s+[A-Z0-9]+\s*:", re.IGNORECASE)


class MmlError(Exception):
    """Error de conexión, de login o de protocolo con el equipo."""

    def __init__(self, mensaje, retcode=None):
        super().__init__(mensaje)
        self.retcode = retcode


class MmlClient:
    """Sesión MML contra un equipo.

    Uso:
        with MmlClient("10.148.48.88") as c:
            c.login("lared", password)
            texto = c.consultar('LST SUB: ISDN="595981000000";')
    """

    def __init__(self, host, port=PUERTO_MML, timeout=15.0):
        self.host = host
        self.port = port
        self.timeout = timeout
        self._sock = None
        self._logueado = False

    # -- conexión -----------------------------------------------------------

    def conectar(self):
        try:
            self._sock = socket.create_connection((self.host, self.port), timeout=self.timeout)
        except OSError as e:
            raise MmlError(f"No se pudo conectar a {self.host}:{self.port}: {e}") from e

    def cerrar(self):
        if self._sock is None:
            return
        try:
            if self._logueado:
                self._enviar("LGO:;")
        except MmlError:
            pass
        finally:
            self._sock.close()
            self._sock = None
            self._logueado = False

    def __enter__(self):
        self.conectar()
        return self

    def __exit__(self, *exc):
        self.cerrar()

    # -- protocolo ------------------------------------------------------------

    def _enviar(self, comando):
        """Manda un comando y devuelve la respuesta completa como texto."""
        if self._sock is None:
            raise MmlError("No hay conexión abierta")
        try:
            self._sock.sendall(comando.encode("ascii") + b"\r\n")
            buffer = b""
            while not FIN_RESPUESTA.search(buffer):
                parte = self._sock.recv(4096)
                if not parte:
                    raise MmlError("El equipo cerró la conexión antes de terminar la respuesta")
                buffer += parte
        except socket.timeout as e:
            raise MmlError(f"Sin respuesta completa del equipo en {self.timeout} s") from e
        except OSError as e:
            raise MmlError(f"Error de red: {e}") from e
        return buffer.decode("utf-8", errors="replace")

    def login(self, usuario, password, extra="HLRSN=1"):
        """Hace LGI. 'extra' es el parámetro que pide el equipo antes de OPNAME
        (en el UDM/USCDB es HLRSN=1). La contraseña nunca se incluye en errores."""
        if '"' in usuario or '"' in password or ";" in password:
            raise MmlError("El usuario o la contraseña tienen caracteres no admitidos (\" o ;)")
        prefijo = f"{extra}, " if extra else ""
        respuesta = self._enviar(f'LGI: {prefijo}OPNAME="{usuario}", PWD="{password}";')
        m = RETCODE.search(respuesta)
        if not m:
            raise MmlError("Respuesta de login sin RETCODE")
        if m.group(1) != "0":
            raise MmlError(f"Login rechazado: RETCODE = {m.group(1)} {m.group(2).strip()}", int(m.group(1)))
        self._logueado = True

    def consultar(self, comando):
        """Manda un comando de solo lectura y devuelve la respuesta cruda."""
        if not COMANDO_LECTURA.match(comando):
            raise MmlError(f"Comando no permitido (solo LST, DSP o GET): {comando.split(':')[0]}")
        if not self._logueado:
            raise MmlError("Hay que hacer login antes de consultar")
        return self._enviar(comando)
