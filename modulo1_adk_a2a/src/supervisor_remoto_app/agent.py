"""Paquete para `adk web`: expone el supervisor que delega al especialista por A2A (puerto 8001).
Requiere el servidor corriendo: uvicorn finanzas_agents.a2a_server:a2a_app --port 8001
"""
from finanzas_agents.a2a_server import supervisor_remoto

root_agent = supervisor_remoto
