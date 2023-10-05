from langchain import PromptTemplate
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain.prompts.chat import SystemMessagePromptTemplate, HumanMessagePromptTemplate


general_system_template = """ 
Answer as an expert curator of biomedical data. 
Follow the instructions below in your answer: 
    1. If you don't know the answer, just say that you don't know, don't try to make up an answer.
    2. Make sure the answer is as concise as possible
    3. Make sure you include all important and relevant bindings, and reactions involved 
    (such as regulations, activations, and inhibitions)
    4. Make sure you include all important and relevant complexes, biocomponents, genes, molecules, proteins, RNAs, and DNAs involved
    5. Don't mention or make references to specific diagrams, figures, tables, schematic references, 
    or other forms of visuals that cannot be represented in your output.
"""


simple_chat_prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(general_system_template + """
                                               Cite your references in a scientific format """),
    HumanMessagePromptTemplate.from_template("""Answer the following question:
                                             {question}""")    
])

qa_prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(general_system_template),
    HumanMessagePromptTemplate.from_template("""Answer the following question using the given context: 
                                             {question} 
                                             
                                             context:
                                             {context}

                                             """)
])



kg_prompt = PromptTemplate(input_variables = ["question", "context"], 
                          template=general_system_template+"""
                          Use the following knowledge triplets to answer the query at the end. 
                          
                                                    
                          {context}
                          
                          Query: {question}

                          """)

combine_prompt = PromptTemplate(input_variables =["ft_answer", "kg_answer"], 
                                template=general_system_template+""" 
                                Provide an answer that includes all important, accurate details in the given answers below. 

                                KG_answer:{kg_answer}
                                
                                ft_answer:{ft_answer}
                                
                                """)

combine_noconcat_prompt = PromptTemplate(input_variables =["ft_answer", "kg_answer"], 
                                template=general_system_template+""" 
                                Provide an answer that includes all important, accurate details in the given answers below. 
                                There are two answers: KG_answer and ft_answer.
                                Do not simply concatenate the answers.

                                KG_answer:{kg_answer}
                                
                                ft_answer:{ft_answer}
                                
                                """)


combine_with_focus_on_kg_prompt = PromptTemplate(input_variables =["ft_answer", "kg_answer"], 
                                template=general_system_template+""" 
                                Provide an answer that includes all important, accurate details in the given answers below. 
                                There are two answers: KG_answer and ft_answer.
                                Do not simply concatenate the two answers. 
                                Make sure your main focus is on KG_answer. Include all important facts from KG_answer.
                                Use the KG_answer as base and extend it to the details provided in ft_answer.
                                
                                
                                KG_answer:{kg_answer}
                                
                                ft_answer:{ft_answer}
                                
                                """)

combine_with_focus_on_kg_limited_token_prompt = PromptTemplate(input_variables =["ft_answer", "kg_answer"], 
                                template=general_system_template+""" 
                                Provide an answer that includes all important, accurate details in the given answers below. 
                                Your answer should be limited to less than 300 tokens.
                                There are two answers: KG_answer and ft_answer.
                                Do not simply concatenate the two answers. 
                                Make sure your main focus is on KG_answer. Include all important facts from KG_answer.
                                Use the KG_answer as base and extend it to the details provided in ft_answer.
                                
                                
                                KG_answer:{kg_answer}
                                
                                ft_answer:{ft_answer}
                                
                                """)
