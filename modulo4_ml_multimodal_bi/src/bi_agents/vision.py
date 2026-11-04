"""Gemini Vision aplicado a dashboards. Offline devuelve un análisis determinista de la serie."""
from shared.config import MODEL_NAME, is_cloud


def analizar_grafica(png: bytes, pregunta: str, serie: list[float] | None = None) -> str:
    if is_cloud():
        from google import genai  # VERIFICAR: google-genai
        from google.genai import types
        client = genai.Client()
        res = client.models.generate_content(
            model=MODEL_NAME,
            contents=[types.Part.from_bytes(data=png, mime_type="image/png"),
                      f"Eres analista BI. Describe tendencia, picos y anomalías visibles. {pregunta}"])
        return res.text
    if serie:
        ultimo, prev = serie[-1], serie[-2] if len(serie) > 1 else serie[-1]
        cambio = (ultimo - prev) / prev * 100
        return f"[stub] Barras: último mes {ultimo:,.0f} vs {prev:,.0f} ({cambio:+.1f}%). Tendencia {'al alza' if sum(serie[-3:]) > sum(serie[:3]) else 'a la baja'}."
    return "[stub] sin serie para describir"
