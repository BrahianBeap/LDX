"""Genera dist/index.html a partir de src/template.html y src/apps.json.

Uso (desde esta carpeta):  python -I build.py
"""
import html
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
ESTADOS = {
    "produccion": ("En producción", "Para usar", "Listas para el trabajo diario."),
    "desarrollo": ("En desarrollo", "En pruebas", "Pueden cambiar o tener datos no oficiales."),
}


def app_html(app):
    e = html.escape
    estado = app["estado"]
    if estado not in ESTADOS:
        raise SystemExit(f"Estado desconocido en {app['nombre']}: {estado}")
    aviso = f'\n          <p class="app-aviso">{e(app["aviso"])}</p>' if app.get("aviso") else ""
    return f"""      <li class="app app--{estado}">
        <div class="app-cuerpo">
          <div class="app-titulo">
            <h3>{e(app["nombre"])}</h3>
            <span class="estado estado--{estado}"><span class="estado-marca" aria-hidden="true"></span>{ESTADOS[estado][0]}</span>
          </div>
          <p class="app-desc">{e(app["que_permite"])}</p>{aviso}
          <p class="app-ingreso"><span class="rotulo">Ingreso</span> {e(app["ingreso"])}</p>
        </div>
        <div class="app-accion">
          <a class="abrir" href="{e(app["ruta"])}" data-nombre="{e(app["nombre"])}">Abrir {e(app["nombre"])}<span class="flecha" aria-hidden="true"></span></a>
          <code class="ruta">oss.personal.com.py{e(app["ruta"])}</code>
        </div>
      </li>"""


def main():
    apps = json.loads((BASE / "src" / "apps.json").read_text(encoding="utf-8"))["apps"]
    grupos = []
    for estado, (_, titulo, nota) in ESTADOS.items():
        items = [a for a in apps if a["estado"] == estado]
        if not items:
            continue
        filas = "\n".join(app_html(a) for a in items)
        grupos.append(
            f'    <li class="grupo grupo--{estado}">\n'
            f'     <p class="grupo-titulo"><span>{titulo}</span> {nota}</p>\n'
            f'     <ol class="apps">\n{filas}\n     </ol>\n    </li>'
        )
    plantilla = (BASE / "src" / "template.html").read_text(encoding="utf-8")
    salida = plantilla.replace("<!--APPS-->", "\n".join(grupos)).replace("<!--CANTIDAD-->", str(len(apps)))
    (BASE / "dist").mkdir(exist_ok=True)
    (BASE / "dist" / "index.html").write_text(salida, encoding="utf-8", newline="\n")
    print(f"dist/index.html generado con {len(apps)} aplicaciones")


if __name__ == "__main__":
    main()
