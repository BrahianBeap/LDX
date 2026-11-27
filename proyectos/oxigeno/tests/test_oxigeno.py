"""Pruebas sin red real: el parser contra respuestas guardadas (con datos de
abonado reemplazados) y el cliente contra un equipo MML simulado en localhost."""

import pathlib
import socket
import threading
import unittest

from oxigeno.consulta import normalizar_msisdn
from oxigeno.mml import MmlClient, MmlError
from oxigeno.respuesta import parsear

FIXTURES = pathlib.Path(__file__).parent / "fixtures"


class TestParser(unittest.TestCase):
    def setUp(self):
        self.r = parsear((FIXTURES / "udm_lst_sub_ok.txt").read_text())

    def test_cabecera(self):
        self.assertEqual(self.r["equipo"], "USCDB")
        self.assertEqual(self.r["comando"], 'LST SUB: ISDN="595900000000";')
        self.assertEqual(self.r["retcode"], 0)
        self.assertTrue(self.r["ok"])
        self.assertEqual(self.r["total"], 50)

    def test_campos_sueltos_quedan_como_texto(self):
        d = self.r["datos"]
        self.assertEqual(d["IMSI"], "744050000000000")
        self.assertEqual(d["CardType"], "USIM")
        self.assertEqual(d["HLRSN"], "1")

    def test_seccion_vacia(self):
        self.assertIs(self.r["datos"]["SABLOCK"], True)

    def test_seccion_mixta_items_y_clave(self):
        bs = self.r["datos"]["Basic Service"]
        self.assertEqual(bs["DefaultCall"], "Telephony (TS11)")
        self.assertEqual(len(bs["items"]), 5)
        self.assertIn("General-DataCDS  (BS30)", bs["items"])

    def test_seccion_solo_claves(self):
        self.assertEqual(self.r["datos"]["ODB Data"], {"ODBOC": "BOIC", "ODBROAM": "BROHPLMNC"})
        self.assertEqual(len(self.r["datos"]["SS Data"]), 15)

    def test_grupos_repetidos(self):
        gprs = self.r["datos"]["GPRS Data"]
        self.assertEqual(gprs, [{"CNTXID": "1", "APNTPLID": "1"}, {"CNTXID": "2", "APNTPLID": "0"}])

    def test_grupos_con_claves_sueltas_al_final(self):
        eps = self.r["datos"]["EPS Data"]
        self.assertEqual(len(eps["grupos"]), 4)
        self.assertEqual(eps["grupos"][3], {"CNTXID": "4", "APNTPLID": "98"})
        self.assertEqual(eps["SMDP"], "MSC")
        self.assertEqual(eps["RROption"], "ALL_PLMNS")

    def test_error(self):
        r = parsear((FIXTURES / "udm_lgi_error.txt").read_text())
        self.assertFalse(r["ok"])
        self.assertEqual(r["retcode"], 1013)
        self.assertEqual(r["mensaje"], "Username or password incorrect")

    def test_sin_retcode(self):
        self.assertFalse(parsear("basura")["ok"])


class TestMsisdn(unittest.TestCase):
    def test_formatos_validos(self):
        for entrada in ["981123456", "0981123456", "595981123456", "+595 981 123 456"]:
            self.assertEqual(normalizar_msisdn(entrada), "595981123456")

    def test_formatos_invalidos(self):
        for entrada in ["12345", "881123456", '981123456";RMV', ""]:
            with self.assertRaises(ValueError):
                normalizar_msisdn(entrada)


class EquipoSimulado:
    """Servidor MML mínimo: acepta un LGI con la clave 'secreta' y responde
    LST con la respuesta guardada. Registra los comandos recibidos."""

    def __init__(self):
        self.recibidos = []
        self.srv = socket.socket()
        self.srv.bind(("127.0.0.1", 0))
        self.srv.listen(1)
        self.port = self.srv.getsockname()[1]
        threading.Thread(target=self._atender, daemon=True).start()

    def _atender(self):
        conn, _ = self.srv.accept()
        buf = b""
        with conn:
            while True:
                datos = conn.recv(4096)
                if not datos:
                    return
                buf += datos
                while b"\r\n" in buf:
                    linea, buf = buf.split(b"\r\n", 1)
                    cmd = linea.decode()
                    self.recibidos.append(cmd)
                    if cmd.startswith("LGI"):
                        rc = "0 Operation is successful" if 'PWD="secreta"' in cmd else "1013 Username or password incorrect"
                        conn.sendall(f"+++    USCDB    x\r\nRETCODE = {rc}\r\n\r\n---    END\r\n".encode())
                    elif cmd.startswith("LST"):
                        # Se manda en dos partes para probar la lectura por trozos
                        resp = (FIXTURES / "udm_lst_sub_ok.txt").read_bytes().replace(b"\n", b"\r\n")
                        conn.sendall(resp[:100])
                        conn.sendall(resp[100:])
                    elif cmd.startswith("LGO"):
                        conn.sendall(b"RETCODE = 0 ok\r\n---    END\r\n")


class TestCliente(unittest.TestCase):
    def test_login_consulta_y_logout(self):
        eq = EquipoSimulado()
        with MmlClient("127.0.0.1", eq.port, timeout=5) as c:
            c.login("lared", "secreta")
            texto = c.consultar('LST SUB: ISDN="595900000000";')
        self.assertTrue(parsear(texto)["ok"])
        self.assertTrue(eq.recibidos[0].startswith('LGI: HLRSN=1, OPNAME="lared"'))
        self.assertEqual(eq.recibidos[-1], "LGO:;")

    def test_login_rechazado_sin_mostrar_la_clave(self):
        eq = EquipoSimulado()
        with MmlClient("127.0.0.1", eq.port, timeout=5) as c:
            with self.assertRaises(MmlError) as ctx:
                c.login("lared", "incorrecta")
        self.assertEqual(ctx.exception.retcode, 1013)
        self.assertNotIn("incorrecta", str(ctx.exception))

    def test_rechaza_comandos_de_escritura(self):
        c = MmlClient("127.0.0.1", 1)
        c._logueado = True
        for cmd in ['SND CANCELC: ISDN="595900000000", DEST=ALL;',
                    'RMV PSUB: USRIDENTIFIER="595900000000";',
                    'ADD PSRV: USRIDENTIFIER="595900000000";',
                    'LGI: OPNAME="x";']:
            with self.assertRaises(MmlError):
                c.consultar(cmd)


if __name__ == "__main__":
    unittest.main()
