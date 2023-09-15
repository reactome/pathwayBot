from langchain import PromptTemplate
from langchain.prompts import ChatPromptTemplate
from langchain.prompts.chat import SystemMessagePromptTemplate, HumanMessagePromptTemplate

qa_prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template("""
                                              Follow the instructions below in your answer: 
                                              1. If you don't know the answer, just say that you don't know, don't try to make up an answer.
                                              2. The length of the answer must be under 200 tokens
                                              """),
    HumanMessagePromptTemplate.from_template("""Answer the following question using the given context: 
                                             {question} 
                                             
                                             context:
                                             {context}

                                             """)
])



kg_prompt = PromptTemplate(input_variables = ["question", "context"], 
                          template="""Answer as a professor of biology, 
                          making sure you mention all reactions involved, thinking logically, 
                          and providing detail and background knowledge.
                          Use the following knowledge triplets to answer the query at the end. 
                          If you don't know the answer, just say that you don't know, don't try to make up an answer.
                          Don't mention or make references to specific diagrams, figures, tables, schematic references, 
                          or other forms of visuals that cannot be represented in your output.
                          
                          {context}
                          
                          Query: {question}

                          """)

combine_prompt = PromptTemplate(input_variables =["ft_answer", "kg_answer"], 
                                template="""Answer as an expert curator of biomedical data. 
                                Provide an answer that includes all important, accurate details in the given answers below. 
                                ft_answer:{ft_answer}
                                
                                KG_answer:{kg_answer}
                                
                                """)
