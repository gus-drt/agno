from typing import AsyncGenerator, Dict, Any
from config import get_current_mode
from backends.sdk_backend import SdkAgentBackend
from backends.cli_backend import CliAgentBackend

class AgentRouter:
    def __init__(self):
        self.sdk_backend = SdkAgentBackend()
        self.cli_backend = CliAgentBackend()
        self.current_backend = None
        self._mode = get_current_mode()
        
    async def start(self):
        self._mode = get_current_mode()
        if self._mode == "sdk":
            self.current_backend = self.sdk_backend
        else:
            self.current_backend = self.cli_backend
            
        await self.current_backend.start()
        
    async def switch_mode(self, new_mode: str):
        if self.current_backend:
            await self.current_backend.stop()
            
        self._mode = new_mode
        if self._mode == "sdk":
            self.current_backend = self.sdk_backend
        else:
            self.current_backend = self.cli_backend
            
        await self.current_backend.start()

    async def chat_stream(self, prompt: str) -> AsyncGenerator[Dict[str, Any], None]:
        if not self.current_backend:
            yield {"type": "error", "content": "Nenhum backend inicializado."}
            return
            
        async for item in self.current_backend.chat_stream(prompt):
            yield item

agent_runner = AgentRouter()
