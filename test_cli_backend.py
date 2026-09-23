import asyncio
import re
from config import CLI_COMMAND

async def test_cli():
    process = await asyncio.create_subprocess_shell(
        CLI_COMMAND,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    print("Processo iniciado.")
    prompt = "o que voce pode fazer"
    process.stdin.write((prompt + "\n").encode("utf-8"))
    await process.stdin.drain()
    process.stdin.close()
    await process.stdin.wait_closed()
    print("Prompt enviado e stdin fechado.")
    
    first_chunk = True
    while True:
        try:
            timeout_val = 45.0 if first_chunk else 2.5
            print(f"Aguardando leitura com timeout de {timeout_val}s...")
            chunk = await asyncio.wait_for(process.stdout.read(1024), timeout=timeout_val)
            if not chunk:
                print("Fim do stream.")
                break
            first_chunk = False
            
            text = chunk.decode("utf-8", errors="replace")
            print("Recebido:", repr(text))
            
        except asyncio.TimeoutError:
            print("Timeout!")
            break
        except Exception as e:
            print("Erro:", e)
            break

if __name__ == "__main__":
    asyncio.run(test_cli())
