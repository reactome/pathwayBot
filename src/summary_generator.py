from llm_interactor import LLMInteractor
from chains import Chains

class SummaryGenerator:
    def __init__(self):

        self.llmInteractor = LLMInteractor()
        self.chains = Chains(self.llmInteractor.get_chatGPT())

    def generate_summary(self, pathway_title):
        result = self.chains.sequential_chain({"query":pathway_title})
        return list(result["kg_answer"], result["ft_answer"], result["output_text"])

    def mass_generator(self, query_list, count):
        summary_list = []
        for query in query_list:
            for c in range(count):
                summary_list.append(self.generate_summary(query))
