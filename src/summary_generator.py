from llm_interactor import LLMInteractor
from chains import Chains
import pandas as pd
import asyncio
from langchain.callbacks import get_openai_callback

from utils import SequentialType

class SummaryGenerator:
    def __init__(self, kg_file):

        self.llmInteractor = LLMInteractor()
        self.chains = Chains(self.llmInteractor.get_chatGPT(), kg_file)
        self.static_gpt_chains = Chains(self.llmInteractor.get_chatGPT(temperature=0), kg_file)

    async def async_generate_summary(self, pathway_title, round, method, seqType, isStatic=False):
        #query = f"{pathway_title} when query is similar or equal to {pathway_title}"
        query = pathway_title
        with get_openai_callback() as cb:
            if isStatic:
                seqChain = self.static_gpt_chains.create_sequentialC(seqType)
            else:
                seqChain = self.chains.create_sequentialC(seqType)
        
            result = await seqChain.acall({"query":query})
        return pathway_title, result, cb.total_cost, round, method, seqType
    
    async def async_generate_base_summary(self, pathway_title, round, method):
        with get_openai_callback() as cb:
            res = await self.static_gpt_chains.async_call_base(pathway_title)
        return pathway_title, res["text"], cb.total_cost, round, method, 0
    
    async def concur_generate_batch_summary(self, query_list_file, out_dir, count=2):
        summary_list = []
        with open(query_list_file) as f:
            for query in f:
                tasks = []
                query = query.strip()
                tasks.append(self.async_generate_base_summary(query, 0, "gpt4-static"))
                tasks.append(self.async_generate_summary(query, 0, "static", SequentialType.BASE, isStatic=True))
                tasks.append(self.async_generate_summary(query, 0, "static", SequentialType.KG_FOCUS, isStatic=True))
                tasks.append(self.async_generate_summary(query, 0, "static", SequentialType.KG_FOCUS_LIMITED_TOKEN, isStatic=True))
                # for c in range(count):
                #     tasks.append(self.async_generate_summary(query, c, "dynamic", SequentialType.BASE))
                #     tasks.append(self.async_generate_summary(query, c, "dynamic", SequentialType.KG_FOCUS))
                #     tasks.append(self.async_generate_summary(query, c, "dynamic", SequentialType.KG_FOCUS_LIMITED_TOKEN))
                outputs = await asyncio.gather(*tasks)

                ## seqType is of type SequentialType
                for query, result, duration, round, method, seqType in outputs:
                    if method == "gpt4-static":
                        summary_list.append([round, duration, query, method, result])
                    else:
                        summary_list.append([round, duration, query, "_".join(["kg_answer",method,str(seqType)]), result["kg_answer"]])
                        summary_list.append([round, duration, query, "_".join(["ft_answer",method,str(seqType)]), result["ft_answer"]])
                        summary_list.append([round, duration, query, "_".join(["ft_kg_answer",method,str(seqType)]), result["ft_kg_answer"]])
                        summary_list.append([round, duration, query, "_".join(["ft_kg_ref_answer",method,str(seqType)]), result["output_text"]])

        # for query in f:
        #     query, result, duration, round, method, seqType = self.async_generate_base_summary(query, 0, "gpt4-static")
        #     summary_list.append([round, duration, query, method, result])

        pd.DataFrame.from_records(summary_list, columns=["trial", "duration", "query", "method", "summary"]). \
            to_csv('/'.join([out_dir, "generated_summaries.csv"]), index=None)

