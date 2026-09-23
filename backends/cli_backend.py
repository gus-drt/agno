import asyncio
import re
from typing import AsyncGenerator, Dict, Any
from config import CLI_COMMAND
from backends.base import BaseAgentBackend
from memory_manager import memory_manager

class CliAgentBackend(BaseAgentBackend):
    def __init__(self):
        self.process = None
        # Expressão regular para limpar códigos de cor ANSI que "sujam" a saída do terminal
        self.ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        self.first_turn = True

    async def start(self):
        pass
        
    async def stop(self):
        pass

    async def chat_stream(self, prompt: str) -> AsyncGenerator[Dict[str, Any], None]:
        memory_manager.log_interaction("user", prompt)

        if self.first_turn:
            persona = (
                "INSTRUÇÃO DE SISTEMA: Você é 'Agno', um agente de IA poderoso e amigável rodando no computador do usuário. "
                "Sua interface é o aplicativo Telegram (texto e emojis). Você tem todos os poderes do Antigravity CLI, mas "
                "aja sempre sob a persona de Agno. Responda de forma clara, usando Markdown leve e emojis amigáveis. "
                "Nunca diga que é o Antigravity, diga que é o Agno. Sempre responda em pt-BR.\n\n"
                "Mensagem do Usuário: "
            )
            prompt_to_send = persona + prompt
            self.first_turn = False
        else:
            prompt_to_send = prompt

        try:
            # Spawns a new process for each turn, continuing the last conversation
            # Using exec avoids shell escaping issues on Windows
            process = await asyncio.create_subprocess_exec(
                CLI_COMMAND, "-c", "-p", prompt_to_send,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
        except Exception as e:
            yield {"type": "error", "content": f"Falha ao iniciar CLI: {str(e)}"}
            return
            
        async def consume_stderr():
            while True:
                line = await process.stderr.readline()
                if not line:
                    break
                print("CLI STDERR:", line.decode("utf-8", errors="replace").strip())
                
        asyncio.create_task(consume_stderr())
        
        # Lê a resposta enquanto houver dados até o EOF
        while True:
            try:
                chunk = await process.stdout.read(1024)
                if not chunk:
                    break
                
                text = chunk.decode("utf-8", errors="replace")
                clean_text = self.ansi_escape.sub('', text)
                
                # Trata mensagens de negação de política de segurança da CLI
                if "Denied by policy" in clean_text or "denied by pre-tool hook" in clean_text:
                    yield {"type": "tool_call", "content": "⚠️ [CLI] Ação restrita por política interna"}
                    clean_text = re.sub(r'Denied by policy "[^"]*"\.\s*\("denied by pre-tool hook:[^)]*"\)\s*', '', clean_text)
                    clean_text = re.sub(r'\(denied by pre-tool hook:[^)]*\)\s*', '', clean_text)
                    clean_text = re.sub(r'Denied by policy "[^"]*"\.\s*', '', clean_text)

                # Heurística para detectar uso de ferramentas no output puro
                if "Running" in clean_text or "tool" in clean_text.lower():
                    yield {"type": "tool_call", "content": "🛠️ [CLI] Operação detectada..."}
                
                if clean_text:
                    yield {"type": "token", "content": clean_text}
                    
            except Exception as e:
                yield {"type": "error", "content": f"CLI Read Error: {str(e)}"}
                break
                
        await process.wait()
