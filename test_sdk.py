import asyncio
import os
from dotenv import load_dotenv
from google.antigravity import Agent, LocalAgentConfig, CapabilitiesConfig
from google.antigravity.hooks import policy

async def main():
    load_dotenv(override=True)
    gcp_project = os.getenv("GCP_PROJECT_ID")
    gcp_location = os.getenv("GCP_LOCATION", "us-central1")
    gemini_api_key = os.getenv("GEMINI_API_KEY")

    policies = [policy.allow_all()]
    config = LocalAgentConfig(
        api_key=gemini_api_key,
        system_instructions="Teste",
        capabilities=CapabilitiesConfig(),
        policies=policies
    )
    
    async with Agent(config) as agent:
        print("Enviando prompt...")
        response = await agent.chat("o que vc pode fazer?")
        print("Response object:", response)
        
        # Testando iterators
        print("Iterando tokens:")
        try:
            async for token in response:
                print("Token:", repr(token))
        except Exception as e:
            print("Erro ao iterar tokens:", e)
            
        print("Iterando tool_calls:")
        try:
            async for call in response.tool_calls:
                print("Tool call:", call)
        except Exception as e:
            print("Erro ao iterar tool_calls:", e)

if __name__ == "__main__":
    asyncio.run(main())
