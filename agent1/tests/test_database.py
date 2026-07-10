import asyncio
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
from tools.database_tool import database_interact

load_dotenv()


async def main():
    print("Testing database_interact tool...\n")

    print("--- Storing a resource ---")
    store_result = await database_interact.func(
        action="store",
        user_id="test_user_001",
        role="SDE",
        topic="Dynamic Programming",
        level="intermediate",
        content="Sample gathered content for testing purposes."
    )
    print(store_result)

    print("\n--- Retrieving resources for test_user_001 ---")
    retrieve_result = await database_interact.func(
        action="retrieve",
        user_id="test_user_001",
        role="SDE"
    )
    print(retrieve_result)

    print("\n--- Retrieving for a user with no data (should say 'No resources found') ---")
    empty_result = await database_interact.func(
        action="retrieve",
        user_id="nonexistent_user",
        role="SDE"
    )
    print(empty_result)

    print("\n--- Invalid action (should return clean error) ---")
    invalid_result = await database_interact.func(
        action="delete",
        user_id="test_user_001"
    )
    print(invalid_result)


if __name__ == "__main__":
    asyncio.run(main())