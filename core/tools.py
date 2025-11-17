from langchain.tools import tool
from .flight_details_funtions import (airports_tool,
                                      flight_details_tool,
                                      format_flight_choice_tool)
from .services import (
    transport_services_tool,
    format_transport_services_tool,
    vip_services_tool,
    format_vip_services_tool
)
from .invoice import (
    single_generate_invoice_tool,
    generate_combined_invoice_tool,
    send_email_tool)


from rag_utils.vector_store import checking_vector_store
from rag_utils.retriever import get_context
from rag_utils.setup import logger


#============================================================================================================
#RAG Tools
@tool
def rag_query_tool(query,chat_history):
    """Retrieve relevant documents from vector store and generate a response using LLM."""
    from .Agent_setup import get_gemini_response
    logger.info(f"🚪 Inside RAG query tool function")
    
    print("🚀 RAG pipeline started...")
    print("Type 'exit' to quit.\n")
    chromaDB = checking_vector_store()
    context = get_context(query,chromaDB)
    answer = get_gemini_response(query,context,chat_history)
    
    logger.info(f"🤖----> Assistant by rag is: {answer}\n")
    return answer



#==============================================================================================================================================
#tools list
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
    generate_combined_invoice_tool
]
