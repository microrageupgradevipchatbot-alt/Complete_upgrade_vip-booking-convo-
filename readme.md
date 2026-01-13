# UpgradeVIP AI Chatbot

An AI-powered conversational assistant to book premium airport services:
- Airport VIP Services: Fast-track, lounge access, meet & greet
- Airport Transfer Services: Chauffeur-driven transfers

It supports real-time flight lookup, multi-service booking, RAG-powered FAQs, and automated invoicing + email.

---

## Highlights

- Conversational booking (no forms)
- Flight/vip/transfer/airport names endpoints integration
- Single or combined service booking (VIP + Transfer)
- RAG-powered answers for policies, services, offices, and contact info
- Automated invoice generation and email sending feature
- Chat history been saved in memory for context

---

## Tech Stack

- LLM + Orchestration
  - LangChain + LangGraph (ReAct agent)
  - Google Gemini (via langchain-google-genai)
- Backend
  - FastAPI ([API/endpoints.py](API/endpoints.py))
- Frontend
  - Streamlit chat UI ([main_streamlit.py](main_streamlit.py))
  - Optional React frontend (CORS enabled)
- RAG / Vector Store
  - ChromaDB ([DATA/DB/chroma.sqlite3](DATA/DB/chroma.sqlite3))
  - Doc source: [DATA/Docs/upgradevip_details.txt](DATA/Docs/upgradevip_details.txt)
  - Loader/split/chroma helpers: [rag_utils/vector_store.py](rag_utils/vector_store.py)
- Booking + Tools
  - Flight + Airports: [core/flight_details_funtions.py](core/flight_details_funtions.py)
  - Services (VIP/Transfer): [core/services.py](core/services.py)
  - Invoices + Email: [core/invoice.py](core/invoice.py)
  - Tool registry: [core/tools.py](core/tools.py)
  - Agent: [`core.Agent_setup.agent`](core/Agent_setup.py)
- Config + Logging
  - Env + paths + logger: [rag_utils/setup.py](rag_utils/setup.py)
- System prompt + flow spec
  - [rag_utils/prompt.py](rag_utils/prompt.py)
  - Project notes: [DATA/MISC/Project Details.md](DATA/MISC/Project Details.md), [DATA/MISC/Features.md](DATA/MISC/Features.md), [DATA/MISC/project_flow.md](DATA/MISC/project_flow.md)

---

## Project Structure

- Frontends
  - Streamlit app: [main_streamlit.py](main_streamlit.py)
  - FastAPI app: [API/endpoints.py](API/endpoints.py)
- Agent + Tools
  - Agent: [`core.Agent_setup.agent`](core/Agent_setup.py)
  - Tools entrypoint: [core/tools.py](core/tools.py)
  - Flight + airport tools: [`core.flight_details_funtions.flight_details_tool`](core/flight_details_funtions.py), [`core.flight_details_funtions.airports_tool`](core/flight_details_funtions.py), [`core.flight_details_funtions.format_flight_choice_tool`](core/flight_details_funtions.py)
  - VIP/Transfer tools: [`core.services.vip_services_tool`](core/services.py), [`core.services.transport_services_tool`](core/services.py), [`core.services.only_transfer_services_tool`](core/services.py), [`core.services.only_vip_services_tool`](core/services.py), [`core.services.format_transport_services_tool`](core/services.py), [`core.services.format_vip_services_tool`](core/services.py)
  - Invoice tools: [`core.invoice.single_generate_invoice_tool`](core/invoice.py), [`core.invoice.generate_combined_invoice_tool`](core/invoice.py), [`core.invoice.send_email_tool`](core/invoice.py)
- RAG
  - Vector store utilities: [`rag_utils.vector_store.load_documents`](rag_utils/vector_store.py), [`rag_utils.vector_store.create_chunks`](rag_utils/vector_store.py), [`rag_utils.vector_store.load_vector_store`](rag_utils/vector_store.py), [`rag_utils.vector_store.create_vector_store`](rag_utils/vector_store.py), [`rag_utils.vector_store.checking_vector_store`](rag_utils/vector_store.py)
  - Retriever: [`rag_utils.retriever.get_context`](rag_utils/retriever.py)
  - Prompts: [rag_utils/prompt.py](rag_utils/prompt.py)
- Data
  - DB: [DATA/DB/chroma.sqlite3](DATA/DB/chroma.sqlite3)
  - Docs: [DATA/Docs/upgradevip_details.txt](DATA/Docs/upgradevip_details.txt)

---

## Setup

1) Python
- Python 3.10+

2) Environment
- Create .env in project root with your keys and URLs (align with [core/config.py](core/config.py)):
  - Google API key for Gemini
  - UpgradeVIP API base URL
  - UpgradeVIP bearer token (API key)
  - SMTP creds if emailing invoices

3) Vector Store
- RAG directories auto-created by [`rag_utils.setup.setup_paths`](rag_utils/setup.py)
- Ensure [DATA/Docs/upgradevip_details.txt](DATA/Docs/upgradevip_details.txt) exists
- On first run, vector DB is created by [`rag_utils.vector_store.create_vector_store`](rag_utils/vector_store.py). Subsequent runs load existing DB via [`rag_utils.vector_store.load_vector_store`](rag_utils/vector_store.py)

---

## Features

- RAG-Powered FAQs
  - Retrieves from ChromaDB
  - Uses [`rag_utils.retriever.get_context`](rag_utils/retriever.py) and vector helpers in [rag_utils/vector_store.py](rag_utils/vector_store.py)
- Booking Flow (VIP/Transfer)
  - Orchestrated by agent with system rules in [rag_utils/prompt.py](rag_utils/prompt.py)
  - Flight lookup via [`core.flight_details_funtions.get_flight_details_from_api`](core/flight_details_funtions.py)
  - Airports list via [`core.flight_details_funtions.get_airports_from_api`](core/flight_details_funtions.py)
  - Services fetch/format:
    - VIP: [`core.services.get_vip_services`](core/services.py), [`core.services.format_vip_services_message`](core/services.py)
    - Transfer: [`core.services.get_transport_services`](core/services.py), [`core.services.format_transport_services_message`](core/services.py)
- Invoicing + Email
  - Single/combined invoice: [`core.invoice.single_generate_invoice_tool`](core/invoice.py), [`core.invoice.generate_combined_invoice_tool`](core/invoice.py)
  - Email dispatch: [`core.invoice.send_email_tool`](core/invoice.py)
- Logging
  - Central logger via [`rag_utils.setup.logger`](rag_utils/setup.py)

---


## Flows

1) FAQ (RAG)
 User -> Agent (RAG) -> Retriever -> LLM -> Answer

2) Booking (VIP or Transfer)
 User -> Agent -> flight_details_tool -> format_flight_choice_tool -> services_tool -> format_services_tool -> Selection -> invoice_tool -> send_email_tool

3) Services by Airport Name (cards from airport name)
 User -> Agent -> airports_tool -> agent matches the code  -> send code to the service endpoint -> call service tool -> call format cards tool -> present to user .

4) Airport names list
user-> agent call airport tool -> format tool ->get the output -> show the user.



tools = [
    airports_tool,

    flight_details_tool,
    format_flight_choice_tool,

    transport_services_tool,
    format_transport_services_tool,
    
    vip_services_tool,
    format_vip_services_tool,
    
    rag_query_tool,
    
    send_email_tool,
    
    single_generate_invoice_tool,
    generate_combined_invoice_tool,

    only_vip_services_tool,
    only_transfer_services_tool,
    airports_raw_tool,
]
