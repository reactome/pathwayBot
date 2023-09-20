import os
import re
import time

import pinecone

from langchain.chains import LLMChain,GraphQAChain,RetrievalQA, TransformChain, SequentialChain
from langchain.indexes.graph import NetworkxEntityGraph

from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS, Pinecone

from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain.chains.query_constructor.base import AttributeInfo

from langchain.evaluation import load_evaluator

import prompts

class Chains:
    def __init__(self, model, graph_file):
        self.embeddings = OpenAIEmbeddings() ## todo be replaced with suggested one from huggingface
        pinecone.init(api_key=os.environ["PINECONE_API_KEY"], environment=os.environ["PINECONE_ENV"])
        ### Use existing index
        self.vectorstore = Pinecone.from_existing_index("pathway-summation", self.embeddings)
        self.model = model
        self.create_ftC()
        self.create_graphC(graph_file)
        self.create_citationC()
        self.create_mergeC()


        self.sequential_chain = SequentialChain(chains=[self.qa, self.gc, self.combine_chain, self.citing_chain], 
                                         input_variables=["query"], 
                                         output_variables=["ft_answer", "kg_answer", "source_documents", "ft_kg_answer", "output_text"])    

    def create_graphC(self, graph_file):
        graph = NetworkxEntityGraph.from_gml(graph_file)
        self.gc = GraphQAChain.from_llm(self.model, 
                           graph=graph, 
                           verbose=True, 
                           template=prompts.kg_prompt, 
                           input_key="query", 
                           output_key="kg_answer")
        

    def create_ftC(self):
        metadata_field_info=[
            AttributeInfo(
                name="query",
                description="The title of the pathway", 
                type="string or list[string]")]
        
        document_content_description = "Reactome-level summation of a pathway"

        retriever = SelfQueryRetriever.from_llm(self.model, self.vectorstore, 
                                                document_content_description, 
                                                metadata_field_info, 
                                                verbose=True)
        self.qa = RetrievalQA.from_chain_type(llm=self.model, 
                                 retriever=retriever, 
                                 return_source_documents = True, 
                                 chain_type_kwargs={"prompt": prompts.qa_prompt},
                                 output_key="ft_answer",
                                 verbose=True)

    def create_citationC(self):
        self.citing_chain = TransformChain(
            input_variables=["ft_answer", "kg_answer", "ft_kg_answer", "source_documents"], output_variables=["output_text"], 
            transform=transform_func
        )


    def create_mergeC(self):
        self.combine_chain = LLMChain(llm=self.model,
                         prompt=prompts.combine_prompt,
                         output_key="ft_kg_answer")
                           

    def call_base(self, query):
        return self.model(prompts.simple_chat_prompt.format_messages(question=query))


def transform_func(inputs: dict) -> dict:
    start = time.time()
    output = ""
    citations = []
    references = set()
    text = inputs["ft_kg_answer"]
    kg = inputs["kg_answer"]
    ft = inputs["ft_answer"]
    sources = inputs['source_documents']
    if len(sources) == 0:
        output = text
        output += "\n\n**All information was derived from KG**\n\n"
        return {"output_text": output}
    embeddings = OpenAIEmbeddings() ## todo be replaced with suggested one from huggingface
    db = FAISS.from_documents(sources, embeddings)
    # kgembed = FAISS.from_documents(kg, embeddings)
    # ftembed = FAISS.from_documents(ft, embeddings)
    #db.similarity_search_with_score(query, k=10)
    #similarity_search_by_vector
    #print(text)
    
    hf_evaluator = load_evaluator("pairwise_embedding_distance", embeddings=embeddings)
    for t in re.split('[!?.]+(?=$|\s)', text):
        if len(t.strip()) > 0:
            kgscore = hf_evaluator.evaluate_string_pairs(prediction=t, prediction_b=kg)
            ftscore = hf_evaluator.evaluate_string_pairs(prediction=t, prediction_b=ft)
            #print(kgscore['score'], ftscore['score'])
            if  kgscore['score'] - ftscore['score'] > 0.1:
                citations.append('kg')
            else:
                doc = db.similarity_search_with_score(t, k=2)
                report_both = False
                citation = doc[0][0].metadata['authoryear-comp']
                references.add(doc[0][0].metadata['citation'])
                if abs(doc[0][1] - doc[1][1]) < 0.1 and doc[1][0].metadata['authoryear-comp'] != doc[0][0].metadata['authoryear-comp']:
                    citation += ', ' + doc[1][0].metadata['authoryear-comp']
                    references.add(doc[1][0].metadata['citation'])
                citations.append(citation)
    cntr = 1
    for t in re.split('[!?.]+(?=$|\s)', text):
        if len(t.strip()) > 0:
            if cntr < len(citations) and citations[cntr] == citations[cntr-1]:
                output += t
            else:
                output += t + ' (' + citations[cntr-1] + ') ' + '.'
        cntr+=1
    output += "\n\n**References**\n\n"
    output += '\n\n'.join([r for r in references])
    end = time.time()
    print(end - start)
    return {"output_text": output}

