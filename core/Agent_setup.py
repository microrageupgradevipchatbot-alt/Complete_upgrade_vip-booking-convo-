from rag_utils.setup import logger
from .tools import tools
from rag_utils.prompt import build_prompt,build_prompt_v3
import os
#====================================langgraph agent setup=========================================
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent
#==================================== Gemini Embeddings and LLM setup ========================================
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if GOOGLE_API_KEY:
    logger.info("GOOGLE_API_KEY loaded successfully.")
else:
    logger.info("GOOGLE_API_KEY not found. Please set it in your environment or .env file.")

def get_gemini_embeddings():
    #api_key = os.getenv("GOOGLE_API_KEY")
    embeddings = GoogleGenerativeAIEmbeddings(
        model="gemini-embedding-001",
        google_api_key=GOOGLE_API_KEY
    )
    return embeddings
def get_gemini_llm():
    #api_key = os.getenv("GOOGLE_API_KEY")
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=GOOGLE_API_KEY,
        temperature=0.7
    )
    return llm
def get_gemini_response(query,context,chat_history):
    #api_key = os.getenv("GOOGLE_API_KEY")
    prompt = build_prompt_v3(query, context,chat_history)
    llm = get_gemini_llm()
    return llm.invoke(prompt).content

#==================================== Create LangGraph Agent =========================================
llm=get_gemini_llm()
memory = InMemorySaver()

agent = create_react_agent(
    llm,
    tools=tools,
    checkpointer=memory,  # save convo in RAM
  #  pre_model_hook=trim_messages,  # run trimming before each model call     
)