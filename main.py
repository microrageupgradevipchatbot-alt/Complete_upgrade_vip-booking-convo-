from pydantic import BaseModel
from typing import Optional
from rag_utils.setup import logger
import uuid
from core.Agent_setup import agent
from rag_utils.prompt import FINAL_SYSTEM_PROMPT
from langchain_core.messages import AIMessage, SystemMessage
import asyncio

def main():
    print("🚀 UpgradeVIP Terminal Chat Started!")
    session_id = str(uuid.uuid4())
    system_message_sent = False

    while True:
        user_input = input("You: ").strip()
        logger.info("session_id: " + session_id)
        if user_input.lower() in ["exit", "quit"]:
            print("👋 Exiting. Goodbye!")
            break

        messages_to_send = []
        if not system_message_sent:
            messages_to_send.append({"role": "system", "content": FINAL_SYSTEM_PROMPT})
            system_message_sent = True

        messages_to_send.append({"role": "user", "content": user_input})

        try:
            result = agent.invoke(
                {
                    "messages": messages_to_send
                },
                config={
                    "configurable": {"thread_id": session_id},
                    "max_iterations": 5
                }
            )
            logger.info(f"response: {result}")
            messages = result.get("messages", [])
            bot_reply = None

            for m in reversed(messages):
                if isinstance(m, AIMessage):
                    bot_reply = getattr(m, "content", None)
                    break

            if isinstance(bot_reply, list) and len(bot_reply) > 0 and isinstance(bot_reply[0], dict):
                bot_reply = bot_reply[0].get("text", "")

            if not bot_reply:
                bot_reply = "Sorry, I am encountering some issues. Please try again later."

            print(f"Assistant: {bot_reply}")

        except Exception as e:
            logger.error(f"❌ Error: {e}")
            print("Assistant: Sorry, I am encountering some issues. Please try again later.")

if __name__ == "__main__":
    main()
    