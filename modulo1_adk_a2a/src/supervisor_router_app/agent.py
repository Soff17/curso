"""Paquete para `adk web`: expone el supervisor que enruta por A2A a DOS especialistas remotos (reto 5.4).
Requiere los dos servidores corriendo:
  uvicorn finanzas_agents.a2a_server:a2a_app --port 8001
  uvicorn finanzas_agents.a2a_server:a2a_app_tesoreria --port 8002
"""
from finanzas_agents.a2a_server import supervisor_router

root_agent = supervisor_router
