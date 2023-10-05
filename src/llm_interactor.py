import os
import openai
from dotenv import load_dotenv, find_dotenv
from langchain.chat_models import ChatOpenAI


class LLMInteractor:
    def __init__(self):
        # Initialize the GPT4 API
        _ = load_dotenv(find_dotenv()) # read local .env file
        openai.api_key  = os.environ['OPENAI_API_KEY']
        openai.organization = os.environ['OPENAI_ORGANIZATION']

    def get_chatGPT(self, model_name="gpt-4", temperature=0.1):
        llm = ChatOpenAI(model_name=model_name, temperature=temperature, openai_api_key=openai.api_key)
        return llm
    
    def get_static_chatGPT(self, model_name="gpt-4", temperature=0):
        llm = ChatOpenAI(model_name=model_name, temperature=temperature, openai_api_key=openai.api_key)
        return llm