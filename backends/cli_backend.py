import asyncio
import re
import json
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
                "Sua interface é o aplicativo Telegram (texto e emojis). Você tem todos os poderes do sistema. "
                "IMPORTANTÍSSIMO: Antes de invocar qualquer ferramenta destrutiva ou executar comandos de terminal perigosos "
                "(ex: criar/modificar arquivos reais, rodar comandos globais), você DEVE explicar ao usuário o que fará "
                "e PERGUNTAR se ele autoriza. Somente execute a ferramenta no turno seguinte, após ele dizer 'sim'. "
                "Aja sempre sob a persona de Agno. Responda de forma clara, usando Markdown leve e emojis amigáveis. "
                "Sempre responda em pt-BR.\n\n"
                "Mensagem do Usuário: "
            )
            prompt_to_send = persona + prompt
            self.first_turn = False
        else:
            prompt_to_send = prompt

        try:
            # Spawns a new process for each turn, continuing the last conversation
            # Utiliza stream-json para capturar as ferramentas corretamente e desativa as travas nativas de permissão 
            # (pois a restrição agora será via prompt no chat)
            process = await asyncio.create_subprocess_exec(
                CLI_COMMAND, "-c", "-p", prompt_to_send,
                "--output-format", "stream-json", "--dangerously-skip-permissions",
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
                line = await process.stdout.readline()
                if not line:
                    break
                
                decoded_line = line.decode("utf-8", errors="replace").strip()
                if not decoded_line:
                    continue
                    
                try:
                    data = json.loads(decoded_line)
                    
                    if data.get("event") == "step_update":
                        step = data.get("step_update", {})
                        
                        # Capturar uso de ferramentas
                        if step.get("state") == "ACTIVE" and step.get("step_type") == "tool":
                            tool_name = step.get("tool_name", "ferramenta_desconhecida")
                            yield {"type": "tool_call", "content": f"🛠️ Executando {tool_name}..."}
                            
                        # Capturar tokens de texto
                        if step.get("step_type") == "agent_response" and "text_delta" in step:
                            yield {"type": "token", "content": step["text_delta"]}
                            
                except json.JSONDecodeError:
                    # Fallback para texto plano se não for JSON
                    clean_text = self.ansi_escape.sub('', decoded_line)
                    if clean_text:
                        yield {"type": "token", "content": clean_text + "\n"}
                    
            except Exception as e:
                yield {"type": "error", "content": f"CLI Read Error: {str(e)}"}
                break
                
        await process.wait()
