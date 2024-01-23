import os
import re
import time

from utils import SequentialType, AsyncGraphQAChain, AsyncSelfQueryRetriever

import pinecone

from langchain.chains import LLMChain,GraphQAChain,RetrievalQA, TransformChain, SequentialChain
from langchain.indexes.graph import NetworkxEntityGraph

from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS, Pinecone

from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain.chains.query_constructor.base import AttributeInfo

from langchain.embeddings import HuggingFaceEmbeddings

from langchain.evaluation import load_evaluator

import prompts

class Chains:
    def __init__(self, model, graph_file):
        self.embeddings = OpenAIEmbeddings() ## todo be replaced with suggested one from huggingface
        #self.embeddings = HuggingFaceEmbeddings(model_name = "sentence-transformers/multi-qa-mpnet-base-dot-v1", model_kwargs = {'device': 'cpu'}, encode_kwargs = {'normalize_embeddings': False})

        pinecone.init(api_key=os.environ["PINECONE_API_KEY"], environment=os.environ["PINECONE_ENV"])
        ### Use existing index
        self.vectorstore = Pinecone.from_existing_index("pathway-summation", self.embeddings)
        self.model = model
        self.graph_file = graph_file

        self.sequential_chain = self.create_sequentialC()

    def create_sequentialC(self, type=SequentialType.BASE):
        gc = self.create_graphC(self.graph_file)
        citing_chain = self.create_citationC()

        if type in [SequentialType.BASE,SequentialType.KG_FOCUS,SequentialType.KG_FOCUS_LIMITED_TOKEN]:
            qa = self.create_ftC()
            combine_chain = self.create_mergeC(type)
            sequential_chain = SequentialChain(chains=[gc, qa, combine_chain, citing_chain], 
                                               input_variables=["query"], 
                                               output_variables=["ft_answer", "kg_answer", "source_documents", "ft_kg_answer", "output_text"])    
        elif type in [SequentialType.KG_EXPANDER, SequentialType.KG_EXPANDER_LIMITED_TOKEN]:
            qa = self.create_ftC()
            combine_chain = self.create_kg_expanderC()
            sequential_chain = SequentialChain(chains=[gc, qa, combine_chain, citing_chain], 
                                               input_variables=["query"], 
                                               output_variables=["ft_answer", "kg_answer", "source_documents", "ft_kg_answer", "output_text"])    
        return sequential_chain


    def create_graphC(self, graph_file):
        graph = NetworkxEntityGraph.from_gml(graph_file)
        gc = AsyncGraphQAChain.from_llm(self.model, 
                           graph=graph, 
                           verbose=True, 
                           template=prompts.kg_prompt, 
                           input_key="query", 
                           output_key="kg_answer")
        return gc
        

    def create_ftC(self):
        metadata_field_info=[
            AttributeInfo(
                name="query",
                description="The title of the pathway", 
                type="string or list[string]")]
        
        document_content_description = "Reactome-level summation of a pathway"

        retriever = AsyncSelfQueryRetriever.from_llm(self.model, self.vectorstore, 
                                                document_content_description, 
                                                metadata_field_info, 
                                                verbose=True)
        qa = RetrievalQA.from_chain_type(llm=self.model, 
                                 retriever=retriever, 
                                 return_source_documents = True, 
                                 chain_type_kwargs={"prompt": prompts.qa_prompt},
                                 output_key="ft_answer",
                                 verbose=True)
        return qa

    def create_citationC(self):
        citing_chain = TransformChain(
            input_variables=["ft_answer", "kg_answer", "ft_kg_answer", "source_documents"], output_variables=["output_text"], 
            transform=transform_func
        )
        return citing_chain


    def create_mergeC(self, type=SequentialType.BASE):
        if type == SequentialType.BASE:
            combine_chain = LLMChain(llm=self.model,
                            prompt=prompts.combine_prompt,
                            output_key="ft_kg_answer")
        elif type == SequentialType.KG_FOCUS:
            combine_chain = LLMChain(llm=self.model,
                         prompt=prompts.combine_with_focus_on_kg_prompt,
                         output_key="ft_kg_answer")
        elif type == SequentialType.KG_FOCUS_LIMITED_TOKEN:
            combine_chain = LLMChain(llm=self.model,
                         prompt=prompts.combine_with_focus_on_kg_limited_token_prompt,
                         output_key="ft_kg_answer")
        else:
            print(f"Error: Unexpected Type for combining_chain: {type}")
            exit(1)
        return combine_chain
                           
    def create_kg_expanderC(self, type=SequentialType.KG_EXPANDER):
        if type == SequentialType.KG_EXPANDER:
            combine_chain = LLMChain(llm=self.model,
                         prompt=prompts.combine_with_focus_on_kg_prompt,
                         output_key="ft_kg_answer")
        return combine_chain

    def call_base(self, query):
        return self.model(prompts.simple_chat_prompt.format_messages(question=query))

    async def async_call_base(self, query):
        baseChain = LLMChain(llm=self.model, prompt=prompts.simple_chat_prompt)
        res = await baseChain.acall({"question":query})
        #print(res)
        #res = await self.model.agenerate(prompts.simple_chat_prompt.format_messages(question=query))
        return res

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

