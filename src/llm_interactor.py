import os
import openai
from dotenv import load_dotenv, find_dotenv
from langchain.llms import OpenAI


class LLMInteractor:
    def __init__(self):
        # Initialize the GPT4 API
        _ = load_dotenv(find_dotenv()) # read local .env file

        openai.api_key  = os.environ['OPENAI_API_KEY']
        openai.organization = os.environ['OPENAI_ORGANIZATION']
        self.llm = OpenAI(model_name="gpt-4", temperature=0.1, openai_api_key=openai.api_key)

    def get_llm(self):
        return self.llm