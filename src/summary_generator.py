from langchain.chains.summarize import load_summarize_chain
from langchain import PromptTemplate
from llm_interactor import LLMInteractor

class SummaryGenerator:
    def __init__(self):

        self.llmInteractor = LLMInteractor()
        self.summary_prompt_template = "As a Reactome Curator write a concise summary for the pathway ```{pathway_title}``` \
                based on the collection of papers texts delimited by triple backquotes. \
                ```{docs}``` \
                    Make sure the summary is citable using these list of papers. \
                    Use the metadata provided along with the papers \
                    to cite the papers where you paraphrased and interpreted the summary text from. "

    def generate_summary(self, pathway_title, papers):
        self.summary_prompt_template.format(pathway_title=pathway_title)
        summary_prompt = PromptTemplate(template=self.summary_prompt_template, input_variables=["docs"])
        self.summary_chain = load_summarize_chain(llm=self.llmInteractor.get_llm(), chain_type='map_reduce', 
                                    combine_prompt=summary_prompt,
                                    verbose=False)
        return self.summary_chain.run(papers)
        
