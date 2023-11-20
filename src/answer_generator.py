from llm_interactor import LLMInteractor
from chains import Chains
import pandas as pd
import asyncio
from langchain.callbacks import get_openai_callback

from utils import SequentialType

class AnswerGenerator:
    def __init__(self, kg_file):

        self.llmInteractor = LLMInteractor()
        ## seqType: SequentialType
        self.seqChain = Chains(self.llmInteractor.get_chatGPT(streaming=True), kg_file).create_sequentialC(SequentialType.KG_FOCUS_LIMITED_TOKEN)

    async def async_generate_answer(self, query, cb):
        #query = f"{pathway_title} when query is similar or equal to {pathway_title}"
        result = await self.seqChain.acall(query, cb)
        return result ##, cb[0].total_cost