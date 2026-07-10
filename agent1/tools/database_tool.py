import aiosqlite
from crewai.tools import tool

DB_PATH = "techguide.db"


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS resources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                role TEXT,
                topic TEXT,
                level TEXT,
                content TEXT
            )
        """)
        await db.commit()


@tool("Database Interaction Tool")
async def database_interact(
    action: str,
    user_id: str,
    role: str = "",
    topic: str = "",
    level: str = "",
    content: str = ""
) -> str:
    """
    Stores or retrieves gathered preparation resources.
    action: 'store' or 'retrieve'
    """
    await init_db()

    try:
        async with aiosqlite.connect(DB_PATH) as db:
            if action == "store":
                await db.execute(
                    "INSERT INTO resources (user_id, role, topic, level, content) VALUES (?, ?, ?, ?, ?)",
                    (user_id, role, topic, level, content)
                )
                await db.commit()
                return "Resource stored successfully."

            elif action == "retrieve":
                cursor = await db.execute(
                    "SELECT topic, level, content FROM resources WHERE user_id=? AND role=?",
                    (user_id, role)
                )
                rows = await cursor.fetchall()
                if not rows:
                    return "No resources found."
                return "\n".join([f"[{r[1]}] {r[0]}: {r[2][:200]}..." for r in rows])

            return "Invalid action. Use 'store' or 'retrieve'."

    except Exception as e:
        return f"Database error: {str(e)}"