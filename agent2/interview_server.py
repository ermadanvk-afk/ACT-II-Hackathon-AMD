import os
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from dotenv import load_dotenv
from openai import AsyncOpenAI
try:
    from interview_memory import InterviewMemory
except ImportError:
    from agent2.interview_memory import InterviewMemory

# Load environment variables
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)

app = FastAPI(title="Prep Agent - Voice Interview Server")

# Initialize the OpenAI client pointing to Fireworks API
# We use AsyncOpenAI for non-blocking streaming
client = AsyncOpenAI(
    api_key=os.getenv("FIREWORKS_API_KEY"),
    base_url=os.getenv("FIREWORKS_BASE_URL")
)

# System prompt for the interviewer
SYSTEM_PROMPT = """You are an elite technical interviewer. You are conducting a live, verbal mock interview with a candidate via video call.
Rules:
1. Keep your responses concise, conversational, and natural. Do not output markdown, bullet points, or long paragraphs, as your text will be converted to speech.
2. Ask one question at a time.
3. Wait for the user to answer. If they struggle, give a tiny hint. If they are right, move to a harder question.
4. Begin by introducing yourself briefly and asking the first technical question."""

@app.websocket("/ws/interview")
async def interview_endpoint(websocket: WebSocket, role: str = "Software Engineer", topic: str = "General"):
    await websocket.accept()
    
    # 1. Dynamically fetch the context from the knowledge base using the tool we already built!
    try:
        from agent2.tools import KnowledgeBaseSearchTool
        
        # Map the role to the correct directory (e.g. Data Analyst -> DA)
        role_map = {"Data Analyst": "DA", "Software Engineer": "SWE", "Machine Learning Engineer": "ML"}
        kb_prefix = role_map.get(role, "SWE")
        kb_dirs = [os.path.join(os.path.dirname(__file__), f"knowledge_base_{kb_prefix}")]
        
        kb_tool = KnowledgeBaseSearchTool()
        context = kb_tool._run(kb_tags=[topic], kb_dirs=kb_dirs)
    except Exception as e:
        context = f"Error fetching context: {str(e)}"
        
    # 2. Inject the fetched context directly into the System Prompt
    dynamic_prompt = SYSTEM_PROMPT + f"\n\nHere is the exact theory and curriculum you must test the candidate on for '{topic}':\n{context}"
    
    # Initialize a fresh memory with the context-aware prompt
    memory = InterviewMemory(system_prompt=dynamic_prompt)
    
    try:
        # Wait for the client to say they are ready
        data = await websocket.receive_text()
        
        # Trigger the first AI greeting by simulating a "hello" from the user behind the scenes
        # Or just let the LLM generate the first message based on the system prompt
        response_stream = await client.chat.completions.create(
            model="accounts/fireworks/models/minimax-m3",
            messages=memory.get_messages() + [{"role": "user", "content": "Hello, I am ready for the interview."}],
            stream=True,
            temperature=0.7,
            max_tokens=150
        )
        
        ai_full_response = ""
        async for chunk in response_stream:
            if chunk.choices[0].delta.content is not None:
                text_chunk = chunk.choices[0].delta.content
                ai_full_response += text_chunk
                await websocket.send_text(text_chunk)
        
        # Save the AI's response to memory
        memory.add_user_message("Hello, I am ready for the interview.")
        memory.add_ai_message(ai_full_response)
        
        # Signal the end of the AI's turn so the frontend knows it can start listening again
        await websocket.send_text("[END_OF_TURN]")

        # Main conversation loop
        while True:
            # 1. Receive transcribed text from the user (Frontend handles STT)
            user_text = await websocket.receive_text()
            print(f"User: {user_text}")
            
            memory.add_user_message(user_text)
            
            # 2. Stream the LLM response
            response_stream = await client.chat.completions.create(
                model="accounts/fireworks/models/minimax-m3",
                messages=memory.get_messages(),
                stream=True,
                temperature=0.7,
                max_tokens=200
            )
            
            ai_full_response = ""
            async for chunk in response_stream:
                if chunk.choices[0].delta.content is not None:
                    text_chunk = chunk.choices[0].delta.content
                    ai_full_response += text_chunk
                    # Send text chunks to frontend for immediate Text-to-Speech
                    await websocket.send_text(text_chunk)
            
            memory.add_ai_message(ai_full_response)
            
            # Signal the end of the AI's turn
            await websocket.send_text("[END_OF_TURN]")
            
    except WebSocketDisconnect:
        print("Client disconnected.")
    except Exception as e:
        print(f"Error: {e}")
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    # Run the server on port 8000 (default) or environment variable
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
