from llm_interactor import LLMInteractor
from chains import Chains
import pandas as pd
import time

class SummaryGenerator:
    def __init__(self, kg_file):

        self.llmInteractor = LLMInteractor()
        self.chains = Chains(self.llmInteractor.get_chatGPT(), kg_file)

    def generate_summary(self, pathway_title):
        query = f"{pathway_title} when query is similar or equal to {pathway_title}"
        result = self.chains.sequential_chain({"query":query})
        return result
    
    def generate_base_summary(self, pathway_title):
        res = self.chains.call_base(pathway_title)
        return res.content
    
    def generate_batch_summary(self, query_list_file, out_dir, count=3):
        summary_list = []
        with open(query_list_file) as f:
            for query in f:
                for c in range(count):
                    start = time.time()
                    res = self.generate_summary(query)
                    end = time.time()
                    duration = round(end-start)
                    summary_list.append([c, duration, query, "kg_answer", res["kg_answer"]])
                    summary_list.append([c, duration, query, "ft_answer", res["ft_answer"]])
                    summary_list.append([c, duration, query, "ft_kg_answer", res["ft_kg_answer"]])
                    summary_list.append([c, duration, query, "output_text", res["output_text"]])

                start = time.time()
                res = self.generate_base_summary(query)
                summary_list.append([0, round(time.time()-start), query, "gpt-4", res])
        pd.DataFrame.from_records(summary_list, columns=["trial", "duration", "query", "method", "summary"]). \
            to_csv('/'.join([out_dir, "generated_summaries.csv"]), index=None)

