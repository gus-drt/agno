import asyncio
from config import CLI_COMMAND

async def test_cli_print():
    prompt = "quem e voce e por onde estamos conversando?"
    process = await asyncio.create_subprocess_shell(
        f"{CLI_COMMAND} -p \"{prompt}\"",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    print("Processo iniciado.")
    
    while True:
        try:
            chunk = await asyncio.wait_for(process.stdout.read(1024), timeout=45.0)
            if not chunk:
                print("Fim do stream.")
                break
            
            text = chunk.decode("utf-8", errors="replace")
            print("Recebido:", repr(text))
            
        except asyncio.TimeoutError:
            print("Timeout!")
            break
        except Exception as e:
            print("Erro:", e)
            break
            
    await process.wait()

if __name__ == "__main__":
    asyncio.run(test_cli_print())
