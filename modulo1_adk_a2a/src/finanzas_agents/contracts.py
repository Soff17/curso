"""Contratos estrictos entre agentes (interfaces A2A) con Pydantic."""
import unicodedata
from typing import Literal, Optional
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator

Trimestre = str  # formato AAAA-Qn
CATEGORIAS = ("Viaticos", "Consultoria", "Tecnologia", "Marketing", "Servicios")


class BudgetRequest(BaseModel):
    division: Literal["Norte", "Sur", "Centro", "Occidente"]
    trimestre: str = Field(pattern=r"^\d{4}-Q[1-4]$")
    categoria: Optional[str] = None

    @field_validator("categoria")
    @classmethod
    def _normaliza(cls, v):
        """Un LLM escribirá 'Tecnología' o 'viáticos'; la BD guarda 'Tecnologia', 'Viaticos'."""
        if not v:
            return v
        limpia = "".join(c for c in unicodedata.normalize("NFKD", v.strip()) if not unicodedata.combining(c))
        limpia = limpia.capitalize()
        if limpia not in CATEGORIAS:
            raise ValueError(f"Categoría inválida '{v}'. Válidas: {', '.join(CATEGORIAS)}")
        return limpia


class BudgetLine(BaseModel):
    categoria: str
    presupuestado: float
    ejecutado: float

    @property
    def desviacion_pct(self) -> float:
        return round((self.ejecutado - self.presupuestado) / self.presupuestado * 100, 2)


class BudgetResponse(BaseModel):
    division: str
    trimestre: str
    lineas: list[BudgetLine]
    total_presupuestado: float
    total_ejecutado: float
    desviacion_pct: float


class A2AEnvelope(BaseModel):
    """Mensaje inter-agente: identifica emisor/receptor y propaga el contexto de sesión."""
    message_id: str = Field(default_factory=lambda: uuid4().hex)
    session_id: str
    sender: str
    receiver: str
    intent: str
    payload: dict
    context: dict = Field(default_factory=dict)  # historial/estado compartido
