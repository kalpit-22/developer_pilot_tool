import asyncio
from core.orchestrator import Orchestrator


async def main(request: str):
    orchestrator = Orchestrator(provider="deepseek")
    await orchestrator.run(request)


if __name__ == "__main__":
    print("=" * 40)
    print("  DevPilot - AI Code Generator")
    print("=" * 40)
    request = input("\nWhat would you like to build? > ").strip()
    
    if not request:
        print("No request provided. Exiting.")
    else:
        asyncio.run(main(request))