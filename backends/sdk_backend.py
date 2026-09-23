import asyncio
import os
from typing import AsyncGenerator, Dict, Any
from dotenv import load_dotenv
from google.antigravity import Agent, LocalAgentConfig, CapabilitiesConfig
from google.antigravity.hooks import policy
from memory_manager import memory_manager
from backends.base import BaseAgentBackend

class SdkAgentBackend(BaseAgentBackend):
    def __init__(self):
        self.config = None
        self.agent = None
        self._agent_context = None
        
    def _get_instructions(self):
        return (
            "Você é Agno, um agente de IA com acesso ao computador do usuário. "
            "Você está integrado ao sistema usando a Antigravity Python SDK, "
            "o que permite usar ferramentas de bash e sistema de arquivos. "
            "Sempre responda em português. A sua principal interface de comunicação "
            "com o usuário é o Telegram, onde respostas em texto e uso de ferramentas são transmitidas. "
            "Mantenha suas mensagens organizadas com tópicos limpos, emojis amigáveis e formatação legível para o Telegram. "
            "Para lembrar de contextos antigos, sinta-se livre para usar suas ferramentas de sistema "
            "para ler os arquivos JSON dentro da pasta 'logs/' deste projeto."
        )
    
    async def start(self):
        load_dotenv(override=True)
        gcp_project = os.getenv("GCP_PROJECT_ID")
        gcp_location = os.getenv("GCP_LOCATION", "us-central1")
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if gemini_api_key:
            gemini_api_key = gemini_api_key.strip('"\'')
            os.environ["GEMINI_API_KEY"] = gemini_api_key

        # Permite execução autônoma de ferramentas de terminal e arquivos
        policies = [policy.allow_all()]

        if gcp_project:
            self.config = LocalAgentConfig(
                vertex=True,
                project=gcp_project,
                location=gcp_location,
                system_instructions=self._get_instructions(),
                capabilities=CapabilitiesConfig(),
                policies=policies
            )
        else:
            self.config = LocalAgentConfig(
                api_key=gemini_api_key,
                system_instructions=self._get_instructions(),
                capabilities=CapabilitiesConfig(),
                policies=policies
            )
        
        self._agent_context = Agent(self.config)
        self.agent = await self._agent_context.__aenter__()

    async def stop(self):
        if self._agent_context:
            await self._agent_context.__aexit__(None, None, None)
            self._agent_context = None
            self.agent = None

    async def chat_stream(self, prompt: str) -> AsyncGenerator[Dict[str, Any], None]:
        if not self.agent:
            yield {"type": "error", "content": "O agente não foi inicializado."}
            return

        memory_manager.log_interaction("user", prompt)

        try:
            response = await self.agent.chat(prompt)

            async def consume_tokens():
                async for token in response:
                    yield {"type": "token", "content": token}
            
            async def consume_tool_calls():
                async for call in response.tool_calls:
                    yield {"type": "tool_call", "content": f"🛠️ Executando ferramenta: {call.name}..."}

            streams = [
                consume_tokens().__aiter__(),
                consume_tool_calls().__aiter__()
            ]
            
            pending = {asyncio.create_task(s.__anext__()): s for s in streams}
            
            while pending:
                done, _ = await asyncio.wait(pending.keys(), return_when=asyncio.FIRST_COMPLETED)
                for task in done:
                    stream = pending.pop(task)
                    try:
                        item = task.result()
                        yield item
                        pending[asyncio.create_task(stream.__anext__())] = stream
                    except StopAsyncIteration:
                        pass
        except Exception as e:
            yield {"type": "error", "content": f"SDK Error: {str(e)}"}
