import asyncio
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
from tools.curriculum_tool import curriculumaccess

load_dotenv()


async def main():
    print("Testing curriculumaccess tool...\n")

    print("--- SDE / Beginner ---")
    result1 = await curriculumaccess.func(role="SDE", level="beginner")
    print(result1)

    print("\n--- Data Analyst / Intermediate ---")
    result2 = await curriculumaccess.func(role="Data Analyst", level="intermediate")
    print(result2)

    print("\n--- ML Engineer / Advanced ---")
    result3 = await curriculumaccess.func(role="ML Engineer", level="advanced")
    print(result3)

if __name__ == "__main__":
    asyncio.run(main())