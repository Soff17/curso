"""Integración con Tableau Server REST API (vía tableauserverclient) + stub offline.

Looker Studio (antes 'Data Studio') no ofrece un SDK equivalente; ver docs/00-analisis-programa.md.
"""
import os
import struct
import zlib

from shared.config import is_cloud


def _png(width: int, height: int, pixels: list[list[tuple[int, int, int]]]) -> bytes:
    raw = b"".join(b"\x00" + b"".join(bytes(p) for p in row) for row in pixels)
    def chunk(t: bytes, d: bytes) -> bytes:
        c = struct.pack(">I", len(d)) + t + d
        return c + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))


def _stub_view(values: list[float]) -> bytes:
    """Gráfica de barras sintética (suficiente para probar el pipeline de visión)."""
    w, h = 240, 120
    mx = max(values) or 1
    bw = w // len(values)
    px = [[(255, 255, 255)] * w for _ in range(h)]
    for i, v in enumerate(values):
        bh = int(v / mx * (h - 10))
        for y in range(h - bh, h):
            for x in range(i * bw + 2, (i + 1) * bw - 2):
                px[y][x] = (200, 40, 40) if i == len(values) - 1 else (40, 90, 200)
    return _png(w, h, px)


def obtener_vista_tableau(workbook: str, vista: str, division: str = "Norte") -> dict:
    """Descarga como imagen una vista de Tableau y devuelve metadatos + bytes (base64 omitido aquí).

    Args:
        workbook: nombre del libro.
        vista: nombre de la vista.
        division: filtro de división.
    """
    if not is_cloud():
        from .ml_tools import serie_gasto_mensual
        serie = serie_gasto_mensual(division)
        return {"status": "ok", "fuente": "stub", "png": _stub_view(serie), "serie": serie}
    import tableauserverclient as TSC  # VERIFICAR: versión de TSC
    auth = TSC.PersonalAccessTokenAuth(os.environ["TABLEAU_TOKEN_NAME"], os.environ["TABLEAU_TOKEN_VALUE"],
                                       os.environ.get("TABLEAU_SITE", ""))
    server = TSC.Server(os.environ["TABLEAU_SERVER_URL"], use_server_version=True)
    with server.auth.sign_in(auth):
        opts = TSC.RequestOptions()
        opts.filter.add(TSC.Filter(TSC.RequestOptions.Field.Name, TSC.RequestOptions.Operator.Equals, vista))
        views, _ = server.views.get(opts)
        if not views:
            return {"status": "error", "message": f"Vista {vista} no encontrada"}
        v = views[0]
        img_req = TSC.ImageRequestOptions(imageresolution=TSC.ImageRequestOptions.Resolution.High,
                                          maxage=1)
        img_req.vf("Division", division)
        server.views.populate_image(v, img_req)
        server.views.populate_csv(v)  # datos subyacentes
        return {"status": "ok", "fuente": "tableau", "png": v.image, "csv": b"".join(v.csv).decode("utf-8")}
