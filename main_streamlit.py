import streamlit as st
import uuid
from rag_utils.prompt import SYSTEM_PROMPT
from rag_utils.setup import logger
from core.Agent_setup import agent
from langchain_core.messages import AIMessage
# ---------- Page config ----------
st.set_page_config(
    page_title="UpgradeVIP Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------- Session state ----------
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "system_sent" not in st.session_state:
    st.session_state.system_sent = False
if "chat" not in st.session_state:
    st.session_state.chat = [
("assistant", 
         "Good day. Welcome to UpgradeVIP – where seamless luxury travel is our standard.\n"
         "I'm here to ensure every detail of your journey is impeccably arranged.\n\n How may I be of service today?\n\n"
         "**Airport VIP Services** – Fast-track security, lounge access, and meet & greet  \n"
         "**Airport Transfer Services** – Chauffeur-driven transfers tailored to your schedule\n\n"
         "What may I arrange to ensure a seamless journey?"
        )]

# ---------- Header ----------
st.markdown("""
<div class="main-header">
  <h1>UpgradeVIP Chatbot</h1>
  <p>Your premium concierge for Airport VIP and Transfers.</p>
</div>
""", unsafe_allow_html=True)
st.write("")

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("#### Session")
    st.code(st.session_state.session_id)
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("New chat"):
            st.session_state.chat = [
                ("assistant", 
         "Good day. Welcome to UpgradeVIP – where seamless luxury travel is our standard.\n"
         "I'm here to ensure every detail of your journey is impeccably arranged.\n\n How may I be of service today?\n\n"
         "**Airport VIP Services** – Fast-track security, lounge access, and meet & greet  \n"
         "**Airport Transfer Services** – Chauffeur-driven transfers tailored to your schedule\n\n"
         "What may I arrange to ensure a seamless journey?"
        )
            ]
            st.session_state.system_sent = False
            st.session_state.session_id = str(uuid.uuid4())
            st.rerun()
    with col_b:
        transcript = "\n".join(
            [("You: " if r == "user" else "Assistant: ") + c for r, c in st.session_state.chat]
        )
        st.download_button("Download", transcript.encode("utf-8"), file_name="upgradevip_chat.txt")

    st.markdown("---")
    st.markdown("#### Tips")
    st.info("""
**Customer Assistance:**  
Ask anything about UpgradeVIP – services, contact info, airport list, or general questions.
- Note: Chatbot will not answer out of scope questions i.e capital of france etc

**Booking Flow:**  
1. Tell the bot which service you want: **airport VIP** or **transfer**.  
2. Provide your **flight number** (e.g. LY001) and **date** (MM/DD/YYYY).  
3. Choose **Arrival/Departure**(choose departure)
4. then select your **class** (Economy/Business/First).  
5. Enter **passenger** and **luggage count** (range 1-10).  
6. Pick your **preferred currency**.  
7. Select a service card by entering card no. or title. 
8. enter prefer time 
9. enter msg for steward 
10. give email.  
11. For multi-service, the bot will ask for other service you want to book.
12 Yes or no 
- if no
    - then invoice will given by bot confirm it
    - email will be send to you
- if yes
    - then repeat from step 1            
*Tip: For airport list, just ask “Show airports list”.*
""")
# ---------- Helpers ----------
from typing import Any, Dict, List, Tuple

def extract_text_from_ai(content: Any) -> str:
    """Best-effort extraction of text from agent outputs."""
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, AIMessage):
        return content.content or ""
    if isinstance(content, dict):
        # common keys across agents/chains
        for k in ("output", "answer", "final", "content", "text"):
            v = content.get(k)
            if isinstance(v, str) and v.strip():
                return v
        # sometimes the last message is in messages
        msgs = content.get("messages")
        if isinstance(msgs, list) and msgs:
            last = msgs[-1]
            if isinstance(last, AIMessage):
                return last.content or ""
            if isinstance(last, dict):
                return str(last.get("content", ""))
        return str(content)
    return str(content)

def md_with_linebreaks(text: str) -> str:
    # Normalize Windows CRLF and turn single newlines into Markdown line breaks
    return text.replace("\r\n", "\n").replace("\n", "  \n")

def _build_chat_history_for_agent() -> List[Dict[str, str]]:
    """
    Convert st.session_state.chat (list of tuples) into the format most agents/tools expect.
    """
    history: List[Dict[str, str]] = []
    for role, content in (st.session_state.chat or []):
        if role in ("user", "assistant"):
            history.append({"role": role, "content": str(content)})
    return history

def call_agent(user_text: str) -> str:
    # IMPORTANT: provide query + chat_history so Schema validation passes
    payload = {
        "query": user_text,
        "chat_history": _build_chat_history_for_agent(),
        "messages": [{"role": "user", "content": user_text}],
    }

    logger.info(f"📥 Agent payload keys: {list(payload.keys())}")

    try:
        result = agent.invoke(
            payload,
            config={"configurable": {"thread_id": st.session_state.session_id}},
        )
        return extract_text_from_ai(result)
    except Exception as e:
        logger.exception("❌ Agent invocation failed")
        return "Sorry, I am encountering some issues. Please try again later."
    # ---------- Chat history display ----------
with st.container():
    for role, content in st.session_state.chat:
        avatar = "🧑" if role == "user" else "🤖"
        with st.chat_message(role, avatar=avatar):
            if role == "assistant":
                st.markdown(md_with_linebreaks(str(content)))
            else:
                st.write(content)



# Add pending_reply to session state (put this after your other session state initializations)
if "pending_reply" not in st.session_state:
    st.session_state.pending_reply = None


# ---------- Input ----------
prompt = st.chat_input("Type your message and press Enter...")
if prompt:
    # Add user message to chat
    st.session_state.chat.append(("user", prompt))
    
    # Display user message immediately
    with st.chat_message("user", avatar="🧑"):
        st.write(prompt)
    
    # Show assistant typing with spinner
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Typing..."):
            reply = call_agent(prompt)
        st.markdown(md_with_linebreaks(reply))


    # Add assistant reply to chat
    st.session_state.chat.append(("assistant", reply))
