# Lab Módulo 5 – Pipeline CI/CD con gate de Faithfulness

## Objetivo
Pipeline que evalúa la **Faithfulness** de un agente RAG con Reranking **antes** de autorizar el despliegue en Agent Engine.

## Requisitos
1. Conjunto de evaluación versionado (`data/casos_gasto.json` + 4 casos propios, incluyendo uno sin respuesta en el corpus).
2. Métricas: Faithfulness, Answer Relevance, Context Recall. En cloud, repetir con Agent Platform Evals (antes Vertex AI Evaluation) y comparar con la versión léxica.
3. Métricas A2A: tasa de éxito de delegación y precisión de ruta.
4. Trazas A2A visibles en Cloud Trace; registros de auditoría en Cloud Logging con PII enmascarada.
5. `cloudbuild.yaml`: tests → gate → build → deploy. Demostrar **un build bloqueado** (agente que alucina) y **uno autorizado**.
6. Service Account de mínimo privilegio (`ci/iam_least_privilege.md`) y propuesta de perímetro VPC-SC.

## Preguntas
¿Qué umbral eligen y por qué? ¿Qué pasa si la evaluación es no determinista? (Pista: repetir N veces, usar la mediana.)
