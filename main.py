from pydantic import BaseModel
from typing import Optional
from rag_utils.setup import logger
import uuid
from core.Agent_setup import agent
from langchain_core.messages import AIMessage, SystemMessage
import asyncio

import asyncio

async def main():
    print("UpgradeVIP Flight Bot (type 'exit' to quit)")
    session_id = str(uuid.uuid4())
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() == "exit":
            print("Goodbye!")
            break
        messages_to_send = [{"role": "user", "content": user_input}]
        logger.info(f"📥 Messages sending to llm: {messages_to_send}")

        try:
            result = await agent.ainvoke(
                {"messages": messages_to_send},
                config={
                    "configurable": {"thread_id": session_id},
                    "max_iterations": 5
                }
            )
            logger.info(f"🔄 Agent response: {result}")

            messages = result.get("messages", [])
            bot_reply = None
            for m in reversed(messages):
                if isinstance(m, AIMessage):
                    bot_reply = getattr(m, "content", None)
                    break
            logger.info(f"\n\n🤖 Bot({session_id}): {bot_reply}")
             # Fix: Extract text if bot_reply is a list of dicts
            if isinstance(bot_reply, list) and bot_reply and isinstance(bot_reply[0], dict) and "text" in bot_reply[0]:
                print(f"🤖 Bot: {bot_reply[0]['text']}")
            else:
                print(f"🤖 Bot: {bot_reply}")

        except Exception as e:
            logger.error(f"❌ Error during agent invocation: {e}")
            print("🤖 Bot: Sorry, something went wrong. Please try again later.")

if __name__ == "__main__":
    asyncio.run(main())
