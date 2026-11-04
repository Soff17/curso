# Rúbricas de evaluación

Escala por criterio: 0 (ausente) – 1 (parcial) – 2 (cumple) – 3 (sobresaliente).

## Módulos 1-5 (por célula)

| Criterio | Peso | M1 | M2 | M3 | M4 | M5 |
|---|---|---|---|---|---|---|
| Funciona de extremo a extremo con el caso de prueba | 30 % | A2A delega y mantiene estado | Cita exactamente 3 fragmentos | SQL correcto + contraste con RAG | Forecast + gráfica + diagnóstico | Pipeline bloquea deploy bajo umbral |
| Calidad de código (tipos, Pydantic, estructura) | 20 % | | | | | |
| Seguridad y guardrails | 20 % | Contratos estrictos | Thresholding | Read-only/LIMIT/timeout | Validación de payload ML | IAM mínimo, DLP |
| Pruebas | 15 % | tests de delegación | tests de ranking | tests de guardrails | tests con stub | tests de gate |
| Documentación / claridad en code review | 15 % | | | | | |

Aprobación del módulo: ≥ 60 %.

## Capstone (Demo Day)

| Criterio | Peso | Evidencia esperada |
|---|---|---|
| Orquestación A2A (supervisor + 3 subagentes) | 20 % | Trazas de delegación correctas |
| Precisión del informe ejecutivo | 25 % | Cifras coinciden con SQL; sin alucinaciones |
| Referencias auditables | 15 % | Cada afirmación cita artículo/tabla/consulta |
| Rerank y política (3 artículos clave, ¿exceso permitido?) | 10 % | |
| Riesgo de mora (modelo ML) + validación visual (Tableau) | 10 % | |
| Gobernanza y evaluación (Faithfulness, DLP, trazas) | 10 % | |
| Presentación y respuesta a preguntas | 10 % | |

**Pregunta oficial de prueba:** "Analiza por qué la división Norte excedió su presupuesto operacional en Q3 y cuál es el riesgo de impago proyectado."
Añadir 2 preguntas sorpresa del instructor (otra división/trimestre) para detectar respuestas memorizadas.
