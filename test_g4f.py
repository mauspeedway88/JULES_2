import asyncio
from g4f.client import AsyncClient

async def main():
    client = AsyncClient()
    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Di hola"}]
        )
        print("Success:", response.choices[0].message.content)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    asyncio.run(main())
