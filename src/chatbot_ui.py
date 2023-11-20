import chainlit as cl ### https://docs.chainlit.io/overview
from langchain import PromptTemplate, OpenAI, LLMChain
from answer_generator import AnswerGenerator
from langchain.schema import StrOutputParser
from langchain.schema.runnable import Runnable
from langchain.schema.runnable.config import RunnableConfig
#from langchain.callbacks import StreamlitCallbackHandler
#import streamlit as st



@cl.on_chat_start
async def on_chat_start():
    answer_generator = AnswerGenerator(kg_file=f"data/kg/reactome2langChainGraph2023.gml")
    cl.user_session.set("answer_generator", answer_generator)

@cl.on_message
async def on_message(message : cl.Message):
    print(message)
    chain = cl.user_session.get("answer_generator")  ## type: AnswerGenerator --> ConversationalRetrievalChain
    cb = cl.AsyncLangchainCallbackHandler()
    res = await chain.async_generate_answer(message, cb=[cb])
    print(res)
    answer = res["ft_kg_answer"]
    source_documents = res["source_documents"]  # type: List[Document]

    text_elements = []  # type: List[cl.Text]

    if source_documents:
        for source_idx, source_doc in enumerate(source_documents):
            source_name = f"source_{source_idx}"
            # Create the text element referenced in the message
            text_elements.append(
                cl.Text(content=source_doc.page_content, name=source_name)
            )
        source_names = [text_el.name for text_el in text_elements]

        if source_names:
            answer += f"\nSources: {', '.join(source_names)}"
        else:
            answer += "\nNo sources found"

    await cl.Message(content=answer, elements=text_elements).send()

### todo: how to call as one of the options to the main project?
# @cl.langchain_factory(use_async=True)
# def factory(self):
#     prompt = PromptTemplate(template=self.template, input_variables=["question"])
#     llm_chain = LLMChain(prompt=prompt, llm=OpenAI(temperature=0), verbose=True)

#     return llm_chain
