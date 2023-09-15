from llm_interactor import LLMInteractor
from chains import Chains
import pandas as pd

class SummaryGenerator:
    def __init__(self, kg_file):

        self.llmInteractor = LLMInteractor()
        self.chains = Chains(self.llmInteractor.get_chatGPT(), kg_file)

    def generate_summary(self, pathway_title):
        result = self.chains.sequential_chain({"query":pathway_title})
        return [result["kg_answer"], result["ft_answer"], result["ft_kg_answer"], result["output_text"]]

    def generate_batch_summary(self, query_list_file, out_dir, count=1):
        summary_list = []
        with open(query_list_file) as f:
            for query in f:
                for c in range(count):
                    summary_list.append(self.generate_summary(query))
        pd.DataFrame.from_records(summary_list, columns=["kg_answer", "ft_answer", "ft_kg_answer", "output_text"]). \
            to_csv('/'.join([out_dir, "generated_summaries.csv"]))

