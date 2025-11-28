import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import OpenAIEmbeddings

load_dotenv()

def get_embedding_model():
  model_type = os.getenv("MODEL_TYPE", "free")
  
  if model_type == "gemini":
    return GoogleGenerativeAIEmbeddings(model=os.getenv("GOOGLE_EMBEDDING_MODEL"))
  
  if model_type == "openai":
    return OpenAIEmbeddings(model=os.getenv("OPENAI_EMBEDDING_MODEL"))

  return HuggingFaceEmbeddings(
    model_name=os.getenv("FREE_EMBEDDING_MODEL")
  )
    