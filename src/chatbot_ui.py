import chainlit as cl ### https://docs.chainlit.io/overview
from langchain import PromptTemplate, OpenAI, LLMChain
#from langchain.callbacks import StreamlitCallbackHandler
#import streamlit as st



class ChatbotUI:

    def __init__(self):
        self.template = """Question: {question}

        Answer: Let's think step by step."""

    def get_user_query(self):
        return input("Please enter your query: ")

    def display_answer(self, answer):
        print(answer)

    ### todo: how to call as one of the options to the main project?
    @cl.langchain_factory(use_async=True)
    def factory(self):
        prompt = PromptTemplate(template=self.template, input_variables=["question"])
        llm_chain = LLMChain(prompt=prompt, llm=OpenAI(temperature=0), verbose=True)

        return llm_chain
