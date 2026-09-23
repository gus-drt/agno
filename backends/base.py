from typing import AsyncGenerator, Dict, Any

class BaseAgentBackend:
    async def start(self):
        """Inicializa o agente (inicia contexto ou o subprocesso)."""
        pass
        
    async def stop(self):
        """Finaliza o agente de forma limpa."""
        pass
        
    async def chat_stream(self, prompt: str) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Envia uma mensagem ao agente e retorna um gerador de eventos.
        Eventos possíveis:
        {"type": "token", "content": "..."}
        {"type": "tool_call", "content": "..."}
        {"type": "error", "content": "..."}
        """
        yield {"type": "error", "content": "Not implemented"}
