from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from rag_utils.setup import logger
import uuid
from core.Agent_setup import agent
from rag_utils.prompt import SYSTEM_PROMPT_FLIGHT_DETAILS_AND_RAG,FINAL_SYSTEM_PROMPT
class MessageRequest(BaseModel):
    message: str
    session: Optional[str] = None

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)
logger.info("🚀 FastAPI app initialized.")
#==========================root endpoint to check if server is running==========================

@app.get("/")
def root():
    return {"okk": True}

#========================================  MAIN  ================================================

from langchain_core.messages import AIMessage, SystemMessage

@app.post("/message")
async def message_endpoint(req: MessageRequest):
    try:
        user_input = req.message.strip()
        session_id = req.session.strip() if req.session and req.session.strip() else str(uuid.uuid4())
        
        logger.info(f"💬 User({session_id}): {user_input}")


        # Get current state to check for existing system message
        current_state = await agent.aget_state({"configurable": {"thread_id": session_id}})
        current_messages = current_state.values.get("messages", []) if current_state else []
        
        # Check if system message already exists
        has_system_message = any(isinstance(msg, SystemMessage) for msg in current_messages)
        
        messages_to_send = []
        if not has_system_message:
            messages_to_send.append({"role": "system", "content": FINAL_SYSTEM_PROMPT})
        
        
        messages_to_send.append({"role": "user", "content": user_input})
        logger.info(f"📥 Messages sending to llm: {messages_to_send}")
        
        result = await agent.ainvoke(
            {
            "messages": messages_to_send},
        config={
            "configurable": {"thread_id": session_id},
            "max_iterations": 5  # or another safe number
        }
        ) 
        logger.info(f"🔄 Agent response: {result}")
        messages = result.get("messages", [])
        bot_reply = None

        for m in reversed(messages):
            if isinstance(m, AIMessage):
                bot_reply = getattr(m, "content", None)
                break

        # If bot_reply is a list of dicts, extract the text
        if isinstance(bot_reply, list) and len(bot_reply) > 0 and isinstance(bot_reply[0], dict):
            bot_reply = bot_reply[0].get("text", "")

        print("✅Bot Reply:", bot_reply)
        return {"bot_reply": bot_reply, "session": session_id}
    
    except Exception as e:
        logger.error(f"❌ Error in message_endpoint: {e}")
        return {
            "bot_reply": "Sorry, I am encountering some issues. Please try again later.",
            "session": req.session or str(uuid.uuid4())
        }
    
    
    
    # bot_reply = None
    
    # for m in reversed(messages):
    #     if isinstance(m, AIMessage):
    #         bot_reply = getattr(m, "content", None)
    #         break
    # print("✅Bot Reply:", bot_reply)
    # return {"bot_reply": bot_reply, "session": session_id}

"""
   for m in reversed(messages):
        if hasattr(m, "name") and m.name == "rag_query_tool" and hasattr(m, "content"):
            bot_reply = m.content
            break
        if not bot_reply:
            for m in reversed(messages):
                if isinstance(m, AIMessage):
                    bot_reply = getattr(m, "content", None)
                    break
    
    return {"bot_reply": bot_reply, "session": session_id}

"""
