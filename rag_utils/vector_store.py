from langchain_community.document_loaders import TextLoader,UnstructuredMarkdownLoader
import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from .setup import (DB_DIR,DOC_DIR)

from pathlib import Path

def load_documents(folder_path):
    documents = []
    
    # Check if folder exists and has files
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"⚠️ Documents folder does not exist: {folder_path}")
    
    files = os.listdir(folder_path)
    if not files:
        raise ValueError(f"⚠️ No files found in documents folder: {folder_path}")
    
    
    for filename in files:
        file_path = os.path.join(folder_path, filename)
        print(f"full filename {file_path}")

        if filename.endswith('.md'):
            loader = UnstructuredMarkdownLoader(file_path)
            print(f"loaded {filename}")
        elif filename.endswith('.txt'):
            loader = TextLoader(file_path)
            print(f"loaded {filename}")
        else:
            print(f"unsupported file type : {filename}")
            continue

        documents.extend(loader.load())
    
    return documents

def create_chunks(documents):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
        )
    docs = text_splitter.split_documents(documents)
    print(f"Created {len(docs)} chunks from {len(documents)} documents.")
    return docs
def create_chroma_db(text_chunks):
  '''Index Documents (store embeddings) in vector store'''
  from core.Agent_setup import get_gemini_embeddings
  embeddings = get_gemini_embeddings()
  collection_name = "upgrade_collection"
  print(f"✅Indexing {len(text_chunks)} chunks into Chroma vector store '{collection_name}'...")
  chromaDB =  Chroma.from_documents(
      collection_name=collection_name,
      documents=text_chunks,
      embedding=embeddings,
      persist_directory=DB_DIR
  )
  print("✅Chroma vector store created successfully.")
  return chromaDB

def load_vector_store():
    """Create the Chroma vector store if not present, else load it."""
    from core.Agent_setup import get_gemini_embeddings  # <-- move import here
    embeddings = get_gemini_embeddings()
    chromaDB = Chroma(
        collection_name="upgrade_collection",
        embedding_function=embeddings,
        persist_directory=DB_DIR
    )
    print("✅Chroma vector store loaded from disk.")

    return chromaDB
def create_vector_store():
    """Create the Chroma vector store if not present, else load it."""
  
    documents = load_documents(DOC_DIR)
    text_chunks = create_chunks(documents)
    chromaDB = create_chroma_db(text_chunks)

    return chromaDB

def checking_vector_store():
    '''Check if vector store exists, if not create it'''
    
    if (DB_DIR / "chroma.sqlite3").exists():
        print("✅ Existing vector store found. Loading it...")
        chromaDB = load_vector_store()
    else:
        print("🛑 No existing vector store found. Creating a new one...")
        chromaDB = create_vector_store()    

    return chromaDB



