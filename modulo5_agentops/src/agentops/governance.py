"""Gobernanza: enmascaramiento de PII (DLP), trazabilidad y costo por tokens."""
import re
import time
from contextlib import contextmanager
from dataclasses import dataclass, field

from shared.config import is_cloud

# --- DLP ---
_PATTERNS = {
    "EMAIL": re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"),
    "TARJETA": re.compile(r"\b(?:\d[ -]?){13,16}\b"),
    "CUENTA_CLABE": re.compile(r"\b\d{18}\b"),
    "TELEFONO": re.compile(r"\b(?:\+?\d{1,3}[ -]?)?\(?\d{2,3}\)?[ -]?\d{3,4}[ -]?\d{4}\b"),
}


def mask_pii(text: str) -> str:
    """Offline: regex. Cloud: Cloud DLP `deidentify_content` con infoTypes (usar `dlp_mask`)."""
    if is_cloud():
        return dlp_mask(text)
    # Orden: más específicos primero para no enmascarar CLABE como teléfono.
    for name in ("EMAIL", "CUENTA_CLABE", "TARJETA", "TELEFONO"):
        text = _PATTERNS[name].sub(f"[{name}]", text)
    return text


def dlp_mask(text: str, project: str | None = None) -> str:
    import os
    from google.cloud import dlp_v2  # VERIFICAR
    client = dlp_v2.DlpServiceClient()
    parent = f"projects/{project or os.environ['GOOGLE_CLOUD_PROJECT']}/locations/global"
    info = [{"name": n} for n in ("EMAIL_ADDRESS", "CREDIT_CARD_NUMBER", "PHONE_NUMBER", "IBAN_CODE")]
    cfg = {"info_type_transformations": {"transformations": [
        {"primitive_transformation": {"replace_with_info_type_config": {}}}]}}
    res = client.deidentify_content(request={
        "parent": parent, "deidentify_config": {"info_type_transformations": cfg["info_type_transformations"]},
        "inspect_config": {"info_types": info}, "item": {"value": text}})
    return res.item.value


# --- Trazabilidad / costos ---
@dataclass
class Span:
    name: str
    start: float
    end: float = 0.0
    attrs: dict = field(default_factory=dict)

    @property
    def ms(self) -> float:
        return round((self.end - self.start) * 1000, 2)


class Tracer:
    """Mini-tracer didáctico. En cloud se sustituye por OpenTelemetry -> Cloud Trace
    (ADK ya emite spans OTel; configurar el exporter de Cloud Trace)."""

    def __init__(self):
        self.spans: list[Span] = []

    @contextmanager
    def span(self, name: str, **attrs):
        s = Span(name, time.perf_counter(), attrs=attrs)
        try:
            yield s
        finally:
            s.end = time.perf_counter()
            self.spans.append(s)

    def a2a_hops(self) -> list[tuple[str, str]]:
        return [(s.attrs["from"], s.attrs["to"]) for s in self.spans if s.name == "a2a.delegate"]


# Precios por 1M tokens: PARÁMETROS DE EJEMPLO; actualizar con la tarifa vigente de Vertex AI.
PRICE_PER_M = {"input": 0.30, "output": 2.50}


def token_cost(input_tokens: int, output_tokens: int, price=PRICE_PER_M) -> float:
    return round(input_tokens / 1e6 * price["input"] + output_tokens / 1e6 * price["output"], 6)


def audit_record(agent: str, user_input: str, answer: str, citations: list[str]) -> dict:
    """Registro de auditoría listo para Cloud Logging (estructurado, con PII enmascarada)."""
    return {"agent": agent, "input": mask_pii(user_input), "answer": mask_pii(answer), "citations": citations}
