import asyncio
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
from tools.web_access_tool import webaccess

load_dotenv()


async def main():
    print("Testing webaccess tool...\n")
    result = await webaccess.func(role="SDE", topic="Dynamic Programming", level="intermediate")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())